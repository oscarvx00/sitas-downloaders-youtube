import os
import time
import json

from . import azure_service_bus_manager as AzureServiceBusManager

AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE = os.environ['AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE']
AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE = os.environ['AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE']
AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE = os.environ['AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE']



def test_send_download_request_message():
    sb_client = AzureServiceBusManager.init()

    msg = AzureServiceBusManager.RabbitDownloadRequest(
        "testUserId",
        "testDownloadId",
        "testSongName",
        False,
        False,
        True,
        False
    )

    AzureServiceBusManager.send_download_request_message(
        sb_client,
        msg
    )


    receiver = sb_client.get_queue_receiver(queue_name=AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE, max_wait_time=3)
    with receiver:
        for msg in receiver:
            assert "testDownloadId" == AzureServiceBusManager.RabbitDownloadRequest.from_json(json.loads(str(msg))).downloadId


    receiver.close()

    sb_client.close()


def test_send_download_completed_message():
    sb_client = AzureServiceBusManager.init()

    msg = AzureServiceBusManager.RabbitDownloadCompleted(
        "downloadIdTest",
        "statusTest",
        "downloadNameTest"
    )

    AzureServiceBusManager.send_download_completed_message(
        sb_client,
        msg
    )


    receiver = sb_client.get_queue_receiver(queue_name=AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE, max_wait_time=3)
    with receiver:
        for msg in receiver:
            assert "downloadIdTest" == AzureServiceBusManager.RabbitDownloadCompleted.from_json(json.loads(str(msg))).downloadId


    receiver.close()

    sb_client.close()