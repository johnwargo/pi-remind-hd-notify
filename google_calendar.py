###########################################################
# Calendar Module
#
# Exposes properties and methods for the Google Calendar
###########################################################

# This project's imports (local modules)
from settings import *
from status import Status
import unicorn_hat as unicorn

# other modules
from dateutil import parser
import logging
import os
import pytz
import socket
import sys
import time
import traceback

# Google Calendar libraries
import datetime
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

reboot_counter = 0

# Initialize the Google Calendar API stuff
# If modifying these scopes, delete the file `~/pi-remind-hd-notify/token.pickle`
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendar:
    # Added to fix an issue when there's an error connecting to the
    # Google Calendar API. The app needs to track whether there's an existing
    # error through the process. If there is, then when checking again for entries
    # the app will leave the light red while checking. Setting it to green if
    # successful.
    _has_error = False

    _busy_only = None
    _display_meeting_summary = None
    _ignore_in_summary = []
    _reminder_only = None
    _use_reboot_counter = None
    _reboot_counter_limit = None
    _service = None
    _use_work_hours = None
    _work_start = None
    _work_end = None

    def __init__(self):
        # Populate the local properties
        logging.info('Calendar Initialization')
        settings = Settings.get_instance()

        _busy_only = settings.get_busy_only()
        logging.info('Calendar: Busy Only: {}'.format(_busy_only))

        _ignore_in_summary = settings.get_ignore_in_summary()
        logging.info('Calendar: Ignore in Summary: {}'.format(_ignore_in_summary))

        _reminder_only = settings.get_reminder_only()
        logging.info('Calendar: Reminder Only: {}'.format(_reminder_only))

        _use_reboot_counter = settings.get_use_reboot_counter()
        logging.info('Calendar: Reboot Counter: {}'.format(_use_reboot_counter))
        if _use_reboot_counter:
            _reboot_counter_limit = settings.get_reboot_counter_limit()
            logging.info('Calendar: Reboot Counter Limit: {}'.format(_reboot_counter_limit))

        _use_work_hours = settings.get_use_working_hours()
        logging.info('Calendar: Use Work Hours: {}'.format(_use_work_hours))
        if _use_work_hours:
            _work_start = settings.get_work_start()
            _work_end = settings.get_work_end()
            logging.info('Work hours: {} to {}'.format(_work_start, _work_end))

        # Turn off logging of specific warnings
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            # logging.debug('Token file exists')
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        logging.debug('Initializing calendar service')
        self._service = build('calendar', 'v3', credentials=creds)
        # Set the timeout for the rest of the Google API calls.
        # need this at its default (infinity, i think) during the registration process.
        socket.setdefaulttimeout(5)  # seconds

    @staticmethod
    def _is_marked_busy(event):
        logging.debug('_is_marked_busy(event)')
        # event is busy if transparency is missing from the event object
        try:
            if event['transparency']:
                return False
            else:
                return True
        except KeyError:
            return True

    @staticmethod
    def _has_reminder(event):
        logging.debug('_has_reminder()')
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
            # overrides = event['reminders'].get('overrides')
            # if overrides:
            if event['reminders'].get('overrides'):
                # OK, then we have a reminder to use
                return True
        # if we got this far, then there must not be a reminder set
        return False

    def ignore_event(self, event_summary):
        if len(self._ignore_in_summary) > 0:
            # loop through the ignore list
            for key in self._ignore_in_summary:
                # see if the ignore keyword is in the lower case summary
                if key in event_summary:
                    return True
            return False
        else:
            return False

    def _is_working_hours(self, event):
        logging.debug('_is_working_hours({})'.format(event))
        event_time = event.time()
        logging.debug('Event Time: {}'.format(event_time))
        # is the current time within working hours?
        return self._work_start < event_time < self._work_end

    @staticmethod
    def _process_upcoming_event(event, start, time_delta):
        logging.debug('_process_upcoming_event(event, {}, {})'.format(start, time_delta))
        event_summary = event['summary'] if 'summary' in event else 'No Title'
        logging.info('Found event: {}'.format(event_summary))
        logging.info('Event starts: {}'.format(start))
        new_event = {
            'summary': event_summary,
            'minutes_to_start': time_delta.total_seconds() // 60}
        return new_event

    @staticmethod
    def _process_upcoming_events(event_list, time_window):
        logging.debug('_process_upcoming_events(event_list, {})'.format(time_window))
        summary_list = []
        nearest_time = time_window
        for event in event_list:
            summary_list.append(event['summary'] if 'summary' in event else 'No Title')
            # find the nearest (soonest) meeting time
            nearest_time = min(nearest_time, event['minutes_to_start'])
        return nearest_time, ', '.join(summary_list)

    def get_status(self, time_window):
        logging.debug('get_status({})'.format(time_window))
        # get the status of the user's calendar
        global reboot_counter
        # get all of the events on the calendar from now through 10 minutes from now
        logging.info('Getting next event')
        # this 'now' is in a different format (UTC)
        now = datetime.datetime.utcnow()
        # Calculate a time search_limit from now
        then = now + datetime.timedelta(minutes=time_window)
        # if we don't have an error from the previous attempt, then change the LED color
        # otherwise leave it alone (it should already be red, so it will stay that way).
        if not self._has_error:
            # turn on a sequential CHECKING_COLOR LED to show that you're requesting data from the Google Calendar API
            unicorn.set_activity_light(unicorn.CHECKING_COLOR, True)
        try:
            # set our base calendar status, assume we're turning the Remote Notify status LED off
            current_status = Status.OFF.value
            # Now check to see whether the LED should be set to Green (free)
            if self._use_work_hours:
                # is the current time within working hours?
                if self._is_working_hours(datetime.datetime.now()):
                    # Is it the weekend?
                    if datetime.datetime.today().weekday() < 5:
                        # No? Working hours on a weekday, so Free
                        logging.debug('Current time is within working hours')
                        current_status = Status.FREE.value
                    else:
                        # working hours, but Weekend, should be OFF
                        logging.debug('Skipping working hours, it\'s the weekend')
                else:
                    # Not working hours, should be OFF
                    logging.debug('Current time is not within working hours')
            else:
                # not using work hours, always set status to FREE
                logging.debug('Working hours disabled')
                current_status = Status.FREE.value

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
            if reboot_counter > 0:
                # reset the reboot counter, since everything worked so far
                reboot_counter = 0
                logging.info('Resetting the reboot counter ({})'.format(reboot_counter))

            # Did we get any events back?
            if not event_list:
                # no? so nothing to do right now
                logging.info('No calendar entries returned')
                # Return values: num_minutes, summary_string, calendar_status
                return 0, '', current_status
            else:
                # what time is it now?
                current_time = pytz.utc.localize(datetime.datetime.utcnow())
                # an empty list of upcoming events, will populate in the following loop
                upcoming_events = []
                logging.info('Events returned: {}'.format(len(event_list)))
                # loop through the events in the list
                for event in event_list:
                    print(event)
                    # write the event to the console
                    logging.debug('Event: {}'.format(event))
                    print(2)
                    # we only care about events that have a start time
                    start = event['start'].get('dateTime')
                    # we only want events that have a start time (skips all day events)
                    # do we have a start time for this event?
                    if start:
                        # get our event summary string
                        event_summary = event['summary'] if 'summary' in event else 'no title'
                        # clockwise events have an icon in the start of the summary
                        # and that was causing an encoding error, so I added this to resolve it
                        event_summary = event_summary.encode('ascii', errors='ignore').strip()
                        logging.debug('Event summary: {}'.format(event_summary))

                        # is this one of the events we're support to just ignore?
                        if not self.ignore_event(event_summary.lower()):
                            # When does the appointment start?
                            # Convert the string it into a Python dateTime object so we can do math on it
                            event_start = parser.parse(start)
                            # does the event start in the future?
                            if current_time < event_start:
                                logging.info('Upcoming event: {}'.format(event_summary))
                                time_delta = event_start - current_time
                                new_event = self._process_upcoming_event(event, start, time_delta)
                                logging.debug('New Event: {}'.format(new_event))
                                # we have an upcoming event
                                if self._reminder_only:
                                    # only use events that have a reminder set
                                    if self._has_reminder(event):
                                        upcoming_events.append(new_event)
                                else:
                                    # add the event to our upcoming event list
                                    upcoming_events.append(new_event)
                            else:
                                logging.info('Ongoing event: {}'.format(event_summary))
                                # we have an ongoing/current event
                                # Are we processing busy events only?
                                if self._busy_only:
                                    # then is the user marked busy for this event?
                                    if self._is_marked_busy(event):
                                        # add the event to our current event list
                                        current_status = Status.BUSY.value
                                else:
                                    if self._is_marked_busy(event):
                                        # add the event to our current event list
                                        current_status = min(current_status, Status.BUSY.value)
                                    else:
                                        current_status = min(current_status, Status.TENTATIVE.value)
                        else:
                            # We're ignoring the event because it contains some strings we don't care about
                            logging.info('Ignoring event: {}'.format(event_summary))

                # start processing our lists
                # do we have any upcoming events?
                if len(upcoming_events) > 0:
                    # then process the list and figure out when the next one is
                    num_minutes, summary_string = self._process_upcoming_events(upcoming_events, time_window)
                else:
                    # No? Then return an invalid number of minutes to the next appointment
                    num_minutes = -1
                    summary_string = ''
                # Return values: num_minutes, summary_string, calendar_status
                return num_minutes, summary_string, current_status
        except Exception as e:
            # Something went wrong, tell the user (just in case they have a monitor on the Pi)
            logging.error('Exception type: {}'.format(type(e)))
            # not much else we can do here except to skip this attempt and try again later
            logging.error('Error: {}'.format(sys.exc_info()[0]))

            # experimenting with a different way to output exception details
            logging.info('print_exc()')
            traceback.print_exc(file=sys.stdout)
            # Another way to output exception details
            logging.info('print_exc(1)')
            traceback.print_exc(limit=1, file=sys.stdout)

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
                logging.info('Incrementing the reboot counter ({})'.format(reboot_counter))
                # did we reach the reboot threshold?
                if reboot_counter == self._reboot_counter_limit:
                    # Reboot the Pi
                    for i in range(1, 10):
                        logging.info('Rebooting in {} seconds'.format(i))
                        time.sleep(1)
                    os.system("sudo reboot")
        # we have to return something here, so making some guesses
        return -1, '', Status.OFF
