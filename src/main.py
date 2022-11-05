import requests
import pika
from minio import Minio
import sys
import time


import queue_manager.rabbit_manager as RabbitManager


rabbit_channel = RabbitManager.init()
