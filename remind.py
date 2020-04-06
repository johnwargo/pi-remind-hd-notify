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
# TODO: split Unicorn HAT functions to a separate module

from __future__ import print_function

import datetime
import math
import os
import socket
import sys
import time

import pytz
import unicornhathd
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
remote_notify_status = 0


def has_reminder(event):
    # Return true if there's a reminder set for the event
    # First, check to see if there is a default reminder set
    # Yes, I know I could have done this and the next check without using variables
    # this approach just makes the code easier to understand
    has_default_reminder = event['reminders'].get('useDefault')
    if has_default_reminder:
        # if yes, then we're good
        return True
    else:
        # are there overrides set for reminders?
        overrides = event['reminders'].get('overrides')
        if overrides:
            # OK, then we have a reminder to use
            return True
    # if we got this far, then there must not be a reminder set
    return False


def get_next_event():
    global has_error, reboot_counter

    # modified from https://developers.google.com/google-apps/calendar/quickstart/python
    # get all of the events on the calendar from now through 10 minutes from now
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Getting next event')
    # this 'now' is in a different format (UTC)
    now = datetime.datetime.utcnow()
    # Calculate a time search_limit from now
    then = now + datetime.timedelta(minutes=SEARCH_LIMIT)
    # if we don't have an error from the previous attempt, then change the LED color
    # otherwise leave it alone (it should already be red, so it will stay that way).
    if not has_error:
        # turn on a sequential CHECKING_COLOR LED to show that you're requesting data from the Google Calendar API
        set_activity_light(CHECKING_COLOR, True)
    try:
        # ask Google for the calendar entries
        events_result = service.events().list(
            # get all of them between now and 10 minutes from now
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=then.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime').execute()
        # turn on the SUCCESS_COLOR LED so you'll know data was returned from the Google calendar API
        set_activity_light(SUCCESS_COLOR, False)
        # Get the event list
        event_list = events_result.get('items', [])
        # initialize this here, setting it to true later if we encounter an error
        has_error = False
        # reset the reboot counter, since everything worked so far
        reboot_counter = 0
        # did we get a return value?
        if not event_list:
            # no? Then no upcoming events at all, so nothing to do right now
            print(datetime.datetime.now(), 'No entries returned')
            return None
        else:
            # what time is it now?
            current_time = pytz.utc.localize(datetime.datetime.utcnow())
            # loop through the events in the list
            for event in event_list:
                # we only care about events that have a start time
                start = event['start'].get('dateTime')
                # return the first event that has a start time
                # so, first, do we have a start time for this event?
                if start:
                    # When does the appointment start?
                    # Convert the string it into a Python dateTime object so we can do math on it
                    event_start = parser.parse(start)
                    # does the event start in the future?
                    if current_time < event_start:
                        # only use events that have a reminder set
                        if has_reminder(event):
                            # no? So we can use it
                            event_summary = event['summary'] if 'summary' in event else 'No Title'
                            print('Found event:', event_summary)
                            print('Event starts:', start)
                            # figure out how soon it starts
                            time_delta = event_start - current_time
                            # Round to the nearest minute and return with the object
                            event['num_minutes'] = time_delta.total_seconds() // 60
                            return event
    except Exception as e:
        # Something went wrong, tell the user (just in case they have a monitor on the Pi)
        print('\nException type:', type(e))
        # not much else we can do here except to skip this attempt and try again later
        print('Error:', sys.exc_info()[0])
        # light up the array with FAILURE_COLOR LEDs to indicate a problem
        flash_all(1, 2, FAILURE_COLOR)
        # now set the current_activity_light to FAILURE_COLOR to indicate an error state
        # with the last reading
        set_activity_light(FAILURE_COLOR, False)
        # we have an error, so make note of it
        has_error = True
        # check to see if reboot is enabled
        if REBOOT_COUNTER_ENABLED:
            # increment the counter
            reboot_counter += 1
            print('Incrementing the reboot counter ({})'.format(reboot_counter))
            # did we reach the reboot threshold?
            if reboot_counter == REBOOT_NUM_RETRIES:
                # Reboot the Pi
                for i in range(1, 10):
                    print('Rebooting in {} seconds'.format(i))
                    time.sleep(1)
                os.system("sudo reboot")

    # if we got this far and haven't returned anything, then there's no appointments in the specified time
    # range, or we had an error, so...
    return None


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
                    flash_all(1, 0.25, WHITE)
                    # display the event summary
                    display_text(next_event['summary'], WHITE)
                    # set the activity light to WHITE as an indicator
                    set_activity_light(WHITE, False)
                # is the appointment less than 5 minutes but more than 2 minutes from now?
                elif num_minutes > SECOND_THRESHOLD:
                    # Flash the lights YELLOW
                    flash_all(2, 0.25, YELLOW)
                    # display the event summary
                    display_text(next_event['summary'], YELLOW)
                    # set the activity light to YELLOw as an indicator
                    set_activity_light(YELLOW, False)
                else:
                    # hmmm, less than 2 minutes, almost time to start!
                    # swirl the lights. Longer every second closer to start time
                    do_swirl(int((4 - num_minutes) * 50))
                    # display the event summary
                    display_text(next_event['summary'], ORANGE)
                    # set the activity light to SUCCESS_COLOR (green by default)
                    set_activity_light(ORANGE, False)
        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def main():
    #  used to setup our status indicator at the bottom of the led array
    global current_activity_light, indicator_row, service, u_height, u_width

    # tell the user what we're doing...
    print('\n')
    print(HASHES)
    print(HASH, 'Pi Remind (HD)                           ', HASH)
    print(HASH, 'https://github.com/johnwargo/pi-remind-hd', HASH)
    print(HASH, 'By John M. Wargo (www.johnwargo.com)     ', HASH)
    print(HASHES)

    # Clear the display (just in case)
    unicornhathd.clear()
    # Initialize  all LEDs to black
    unicornhathd.set_all(0, 0, 0)
    # set the display orientation to zero degrees
    unicornhathd.rotation(90)
    # set u_width and u_height with the appropriate parameters for the HAT
    u_width, u_height = unicornhathd.get_shape()
    # calculate where we want to put the indicator light
    indicator_row = u_height - 1

    # The app flashes a GREEN light in the first row every time it connects to Google to check the calendar.
    # The LED increments every time until it gets to the other side then starts over at the beginning again.
    # The current_activity_light variable keeps track of which light lit last. At start it's at -1 and goes from there.
    current_activity_light = u_width

    # Set a specific brightness level for the Pimoroni Unicorn HAT, otherwise it's pretty bright.
    # Comment out the line below to see what the default looks like.
    unicornhathd.brightness(0.5)

    # output whether reboot mode is enabled
    if REBOOT_COUNTER_ENABLED:
        print('Reboot enabled ({} retries)'.format(REBOOT_NUM_RETRIES))

    try:
        # Initialize the Google Calendar API stuff
        print('Initializing the Google Calendar API')
        # Google says: If modifying these scopes, delete your previously saved credentials at ~/.credentials/client_secret.json
        # On the pi, it's in /root/.credentials/
        SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
        store = file.Storage('google_api_token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('calendar', 'v3', http=creds.authorize(Http()))

        # Set the timeout for the rest of the Google API calls.
        # need this at its default (infinity, i think) during the registration process.
        socket.setdefaulttimeout(10)  # 10 seconds
    except Exception as e:
        print('\nException type:', type(e))
        # not much else we can do here except to skip this attempt and try again later
        print('Error:', sys.exc_info()[0])
        print('Unable to initialize Google Calendar API')
        # make all the LEDs red
        set_all(FAILURE_COLOR)
        #  Wait 5 seconds (so the user can see the error color on the display)
        time.sleep(5)
        # turn off all of the LEDs
        unicornhathd.off()
        # then exit, nothing else we can do here, right?
        sys.exit(0)

    print('Application initialized\n')

    # flash some random LEDs just for fun...
    flash_random(5, 0.5)
    # blink all the LEDs GREEN to let the user know the hardware is working
    flash_all(3, 0.10, GREEN)

    calendar_loop()


if __name__ == '__main__':
    try:
        # do our stuff
        main()
    except KeyboardInterrupt:
        # turn off all of the LEDs
        unicornhathd.off()
        # tell the user we're exiting
        print('\nExiting application\n')
        # exit the application
        sys.exit(0)
