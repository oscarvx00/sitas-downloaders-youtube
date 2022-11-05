import requests
import pika
from minio import Minio
import json
import random
import os


import queue_manager.rabbit_manager as RabbitManager
import youtube_manager.youtube_manager as YoutubeManager

OTHER_DOWNLOAD_MODULES = ["soundcloud", "spotify"]


rabbit_channel = RabbitManager.init()

print(YoutubeManager.search_song("martin garix pizza"))


def resend_download_request(download_request : RabbitManager.RabbitDownloadRequest):

    available_modules = []
    for module in OTHER_DOWNLOAD_MODULES:
        if download_request[module]:
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
    download_dir = "../download_folder/" + download_request.downloadId
    download_command = f'yt-dlp -f \'ba\' -x --audio-format mp3 -P {download_dir} {url}'
    print(download_command)
    os.system(download_command)
    print("Downloaded " + url)

    #Search for dong in download folder
    print(os.listdir(download_dir))


#Register callback, listen to msgs
rabbit_channel.basic_consume(RabbitManager.DOWNLOAD_REQUEST_YOUTUBE_QUEUE, auto_ack=True, on_message_callback=download_request_callback)
rabbit_channel.start_consuming()