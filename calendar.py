###########################################################
# Calendar Module
#
# Exposes properties and methods for the Google Calendar
###########################################################
# TODO: Clean up imports

import datetime
# import math
import os
import socket
import sys
import time

import pytz
from dateutil import parser
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools


class GoogleCalendar:

    global service

    def __init__(self):
        try:
            # Initialize the Google Calendar API stuff
            print('Initializing the Google Calendar API')
            # Google says: If modifying these scopes, delete your previously saved
            # credentials at ~/.credentials/client_secret.json
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
            unicorn.set_all(FAILURE_COLOR)
            #  Wait 5 seconds (so the user can see the error color on the display)
            time.sleep(5)
            # turn off all of the LEDs
            unicorn.off()
            # then exit, nothing else we can do here, right?
            sys.exit(0)

    def has_reminder(self, event):
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

    def get_next_event(self):
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
            unicorn.set_activity_light(CHECKING_COLOR, True)
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
            unicorn.set_activity_light(SUCCESS_COLOR, False)
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
            unicorn.flash_all(1, 2, FAILURE_COLOR)
            # now set the current_activity_light to FAILURE_COLOR to indicate an error state
            # with the last reading
            unicorn.set_activity_light(FAILURE_COLOR, False)
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

