from python:3.6-slim-buster

RUN pip3 install pymodes pycot pytak python-dateutil lxml

RUN apt update && \
    apt install -y --no-install-recommends git

RUN git clone https://github.com/ampledata/adsbcot.git && \
    cd adsbcot/ && \
    python setup.py install

CMD "/bin/bash"