#!/bin/sh

apt update
apt install -y --no-install-recommends librtlsdr-dev
cd /system
/usr/local/bin/pip install .[with_pymodes] --use-feature=in-tree-build
adsbcot -U tcp:tak:8087 -D tcp+raw:adsb:30002