FROM python:3.8-slim-buster
WORKDIR /sitas-dl-yt

RUN apt update
RUN apt install -y ffmpeg
RUN apt install -y ffprobe

COPY ./ ./
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "src/main.py" ]