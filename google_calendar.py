###########################################################
# Calendar Module
#
# Exposes properties and methods for the Google Calendar
###########################################################
# TODO: Clean up imports
# TODO: Ignore tentative appointments
# TODO: Move reboot counter to remind.py

# This project's imports (local modules)
import status
import unicorn_hat as unicorn

# other modules
import logging
import math
import os
import socket
import sys
import time

import pytz
from dateutil import parser
from httplib2 import Http
# from oauth2client import client, file, tools

# Google Calendar libraries
import datetime
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

reboot_counter = 0

# Initialize the Google Calendar API stuff
# Google says: If modifying these scopes, delete your previously saved
# credentials at ~/.credentials/credentials.json
# On the pi, it's in /root/.credentials/
# SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendar:
    # Added to fix an issue when there's an error connecting to the
    # Google Calendar API. The app needs to track whether there's an existing
    # error through the process. If there is, then when checking again for entries
    # the app will leave the light red while checking. Setting it to green if
    # successful.
    _has_error = False

    _ignore_tentative_appointments = False
    _use_reboot_counter = False
    _reboot_counter_limit = 0
    _service = None
    _search_limit = 10

    def __init__(self, search_limit, ignore_tentative_appointments, use_reboot_counter, reboot_counter_limit):
        _ignore_tentative_appointments = ignore_tentative_appointments
        _use_reboot_counter = use_reboot_counter
        _reboot_counter_limit = reboot_counter_limit
        _search_limit = search_limit

        # logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # logging.debug('Checking token.pickle')
        if os.path.exists('token.pickle'):
            # logging.debug('Token file exists')
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # logging.debug('checking creds')
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # logging.debug('creds are valid')
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                # logging.debug('running local server')
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            # logging.debug('Save the credentials')
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        logging.debug('Initializing calendar service')
        self._service = build('calendar', 'v3', credentials=creds)

        # Set the timeout for the rest of the Google API calls.
        # need this at its default (infinity, i think) during the registration process.
        socket.setdefaulttimeout(5)  # seconds

    @staticmethod
    def _has_reminder(self, event):
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

    @staticmethod
    def get_status(self):
        pass

    def get_next_event(self):
        global reboot_counter
        # modified from https://developers.google.com/google-apps/calendar/quickstart/python
        # get all of the events on the calendar from now through 10 minutes from now
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Getting next event')
        # this 'now' is in a different format (UTC)
        now = datetime.datetime.utcnow()
        # Calculate a time search_limit from now
        then = now + datetime.timedelta(minutes=self._search_limit)
        # if we don't have an error from the previous attempt, then change the LED color
        # otherwise leave it alone (it should already be red, so it will stay that way).
        if not self._has_error:
            # turn on a sequential CHECKING_COLOR LED to show that you're requesting data from the Google Calendar API
            unicorn.set_activity_light(unicorn.CHECKING_COLOR, True)
        try:
            # ask Google for the calendar entries
            events_result = self._service.events().list(
                # get all of them between now and 10 minutes from now
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=then.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime').execute()
            # turn on the SUCCESS_COLOR LED so you'll know data was returned from the Google calendar API
            unicorn.set_activity_light(unicorn.SUCCESS_COLOR, False)
            # Get the event list
            event_list = events_result.get('items', [])
            # initialize this here, setting it to true later if we encounter an error
            self._has_error = False
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
                            if self._has_reminder(event):
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
            unicorn.flash_all(1, 2, unicorn.FAILURE_COLOR)
            # now set the current_activity_light to FAILURE_COLOR to indicate an error state
            # with the last reading
            unicorn.set_activity_light(unicorn.FAILURE_COLOR, False)
            # we have an error, so make note of it
            self._has_error = True
            # check to see if reboot is enabled
            if self._use_reboot_counter:
                # increment the counter
                reboot_counter += 1
                print('Incrementing the reboot counter ({})'.format(reboot_counter))
                # did we reach the reboot threshold?
                if reboot_counter == self._reboot_counter_limit:
                    # Reboot the Pi
                    for i in range(1, 10):
                        print('Rebooting in {} seconds'.format(i))
                        time.sleep(1)
                    os.system("sudo reboot")

        # if we got this far and haven't returned anything, then there's no appointments in the specified time
        # range, or we had an error, so...
        return None
