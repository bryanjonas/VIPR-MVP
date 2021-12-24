from python:3.6-slim-buster

RUN apt update && \
    apt install -y --no-install-recommends git

RUN pip3 install docker

COPY ./requirements.txt /

RUN pip3 install -r /requirements.txt

CMD "/bin/bash"