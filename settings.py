###########################################################
#  Settings module
#
# Abstracts out all functions related to app configuration
###########################################################
# Singleton example https://gist.github.com/pazdera/1098129

import datetime
import logging
import json

# string displayed by assert statement
CONFIG_ERROR = 'Configuration data not available'
# the config object properties, used when validating the config
CONFIG_PROPERTIES = ["access_token", "busy_only", "debug_mode", "display_meeting_summary", "device_id",
                     "ignore_in_summary", "reboot_counter_limit", "reminder_only", "use_reboot_counter",
                     "use_remote_notify", "use_working_hours", "work_start", "work_end"]

# a place to hold the object from the config file
_config = None


class Settings:

    # singleton instance of this class
    __instance = None

    _busy_only = None
    _debug_mode = None
    _display_meeting_summary = None
    _ignore_in_summary = None
    _reminder_only = None
    _use_remote_notify = None
    _access_token = None
    _device_id = None
    _use_reboot_counter = None
    _reboot_counter_limit = None
    _use_working_hours = None
    _work_end = None
    _work_start = None

    def __init__(self):
        global _config

        if Settings.__instance is None:
            # then we've not initialized yet
            logging.info('Settings: Initializing class')
            # we're creating an instance of the class, so set that here
            Settings.__instance = self
            logging.info('Settings: Opening project configuration file (config.json)')
            # Read the config file contents
            # https://martin-thoma.com/configuration-files-in-python/
            with open("config.json") as json_data_file:
                _config = json.load(json_data_file)
            #  did the config read correctly?
            if _config is not None:
                logging.info('Config file read')
                Settings._busy_only = self.get_config_value(_config, 'busy_only', False)
                Settings._debug_mode = self.get_config_value(_config, 'debug_mode', False)
                Settings._display_meeting_summary = self.get_config_value(_config, 'display_meeting_summary', True)
                Settings._ignore_in_summary = self.get_config_value(_config, 'ignore_in_summary', [])
                Settings._reminder_only = self.get_config_value(_config, 'reminder_only', False)
                Settings._use_reboot_counter = self.get_config_value(_config, 'use_reboot_counter', False)
                logging.info('Busy only: {}'.format(Settings._busy_only))
                logging.info('Debug Mode: {}'.format(Settings._debug_mode))
                logging.info('Display Meeting Summary: {}'.format(Settings._display_meeting_summary))
                logging.info('Ignore in Meeting Summary: {}'.format(Settings._ignore_in_summary))
                logging.info('Reminder Only: {}'.format(Settings._reminder_only))

                logging.info('Use Reboot Counter: {}'.format(Settings._use_reboot_counter))
                if Settings._use_reboot_counter:
                    Settings._reboot_counter_limit = self.get_config_value(_config, 'reboot_counter_limit', 10)
                    logging.info('Reboot Counter Limit: {}'.format(Settings._reboot_counter_limit))

                Settings._use_remote_notify = self.get_config_value(_config, 'use_remote_notify', False)
                logging.info('Use Remote Notify: {}'.format(Settings._use_remote_notify))
                # if remote notify is enabled, that's the only time we need...
                if Settings._use_remote_notify:
                    Settings._access_token = self.get_config_value(_config, 'access_token', "")
                    Settings._device_id = self.get_config_value(_config, 'device_id', "")
                    logging.info('Access Token: {}'.format(Settings._access_token))
                    logging.info('Device ID: {}'.format(Settings._device_id))

                Settings._use_working_hours = self.get_config_value(_config, 'use_working_hours', False)
                logging.debug('Use Working Hours: {}'.format(Settings._use_working_hours))
                if Settings._use_working_hours:
                    # if working hours are enabled, that's the only time we need...
                    # convert the time string to a time value
                    Settings._work_start = datetime.datetime.strptime(
                        self.get_config_value(_config, 'work_start', "8:00"), '%H:%M').time()
                    Settings._work_end = datetime.datetime.strptime(
                        self.get_config_value(_config, 'work_end', "17:30"), '%H:%M').time()
                    logging.info('Work Start: {}'.format(Settings._work_start))
                    logging.info('Work End: {}'.format(Settings._work_end))
        else:
            logging.info('Using existing Settings class')

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings()
        return Settings.__instance

    @staticmethod
    def validate_config_options():
        # list config options, especially missing ones
        global _config
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        # Returns a list of missing attributes for the object
        # These logging statements are info because debug won't be set until after
        # the app validates the config file
        logging.info('Validating configuration file')
        res = []
        for i, val in enumerate(CONFIG_PROPERTIES):
            try:
                prop = _config[val]
                logging.info("Config: {}: {}".format(val, prop))
            except KeyError:
                logging.error("Config: {}: MISSING".format(val))
                res.append(val)

    @staticmethod
    def get_config_value(config_object, key, default_value):
        logging.info('get_config_value(_config, {}, {})'.format(key, default_value))
        try:
            value = config_object[key]
            if value:
                print(value)
                return value
            else:
                print("using default")
                return default_value
        except KeyError:
            print("key error")
            return default_value

    @staticmethod
    def get_access_token():
        assert Settings._use_remote_notify is True, "Remote Notify disabled"
        return Settings._access_token

    @staticmethod
    def get_busy_only():
        return Settings._busy_only

    @staticmethod
    def get_debug_mode():
        return Settings._debug_mode

    @staticmethod
    def get_device_id():
        assert Settings._use_remote_notify is True, "Remote Notify disabled"
        return Settings._device_id

    @staticmethod
    def get_display_meeting_summary():
        return Settings._display_meeting_summary

    @staticmethod
    def get_ignore_in_summary():
        return Settings._ignore_in_summary

    @staticmethod
    def get_reminder_only():
        return Settings._reminder_only

    @staticmethod
    def get_use_reboot_counter():
        return Settings._use_reboot_counter

    @staticmethod
    def get_reboot_counter_limit():
        assert Settings._use_reboot_counter is True, "Reboot counter disabled"
        return Settings._reboot_counter_limit

    @staticmethod
    def get_use_remote_notify():
        return Settings._use_remote_notify

    @staticmethod
    def get_use_working_hours():
        return Settings._use_working_hours

    @staticmethod
    def get_work_start():
        assert Settings._use_working_hours is True, "Working hours disabled"
        return Settings._work_start

    @staticmethod
    def get_work_end():
        assert Settings._use_working_hours is True, "Working hours disabled"
        return Settings._work_end

# _busy_only = self.get_config_value(config, 'busy_only', False)
# _debug_mode = config['debug_mode']
# _display_meeting_summary = config['display_meeting_summary']
# _ignore_in_summary = config['ignore_in_summary']
# _reminder_only = config['reminder_only']
# _use_reboot_counter = config['use_reboot_counter']
# _reboot_counter_limit = config['reboot_counter_limit']
# _use_remote_notify = config['use_remote_notify']
# _use_working_hours = config['use_working_hours']
# # if remote notify is enabled, that's the only time we need...
# if _use_remote_notify:
#     _access_token = config['access_token']
#     _device_id = config['device_id']
# if _use_working_hours:
#     # if working hours are enabled, that's the only time we need...
#     work_start = config['work_start']
#     work_end = config['work_end']
#     # convert the time string to a time value
#     _work_start = datetime.datetime.strptime(work_start, '%H:%M').time()
#     _work_end = datetime.datetime.strptime(work_end, '%H:%M').time()
