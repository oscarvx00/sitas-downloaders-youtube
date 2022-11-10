import json
import random
import os
import shutil


import queue_manager.rabbit_manager as RabbitManager
import youtube_manager.youtube_manager as YoutubeManager
import internal_storage.minio_manager as MinioManager

OTHER_DOWNLOAD_MODULES = ["soundcloud", "spotify"]
DOWNLOAD_DIR = "downloads_dir/"


global rabbit_channel
rabbit_channel = None
global minio_client
minio_client = None

def resend_download_request(download_request : RabbitManager.RabbitDownloadRequest):

    available_modules = []
    for module in OTHER_DOWNLOAD_MODULES:
        if getattr(download_request, module):
            available_modules.append(module)
    
    if len(available_modules) == 0:
        print("Request " + download_request.downloadId + " discarded, no modules enabled")
        RabbitManager.send_download_completed_message(rabbit_channel, RabbitManager.RabbitDownloadCompleted(
            download_request.downloadId,
            status='Error',
            downloadName=''
        ))
    else:
        download_request.youtube = False
        selected_module = random.choice(available_modules)
        RabbitManager.send_download_request_message(rabbit_channel, download_request, selected_module)


def get_song_name(download_id: str):
    dir = f'{DOWNLOAD_DIR}{download_id}'
    filenames = next(os.walk(dir), (None, None, []))[2]
    filenames = [a for a in filenames if a.endswith('.mp3') ]
    if len(filenames) == 0:
        return None
    else:
        return filenames[0]

def rename_song_file(song_name : str, download_id: str):
    dir = f'{DOWNLOAD_DIR}{download_id}'
    filepath = f'{DOWNLOAD_DIR}{download_id}/{song_name}'
    os.rename(filepath, f'{dir}/{download_id}')



def download_request_callback(ch, method, properties, body):

    download_request_raw_json = json.loads(body)
    download_request = RabbitManager.RabbitDownloadRequest.from_json(download_request_raw_json)

    print("[+] Received: ", download_request)

    url = download_request.songName

    if not download_request.direct:
        video_id = YoutubeManager.search_song(url)
        if video_id == None:
            resend_download_request(download_request)
            return
        url = "https://www.youtube.com/watch?v=" + video_id    


    print("Downloading " + url)
    download_dir = DOWNLOAD_DIR + download_request.downloadId
    download_command = f'yt-dlp -f \'ba\' -x --audio-format mp3 -P {download_dir} -k {url}'
    print(download_command)
    os.system(download_command)
    print("Downloaded " + url)

    #Search for dong in download folder
    song_name = get_song_name(download_request.downloadId)
    print(song_name)
    if song_name == None:
        resend_download_request(download_request)
        return

    song_name_winthout_extension = song_name.split('.mp3')[0]
    
    
    rename_song_file(song_name, download_request.downloadId)

    #Upload song to minio
    MinioManager.save_in_internal_storage(
        minio_client,
        f'{DOWNLOAD_DIR}{download_request.downloadId}/{download_request.downloadId}',
        download_request.downloadId
    )

    RabbitManager.send_download_completed_message(
        rabbit_channel,
        RabbitManager.RabbitDownloadCompleted(
            download_request.downloadId,
            'OK',
            song_name_winthout_extension
    ))

    shutil.rmtree(f'{DOWNLOAD_DIR}{download_request.downloadId}')

    print(f'Download {download_request.downloadId} completed, file uploaded')


def run():
    global rabbit_channel
    rabbit_channel = RabbitManager.init()
    global minio_client
    minio_client = MinioManager.init()

    #Register callback, listen to msgs
    rabbit_channel.basic_consume(RabbitManager.DOWNLOAD_REQUEST_YOUTUBE_QUEUE, auto_ack=True, on_message_callback=download_request_callback)
    print('Listening to messages')
    rabbit_channel.start_consuming()


