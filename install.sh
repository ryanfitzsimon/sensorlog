#!/usr/bin/sh

sudo pip install -r requirements.txt
sudo ln -fs $(pwd)/sensorlog.py /usr/local/bin/sensorlog
sudo cp 10-sensorlog.rules /etc/udev/rules.d
