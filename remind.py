#!/usr/bin/python
"""*****************************************************************************************************************
    Pi Remind HD Notify
    Created April 4, 2020.
    By John M. Wargo (https://www.johnwargo.com)

    This application connects to a Google Calendar and determines whether there are any appointments in the next
    few minutes and flashes some LEDs if there are. The project uses a Raspberry Pi 2 device with a Pimoroni
    Unicorn HAT HD (a 16x16 matrix of bright, multicolored LEDs) to display an obnoxious reminder every minute,
    changing color at 10 minutes (WHITE), 5 minutes (YELLOW) and 2 minutes (multi-color swirl).

    Coupled with the Remote Notify project, the server code sends appointment status to the remote notify device
    to make others aware of the user's status (busy, tentative, free).

    Google Calendar example code: https://developers.google.com/google-apps/calendar/quickstart/python
********************************************************************************************************************"""
# TODO: Implement weekend days as a config setting
# TODO: Add option to ignore declined events (not possible with the Calendar API today)
# TODO: Make search limit a config setting (meh)
# TODO: Use threads for all display updates

from __future__ import print_function

# This project's imports (local modules)
from google_calendar import GoogleCalendar
from particle import *
from settings import *
from status import Status
import unicorn_hat as unicorn

#  Other imports
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import socket
import sys
import time

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
cal = None  # Google Calendar
particle = None  # Particle Cloud

debug_mode = False
display_meeting_summary = True
# whether you have a remote notify device connected. Use the config file to override
use_remote_notify = False


def processing_loop():
    global cal, display_meeting_summary, particle

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
            logging.info(HASHES)
            # reset last_minute to the current_minute, of course
            last_minute = current_minute
            # we've moved a minute, so we have work to do
            # get the calendar status from Google Calendar
            num_minutes, summary_string, calendar_status = cal.get_status(SEARCH_LIMIT)
            # num_minutes: How many minutes before the next meeting start time
            # summary_string: Concatenated list of upcoming meeting summaries
            # calendar_status: Remote Notify Status value (busy, tentative, free, off)

            # should we update a remote notify device?
            # Do this first since swirling the display takes longer
            if use_remote_notify:
                # Only change the status if it's different from the current status
                if calendar_status != previous_status:
                    logging.info('Setting Remote Notify status to {}'.format(calendar_status))
                    # Capture the current status for next time
                    previous_status = calendar_status
                    try:
                        # update the remote device status
                        particle.set_status(calendar_status)
                    except Exception as e:
                        # Something went wrong, tell the user (just in case they have a monitor on the Pi)
                        logging.error('Exception type: {}'.format(type(e)))
                        # not much else we can do here except to skip this attempt and try again later
                        logging.error('Error: {}'.format(sys.exc_info()[0]))
                        # light up the array with FAILURE_COLOR LEDs to indicate a problem
                        # unicorn.flash_all(1, 1, unicorn.FAILURE_COLOR)
                        # now set the current_activity_light to FAILURE_COLOR to indicate an error state
                        # with the last reading
                        unicorn.set_activity_light(unicorn.FAILURE_COLOR, False)

            # Any meetings coming up in the next num_minutes minutes?
            if num_minutes > 0:
                if num_minutes != 1:
                    logging.info('Next event starts in {} minutes'.format(num_minutes))
                else:
                    logging.info('Next event starts in 1 minute')
                logging.info('Event list: {}'.format(summary_string))
                # is the appointment between 10 and 5 minutes from now?
                if num_minutes >= FIRST_THRESHOLD:
                    # Flash the lights in WHITE
                    unicorn.flash_all(1, 0.25, unicorn.WHITE)
                    if display_meeting_summary:
                        unicorn.display_text(summary_string, unicorn.WHITE)
                    # set the activity light to WHITE as an indicator
                    unicorn.set_activity_light(unicorn.WHITE, False)
                # is the appointment less than 5 minutes but more than 2 minutes from now?
                elif num_minutes > SECOND_THRESHOLD:
                    # Flash the lights YELLOW
                    unicorn.flash_all(2, 0.25, unicorn.YELLOW)
                    if display_meeting_summary:
                        unicorn.display_text(summary_string, unicorn.YELLOW)
                    # set the activity light to YELLOw as an indicator
                    unicorn.set_activity_light(unicorn.YELLOW, False)
                else:
                    # hmm, less than 2 minutes, almost time to start!
                    # swirl the lights. Longer every second closer to start time
                    unicorn.do_swirl(int((4 - num_minutes) * 50))
                    if display_meeting_summary:
                        unicorn.display_text(summary_string, unicorn.ORANGE)
                    # set the activity light to SUCCESS_COLOR (green by default)
                    unicorn.set_activity_light(unicorn.ORANGE, False)
            else:
                logging.debug('No upcoming events found')

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def main():
    global cal, debug_mode, display_meeting_summary, particle, use_remote_notify

    # Logging
    # Set up the basic console logger
    format_str = '%(asctime)s %(levelname)s %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=format_str, level=logging.INFO, datefmt=date_format)
    logger = logging.getLogger()
    # Add a file handler as well; roll at midnight and keep 7 copies
    file_handler = TimedRotatingFileHandler("remind_log", when="midnight", backupCount=6)
    log_formatter = logging.Formatter(format_str, datefmt=date_format)
    file_handler.setFormatter(log_formatter)
    # file log always gets debug; console log level set in the config
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # tell the user what we're doing...
    print('\n')
    print(HASHES)
    print(HASH, 'Pi Remind HD Notify                      ', HASH)
    print(HASH, 'By John M. Wargo (https://johnwargo.com) ', HASH)
    print(HASHES)
    print('From: ' + PROJECT_URL + '\n')

    settings = Settings.get_instance()
    settings.validate_config_options()

    debug_mode = settings.get_debug_mode()
    if debug_mode:
        logging.info('Remind: Enabling debug mode')
        logger.setLevel(logging.DEBUG)

    display_meeting_summary = settings.get_display_meeting_summary()

    use_remote_notify = settings.get_use_remote_notify()
    if use_remote_notify:
        logging.info('Remind: Remote Notify Enabled')
        access_token = settings.get_access_token()
        device_id = settings.get_device_id()
        # Check to see if the string values we need are populated
        if len(access_token) < 1 or len(device_id) < 1:
            logging.error('One or more values are missing from the project configuration file')
            logging.error(CONFIG_ERROR_STR)
            sys.exit(0)
        logging.debug('Remind: Creating Particle object')
        particle = ParticleCloud(access_token, device_id)

        logging.info('Remind: Resetting Remote Notify status')
        particle.set_status(Status.FREE.value)
        time.sleep(1)
        particle.set_status(Status.OFF.value)

    # is the reboot counter in play?
    use_reboot_counter = settings.get_use_reboot_counter()
    if use_reboot_counter:
        # then get the reboot counter limit
        reboot_counter_limit = settings.get_reboot_counter_limit()
        # and tell the user the feature is enabled
        logging.info('Remind: Reboot enabled ({} retries)'.format(reboot_counter_limit))

    logging.info('Remind: Initializing Google Calendar interface')
    try:
        cal = GoogleCalendar()
        # Set the timeout for the rest of the Google API calls.
        # need this at its default during the registration process.
        socket.setdefaulttimeout(5)  # seconds
    except Exception as e:
        logging.error('Remind: Unable to initialize Google Calendar API')
        logging.error('Exception type: {}'.format(type(e)))
        logging.error('Error: {}'.format(sys.exc_info()[0]))
        unicorn.set_all(unicorn.FAILURE_COLOR)
        time.sleep(5)
        unicorn.off()
        sys.exit(0)

    logging.info('Remind: Application initialized')

    # flash some random LEDs just for fun...
    unicorn.flash_random(5, 0.5)
    # blink all the LEDs GREEN to let the user know the hardware is working
    unicorn.flash_all(3, 0.10, unicorn.GREEN)
    # get to work
    processing_loop()


if __name__ == '__main__':
    try:
        unicorn.init()
        main()
    except KeyboardInterrupt:
        logging.info('\n\nStopped by user, exiting...\n')
    except RuntimeError as err:
        logging.error("\n\nRuntime Error: {0}\n".format(err))
    finally:
        unicorn.off()  # turn off all the LEDs
        logging.shutdown()  # close the log, write all entries to disk
        sys.exit(0)  # exit the application
