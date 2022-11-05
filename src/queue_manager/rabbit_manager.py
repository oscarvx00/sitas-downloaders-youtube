import pika
import os
import json


DOWNLOAD_REQUEST_EXCHANGE = os.environ['DOWNLOAD_REQUEST_EXCHANGE']
DOWNLOAD_REQUEST_YOUTUBE_QUEUE = os.environ['DOWNLOAD_REQUEST_YOUTUBE_QUEUE']
DOWNLOAD_COMPLETED_EXCHANGE = os.environ['DOWNLOAD_COMPLETED_EXCHANGE']

RABBITMQ_ENDPOINT = os.environ['RABBITMQ_ENDPOINT']
RABBITMQ_VHOST = os.environ['RABBITMQ_VHOST']
RABBITMQ_USER = os.environ['RABBITMQ_USER']
RABBITMQ_PASS = os.environ['RABBITMQ_PASS']


class RabbitDownloadRequest:
    def __init__(self, userId, downloadId, songName, spotify, youtube, soundcloud, direct):
        self.userId = userId
        self.downloadId = downloadId
        self.songName = songName
        self.spotify = spotify
        self.youtube = youtube
        self.soundcloud = soundcloud
        self.direct = direct
    
    def from_json(json_dict):
        return RabbitDownloadRequest(
            json_dict['userId'],
            json_dict['downloadId'],
            json_dict['songName'],
            json_dict['spotify'],
            json_dict['youtube'],
            json_dict['soundcloud'],
            json_dict['direct']
        )
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class RabbitDownloadCompleted:
    def __init__(self, downloadId, status, downloadName):
        self.downloadId = downloadId
        self.status = status
        self.downloadName = downloadName
    
    def to_json(self):
        return json.dumps(self, default=lambda o:o.__dict__)


def init():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_ENDPOINT, virtual_host=RABBITMQ_VHOST, credentials=pika.PlainCredentials(username=RABBITMQ_USER, password=RABBITMQ_PASS))
    )
    
    rabbit_channel = connection.channel()

    #Declare download request excahnge
    rabbit_channel.exchange_declare(exchange=DOWNLOAD_REQUEST_EXCHANGE, exchange_type='direct', durable=False)

    #Declare youtube download request queue
    rabbit_channel.queue_declare(queue=DOWNLOAD_REQUEST_YOUTUBE_QUEUE, exclusive=False, durable=False)

    #Bind queue to exchange
    rabbit_channel.queue_bind(exchange=DOWNLOAD_REQUEST_EXCHANGE, queue=DOWNLOAD_REQUEST_YOUTUBE_QUEUE, routing_key='youtube')

    #Declare download complete exchange
    rabbit_channel.exchange_declare(exchange=DOWNLOAD_COMPLETED_EXCHANGE, exchange_type='fanout')

    return rabbit_channel



def send_download_request_message(rabbit_channel ,message : RabbitDownloadRequest, routing_key : str):
    rabbit_channel.basic_publish(
        exchange=DOWNLOAD_REQUEST_EXCHANGE,
        routing_key=routing_key,
        body=message.to_json()
    )


def send_download_completed_message(rabbit_channel, message : RabbitDownloadCompleted):
    rabbit_channel.basic_publish(
        exchange=DOWNLOAD_COMPLETED_EXCHANGE,
        body=message.to_json()
    )