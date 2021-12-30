#!/bin/sh

apt update
apt install -y --no-install-recommends librtlsdr-dev
cd /system
pip install .[with_pymodes]
adsbcot -U tcp:tak:8087 -D tcp+raw:adsb:30002
