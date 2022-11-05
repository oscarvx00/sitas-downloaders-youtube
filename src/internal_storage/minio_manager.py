from minio import Minio
import os

MINIO_INTERNAL_ENDPOINT = os.environ['MINIO_INTERNAL_ENDPOINT']
MINIO_INTERNAL_PORT = os.environ['MINIO_INTERNAL_PORT']
MINIO_INTERNAL_USER = os.environ['MINIO_INTERNAL_USER']
MINIO_INTERNAL_PASS = os.environ['MINIO_INTERNAL_PASS']
MINIO_INTERNAL_BUCKET = os.environ['MINIO_INTERNAL_BUCKET']



def init():
    minio_client = Minio(
        endpoint=f'{MINIO_INTERNAL_ENDPOINT}:{MINIO_INTERNAL_PORT}',
        access_key=MINIO_INTERNAL_USER,
        secret_key=MINIO_INTERNAL_PASS,
        secure=False
    )

    return minio_client


def save_in_internal_storage(minio_client, filepath: str, download_id : str):

    minio_client.fput_object(
        MINIO_INTERNAL_BUCKET,
        f'{download_id}.mp3',
        filepath
    )