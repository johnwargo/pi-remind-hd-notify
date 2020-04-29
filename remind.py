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
# TODO: Clean up imports

# This project's imports (local modules)
from calendar import *
from particle import *
import status as status
import unicorn_hat as unicorn

#  Other imports
import datetime
import logging
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
CONFIG_ERROR_STR = 'Please validate the contents of the config.json file before continuing'

# Event search scope (searches this many minutes in the future for events). Increase this value to get reminders
# earlier. The app displays WHITE lights from this limit up to FIRST_THRESHOLD
SEARCH_LIMIT = 10  # minutes
# Reminder thresholds
FIRST_THRESHOLD = 5  # minutes, WHITE lights before this
# RED for anything less than (and including) the second threshold
SECOND_THRESHOLD = 2  # minutes, YELLOW lights before this

# initialize the classes we'll use as globals
calendar = None
particle = None

# whether or not you have a remote notify device connected. Use the config file to override
use_remote_notify = False


def processing_loop():
    global particle

    # initialize the previous remote notify status
    previous_status = -1

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
            # next_event = calendar.get_next_event()
            next_event = calendar.get_status()
            # do we get an event?
            if next_event is not None:
                num_minutes = next_event['num_minutes']
                if num_minutes != 1:
                    logging.info('Starts in {} minutes\n'.format(num_minutes))
                else:
                    logging.info('Starts in 1.0 minute\n')
                # is the appointment between 10 and 5 minutes from now?
                if num_minutes >= FIRST_THRESHOLD:
                    # Flash the lights in WHITE
                    unicorn.flash_all(1, 0.25, unicorn.WHITE)
                    # display the event summary
                    unicorn.display_text(next_event['summary'], unicorn.WHITE)
                    # set the activity light to WHITE as an indicator
                    unicorn.set_activity_light(unicorn.WHITE, False)
                # is the appointment less than 5 minutes but more than 2 minutes from now?
                elif num_minutes > SECOND_THRESHOLD:
                    # Flash the lights YELLOW
                    unicorn.flash_all(2, 0.25, unicorn.YELLOW)
                    # display the event summary
                    unicorn.display_text(next_event['summary'], unicorn.YELLOW)
                    # set the activity light to YELLOw as an indicator
                    unicorn.set_activity_light(unicorn.YELLOW, False)
                else:
                    # hmmm, less than 2 minutes, almost time to start!
                    # swirl the lights. Longer every second closer to start time
                    unicorn.do_swirl(int((4 - num_minutes) * 50))
                    # display the event summary
                    unicorn.display_text(next_event['summary'], unicorn.ORANGE)
                    # set the activity light to SUCCESS_COLOR (green by default)
                    unicorn.set_activity_light(unicorn.ORANGE, False)

                # should we update a remote notify device?
                if use_remote_notify:
                    # get status from the results
                    # TODO: Change this
                    current_status = status.Status.BUSY
                    # Only change the status if it's different than the current status
                    if current_status != previous_status:
                        # update the remote device status
                        particle.set_status(current_status)

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def main():
    global calendar, particle, use_remote_notify

    logging.basicConfig(level=logging.DEBUG)

    # tell the user what we're doing...
    logging.info('\n')
    logging.info(HASHES)
    logging.info(HASH, 'Pi Remind HD Notify                      ', HASH)
    logging.info(HASH, 'By John M. Wargo (https://johnwargo.com) ', HASH)
    logging.info(HASHES)
    logging.info(PROJECT_URL)

    # Read the config file contents
    # https://martin-thoma.com/configuration-files-in-python/
    logging.info('Opening project configuration file (config.json)')
    with open("config.json") as json_data_file:
        config = json.load(json_data_file)
    #  does the config exist (non-empty)?
    if config:
        logging.debug(config)

        if config.access_token and config.device_id and config.ignore_tentative_appointments \
                and config.use_reboot_counter and config.reboot_counter_limit and config.use_remote_notify:
            # Set our global variables
            use_remote_notify = config.use_remote_notify
        else:
            logging.error('One or more settings are missing from the project configuration file')
            logging.error(CONFIG_ERROR_STR)
            sys.exit(0)
    else:
        logging.error('Unable to read the configuration file')
        logging.error(CONFIG_ERROR_STR)
        sys.exit(0)

    if use_remote_notify:
        # Initialize the Particle Cloud object
        particle = ParticleCloud(config.access_token, config.device_id)
        # turn the remote notify status LED off
        particle.set_status(status.Status.OFF)

    # Lets see if we can initialize the calendar
    try:
        calendar = GoogleCalendar(SEARCH_LIMIT, config.ignore_tentative_appointments,
                                  config.use_reboot_counter, config.reboot_retries)
    except Exception as e:
        logging.error('Unable to initialize Google Calendar API')
        logging.error('\nException type:', type(e))
        logging.error('Error:', sys.exc_info()[0])
        unicorn.set_all(unicorn.FAILURE_COLOR)
        time.sleep(5)
        unicorn.off()
        sys.exit(0)

    if config.use_reboot_counter:
        logging.info('Reboot enabled ({} retries)'.format(config.reboot_retries))

    logging.info('Application initialized\n')

    # flash some random LEDs just for fun...
    unicorn.flash_random(5, 0.5)
    # blink all the LEDs GREEN to let the user know the hardware is working
    unicorn.flash_all(3, 0.10, unicorn.GREEN)

    processing_loop()


if __name__ == '__main__':
    try:
        # Initialize the Unicorn HAT
        unicorn.init()
        # do our stuff
        main()
    except KeyboardInterrupt:
        # turn off all of the LEDs
        unicorn.off()
        # tell the user we're exiting
        logging.info('\nExiting application\n')
        # exit the application
        sys.exit(0)
