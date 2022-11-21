import json
import random
import os
import shutil
import time


#import queue_manager.rabbit_manager as RabbitManager
import youtube_manager.youtube_manager as YoutubeManager
import internal_storage.minio_manager as MinioManager
import queue_manager.azure_service_bus_manager as AzureServiceBusManager

OTHER_DOWNLOAD_MODULES = ["soundcloud", "spotify"]
DOWNLOAD_DIR = "downloads_dir/"


#global rabbit_channel
#rabbit_channel = None
global minio_client
minio_client = None
global sb_client
sb_client = None

def resend_download_request(download_request : AzureServiceBusManager.RabbitDownloadRequest):

    available_modules = []
    for module in OTHER_DOWNLOAD_MODULES:
        if getattr(download_request, module):
            available_modules.append(module)
    
    if len(available_modules) == 0:
        print("Request " + download_request.downloadId + " discarded, no modules enabled")
        AzureServiceBusManager.send_download_completed_message(sb_client, AzureServiceBusManager.RabbitDownloadCompleted(
            download_request.downloadId,
            status='Error',
            downloadName=''
        ))
    else:
        download_request.youtube = False
        AzureServiceBusManager.send_download_request_message(sb_client, download_request)


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



def download_request_callback(msg):

    print(msg)
    download_request_raw_json = json.loads(str(msg))
    download_request = AzureServiceBusManager.RabbitDownloadRequest.from_json(download_request_raw_json)

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
    download_command = f'yt-dlp -f \'ba\' -x --max-downloads 1 --audio-format mp3 -P {download_dir} -k {url}'.replace("&", "\&")
    print(download_command)
    os.system(download_command)
    print("Downloaded " + url)

    #Search for song in download folder
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

    AzureServiceBusManager.send_download_completed_message(
        sb_client,
        AzureServiceBusManager.RabbitDownloadCompleted(
            download_request.downloadId,
            'OK',
            song_name_winthout_extension
    ))

    shutil.rmtree(f'{DOWNLOAD_DIR}{download_request.downloadId}')

    print(f'Download {download_request.downloadId} completed, file uploaded')


def run():
    #global rabbit_channel
    #rabbit_channel = RabbitManager.init()
    global minio_client
    minio_client = MinioManager.init()
    global sb_client
    sb_client = AzureServiceBusManager.init()

    #Register callback, listen to msgs
    #rabbit_channel.basic_consume(AzureServiceBusManager.DOWNLOAD_REQUEST_YOUTUBE_QUEUE, auto_ack=True, on_message_callback=download_request_callback)
    #print('Listening to messages')
    #rabbit_channel.start_consuming()
    while True:
        receiver = sb_client.get_queue_receiver(queue_name=AzureServiceBusManager.AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE)
        with receiver:
            for msg in receiver:
                download_request_callback(msg)
                receiver.complete_message(msg)

        print('Listening loop')
        time.sleep(10)

