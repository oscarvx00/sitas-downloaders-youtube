import pytest
import os
import shutil
from mock import patch, call

import youtube_downloader

#from queue_manager.rabbit_manager import RabbitDownloadRequest
from queue_manager.azure_service_bus_manager import RabbitDownloadRequest

def test_resend_download_request_no_modules():

    with patch.object( youtube_downloader.AzureServiceBusManager, 'send_download_completed_message') as send_download_completed_message_mock:
        
        #Prepare
        test_request = RabbitDownloadRequest(
            'test_userId',
            'test_downloadId',
            'testSongName',
            False,
            False,
            False,
            False
        )

        call_args_list = send_download_completed_message_mock.call_args_list

        #Test
        youtube_downloader.resend_download_request(test_request)

        #Assert
        for call in call_args_list:
            #print('args: {}'.format(write_call[0]))
            #print('kwargs: {}'.format(write_call[1]))
            args, kwargs = call
            assert args[0] == None
            assert args[1].status == 'Error'
            assert args[1].downloadId == test_request.downloadId



def test_resend_download_request_module_soundcloud():

    with patch.object( youtube_downloader.AzureServiceBusManager, 'send_download_request_message') as send_download_request_message:
        
        #Prepare
        test_request = RabbitDownloadRequest(
            'test_userId',
            'test_downloadId',
            'testSongName',
            False,
            True,
            True, #Soundcloud module
            False
        )

        call_args_list = send_download_request_message.call_args_list

        #Test
        youtube_downloader.resend_download_request(test_request)

        #Assert
        for call in call_args_list:
            #print('args: {}'.format(write_call[0]))
            #print('kwargs: {}'.format(write_call[1]))
            args, kwargs = call
            assert args[0] == None
            assert args[1].soundcloud == True
            assert args[1].youtube == False
            assert args[1].downloadId == test_request.downloadId



def test_get_song_name_ok():
    #Prepare
    #Create dir
    os.mkdir("downloads_dir/")
    os.mkdir("downloads_dir/test_download_id")
    #Create dummy file
    test_download_song_name = "song_file_name.mp3"
    f = open("downloads_dir/test_download_id/" + test_download_song_name, 'w')
    f.write("dummy text")
    f.close()
    
    #Test
    song_name_result = youtube_downloader.get_song_name("test_download_id")

    #Clean
    shutil.rmtree('downloads_dir/')

    #Assert
    assert song_name_result == test_download_song_name


    
def test_get_song_name_no_mp3_file():
    #Prepare
    #Create dirs
    os.mkdir("downloads_dir/")
    os.mkdir("downloads_dir/test_download_id")
    #Create dummy file not mp3
    test_dummy_file_name = "dummy.txt"
    f = open("downloads_dir/test_download_id/" + test_dummy_file_name, 'w')
    f.write("dummy text")
    f.close()

    #Test
    song_name_result = youtube_downloader.get_song_name("test_download_id")

    #Clean
    shutil.rmtree('downloads_dir/')

    #Assert
    assert song_name_result == None



def test_rename_song_file():
    #Prepare
    #Create dirs
    os.mkdir("downloads_dir/")
    os.mkdir("downloads_dir/test_download_id")
    #Create dummy file not mp3
    test_dummy_file_name = "dummy.mp3"
    f = open("downloads_dir/test_download_id/" + test_dummy_file_name, 'w')
    f.write("dummy text")
    f.close()

    #Test
    youtube_downloader.rename_song_file("dummy.mp3", "test_download_id")

    file_exists = os.path.isfile("downloads_dir/test_download_id/test_download_id")

    #Clean
    shutil.rmtree('downloads_dir/')

    #Assert
    assert file_exists
