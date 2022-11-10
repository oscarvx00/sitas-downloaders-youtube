FROM python:3.8-slim-buster
WORKDIR /sitas-dl-yt

COPY ./ ./
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "src/main.py" ]