import pytest
import os
import shutil
from mock import patch, call

import youtube_downloader

from queue_manager.rabbit_manager import RabbitDownloadRequest

#@patch.object( youtube_downloader.RabbitManager, 'send_download_completed_message')
def test_resend_download_request():
    #mocker.patch('youtube_downloader.RabbitManager')
    #mocker.patch('Module.rabbit_channel')

    
    with patch.object( youtube_downloader.RabbitManager, 'send_download_completed_message') as send_download_completed_message_mock:
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

        youtube_downloader.resend_download_request(test_request)

        expected_args = [None, test_request]
        
        for call in call_args_list:
            #print('args: {}'.format(write_call[0]))
            #print('kwargs: {}'.format(write_call[1]))
            args, kwargs = call
            assert args[0] == None
            assert args[1].status == 'Error'
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
