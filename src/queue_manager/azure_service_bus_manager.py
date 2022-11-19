from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os
import json

AZURE_SERVICE_BUS_CONNECTION_STRING = os.environ['AZURE_SERVICE_BUS_CONNECTION_STRING']
AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE = os.environ['AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE']
AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE = os.environ['AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE']
AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE = os.environ['AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE']




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

    def __str__(self):
        return f'DownloadRequest: [downloadId: {self.downloadId}, songName: {self.songName}, soundcloud: {self.soundcloud}]\n'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class RabbitDownloadCompleted:
    def __init__(self, downloadId, status, downloadName):
        self.downloadId = downloadId
        self.status = status
        self.downloadName = downloadName

    def from_json(json_dict):
        return RabbitDownloadCompleted(
            json_dict['downloadId'],
            json_dict['status'],
            json_dict['downloadName']
        )
    
    def to_json(self):
        return json.dumps(self, default=lambda o:o.__dict__)
    
    def __str__(self):
        return "DownloadCompleted: [downloadId: " + self.downloadId + " , downloadName: " + self.downloadName + "]\n"

    def __eq__(self, other):
        return self.to_json() == other.to_json()



def init():
    sb_client = ServiceBusClient.from_connection_string(conn_str=AZURE_SERVICE_BUS_CONNECTION_STRING)
    return sb_client


def send_download_request_message(sb_client ,message : RabbitDownloadRequest):

    message = ServiceBusMessage(message.to_json())
    sender = sb_client.get_queue_sender(queue_name=AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE)
    sender.send_messages(message)
    sender.close()


def send_download_completed_message(sb_client, message : RabbitDownloadCompleted):
    message = ServiceBusMessage(message.to_json())
    sender = sb_client.get_queue_sender(queue_name=AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE)
    sender.send_messages(message)
    sender.close()