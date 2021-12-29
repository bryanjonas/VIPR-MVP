FROM docker:dind

RUN apk update && apk add docker

# Install python/pip
ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache git python3 && ln -sf python3 /usr/bin/python

RUN python3 -m ensurepip

RUN pip3 install --no-cache --upgrade pip setuptools docker

COPY ./requirements.txt /

RUN pip3 install -r /requirements.txt