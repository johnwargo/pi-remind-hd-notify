#!/usr/bin/python
"""*****************************************************************************************************************
    Pi Remind HD Notify
    Created April 4, 2020.
    By John M. Wargo (https://www.johnwargo.com)

    This application connects to a Google Calendar and determines whether there are any appointments in the next
    few minutes and flashes some LEDs if there are. The project uses a Raspberry Pi 2 device with a Pimoroni
    Unicorn HAT HD (a 16x16 matrix of bright, multi-colored LEDs) to display an obnoxious reminder every minute,
    changing color at 10 minutes (WHITE), 5 minutes (YELLOW) and 2 minutes (multi-color swirl).

    Coupled with the Remote Notify project, the server code sends appointment status to the remote notify device
    to make others aware of the user's status (busy, tentative, free).

    Google Calendar example code: https://developers.google.com/google-apps/calendar/quickstart/python
********************************************************************************************************************"""
# TODO: Add configurable option for ignoring tentative appointments
# TODO: Clean up imports (in each file)

# This project's imports (local modules)
from particle import *
from unicorn_hat import *
#  Other imports
import datetime
import math
import os
import socket
import sys
import time
import pytz
from dateutil import parser
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

HASH = '#'
HASHES = '#############################################'
PROJECT_URL = 'https://github.com/johnwargo/pi-remind-hd-notify'

# Event search scope (searches this many minutes in the future for events). Increase this value to get reminders
# earlier. The app displays WHITE lights from this limit up to FIRST_THRESHOLD
SEARCH_LIMIT = 10  # minutes
# Reminder thresholds
FIRST_THRESHOLD = 5  # minutes, WHITE lights before this
# RED for anything less than (and including) the second threshold
SECOND_THRESHOLD = 2  # minutes, YELLOW lights before this

# Reboot Options - Added this to enable users to reboot the pi after a certain number of failed retries.
# I noticed that on power loss, the Pi looses connection to the network and takes a reboot after the network
# comes back to fix it.
REBOOT_COUNTER_ENABLED = False
REBOOT_NUM_RETRIES = 10
reboot_counter = 0  # counter variable, tracks retry events.

# JMW Added 20170414 to fix an issue when there's an error connecting to the
# Google Calendar API. The app needs to track whether there's an existing
# error through the process. If there is, then when checking again for entries
# the app will leave the light red while checking. Setting it to green if
# successful.
has_error = False

# create a variable to track the current status of the remote notify device.
# make this a class property the app can check.
remote_notify_status = 0


def calendar_loop():
    # initialize the lastMinute variable to the current time to start
    last_minute = datetime.datetime.now().minute
    # on startup, just use the previous minute as lastMinute, that way the app
    # will check for appointments immediately on startup.
    if last_minute == 0:
        last_minute = 59
    else:
        last_minute -= 1
    # infinite loop to continuously check Google Calendar for future entries
    while 1:
        # get the current minute
        current_minute = datetime.datetime.now().minute
        # is it the same minute as the last time we checked?
        if current_minute != last_minute:
            # reset last_minute to the current_minute, of course
            last_minute = current_minute
            # we've moved a minute, so we have work to do
            # get the next calendar event (within the specified time limit [in minutes])
            next_event = get_next_event()
            # do we get an event?
            if next_event is not None:
                num_minutes = next_event['num_minutes']
                if num_minutes != 1:
                    print('Starts in {} minutes\n'.format(num_minutes))
                else:
                    print('Starts in 1.0 minute\n')
                # is the appointment between 10 and 5 minutes from now?
                if num_minutes >= FIRST_THRESHOLD:
                    # Flash the lights in WHITE
                    unicorn.flash_all(1, 0.25, WHITE)
                    # display the event summary
                    unicorn.display_text(next_event['summary'], WHITE)
                    # set the activity light to WHITE as an indicator
                    unicorn.set_activity_light(WHITE, False)
                # is the appointment less than 5 minutes but more than 2 minutes from now?
                elif num_minutes > SECOND_THRESHOLD:
                    # Flash the lights YELLOW
                    unicorn.flash_all(2, 0.25, YELLOW)
                    # display the event summary
                    unicorn.display_text(next_event['summary'], YELLOW)
                    # set the activity light to YELLOw as an indicator
                    unicorn.set_activity_light(YELLOW, False)
                else:
                    # hmmm, less than 2 minutes, almost time to start!
                    # swirl the lights. Longer every second closer to start time
                    unicorn.do_swirl(int((4 - num_minutes) * 50))
                    # display the event summary
                    unicorn.display_text(next_event['summary'], ORANGE)
                    # set the activity light to SUCCESS_COLOR (green by default)
                    unicorn.set_activity_light(ORANGE, False)
        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def main():
    # tell the user what we're doing...
    print('\n')
    print(HASHES)
    print(HASH, 'Pi Remind HD Notify                      ', HASH)
    print(HASH, 'By John M. Wargo (https://johnwargo.com) ', HASH)
    print(HASHES)
    print(PROJECT_URL)

    # Initialize the Particle Cloud object
    particle = ParticleCloud()
    if not particle.config_is_valid():
        print('Particle Cloud configuration invalid or missing')
        print('Please validate the contents of the config.py file before continuing')
        # then exit, nothing else we can do here
        sys.exit(0)

    if REBOOT_COUNTER_ENABLED:
        print('Reboot enabled ({} retries)'.format(REBOOT_NUM_RETRIES))

    print('Application initialized\n')

    # flash some random LEDs just for fun...
    unicorn.flash_random(5, 0.5)
    # blink all the LEDs GREEN to let the user know the hardware is working
    unicorn.flash_all(3, 0.10, GREEN)

    calendar_loop()


# Initialize the Unicorn HAT
unicorn = UnicornHAT()

if __name__ == '__main__':
    try:
        # do our stuff
        main()
    except KeyboardInterrupt:
        # turn off all of the LEDs
        unicorn.off()
        # tell the user we're exiting
        print('\nExiting application\n')
        # exit the application
        sys.exit(0)
