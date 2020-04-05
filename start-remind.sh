#!/bin/bash

# the python executable we're running
home_folder="/home/pi/pi-remind-hd"
start_file="./remind.py"

# change to the pi user's home folder, that way everything happens in the same folder
cd $home_folder

# get the file date from the file
fd=`date -d @$( stat -c %Y $start_file ) +"%Y-%m-%d %T"`
# tell the user what we're doing
echo "Starting Pi Remind (file date: $fd)"
# then launch the start file
python $start_file

# How To Autostart Apps In Rasbian LXDE Desktop
# http://www.raspberrypi-spy.co.uk/2014/05/how-to-autostart-apps-in-rasbian-lxde-desktop/
