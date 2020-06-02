###########################################################
#  Settings module
#
# Abstracts out all functions related to app configuration
###########################################################

import datetime
import logging
import json

# string displayed by assert statment
CONFIG_ERROR = 'Configuration data not available'
# the config object properties, used when validating the config
CONFIG_PROPERTIES = ["access_token", "busy_only", "debug_mode", "display_meeting_summary", "device_id",
                     "ignore_in_summary", "reboot_counter_limit", "reminder_only", "use_reboot_counter",
                     "use_remote_notify", "use_working_hours", "work_start", "work_end"]


class Settings:
    # singleton instance of this class
    __instance = None
    # Initialize the variable that tells everyone that we have a loaded config file
    _has_config: bool = False

    # local config setting properties
    _access_token = ""
    _busy_only: bool
    _device_id = ""
    _display_meeting_summary = ""
    _ignore_in_summary = []
    _reminder_only: bool
    _use_reboot_counter: bool
    _reboot_counter_limit: int
    _use_remote_notify: bool
    _debug_mode: bool
    _use_working_hours: bool
    _work_start: int
    _work_end: int

    def __init__(self):
        if Settings.__instance is None:
            # then we've not initialized yet
            logging.info('Settings: Initializing class')
            # we're creating an instance of the class, so set that here
            Settings.__instance = self
            logging.info('Settings: Opening project configuration file (config.json)')
            # Read the config file contents
            # https://martin-thoma.com/configuration-files-in-python/
            with open("config.json") as json_data_file:
                config = json.load(json_data_file)
            # assume the config file is invalid
            _has_config = False
            #  did the config read correctly?
            if config:
                # make sure all the required settings are in there
                if self.validate_config(config):
                    # then populate the local variables with the values
                    _has_config = True
                    _busy_only = self.get_config_value(config, 'busy_only', False)
                    _debug_mode = self.get_config_value(config, 'debug_mode', False)
                    _display_meeting_summary = self.get_config_value(config, 'display_meeting_summary', True)
                    _ignore_in_summary = self.get_config_value(config, 'ignore_in_summary', [])
                    _reminder_only = self.get_config_value(config, 'reminder_only', False)
                    _use_reboot_counter = self.get_config_value(config, 'use_reboot_counter', False)
                    _reboot_counter_limit = self.get_config_value(config, 'reboot_counter_limit', 10)
                    _use_remote_notify = self.get_config_value(config, 'use_remote_notify', False)
                    _use_working_hours = self.get_config_value(config, 'use_working_hours', False)
                    # if remote notify is enabled, that's the only time we need...
                    if _use_remote_notify:
                        _access_token = self.get_config_value(config, 'access_token', "")
                        _device_id = self.get_config_value(config, 'device_id', "")
                    if _use_working_hours:
                        # if working hours are enabled, that's the only time we need...
                        work_start = self.get_config_value(config, 'work_start', "8:00")
                        work_end = self.get_config_value(config, 'work_end', "17:30")
                        # convert the time string to a time value
                        _work_start = datetime.datetime.strptime(work_start, '%H:%M').time()
                        _work_end = datetime.datetime.strptime(work_end, '%H:%M').time()
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
        else:
            logging.info('Using existing Settings class')

    @staticmethod
    def get_config_value(config_object, key, default_value):
        try:
            value = config_object[key]
            if value:
                return value
            else:
                return default_value
        except KeyError:
            return default_value

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings()
        return Settings.__instance

    def validate_config(self, config_object):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        # Returns a list of missing attributes for the object
        # These logging statements are info because debug won't be set until after
        # the app validates the config file
        logging.debug('Validating configuration file')
        res = []
        for i, val in enumerate(CONFIG_PROPERTIES):
            try:
                prop = config_object[val]
                logging.info("Config: {}: {}".format(val, prop))
            except KeyError:
                logging.info("Config: {}: MISSING".format(val))
                res.append(val)
        return len(res) < 1, ','.join(res)

    def get_access_token(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        assert self._use_remote_notify, "Remote Notify disabled"
        return self._access_token

    def get_busy_only(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._busy_only

    def get_device_id(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        assert self._use_remote_notify, "Remote Notify disabled"
        return self._device_id

    def get_display_meeting_summary(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._display_meeting_summary

    def get_ignore_in_summary(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._ignore_in_summary

    def get_reminder_only(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._reminder_only

    def get_use_reboot_counter(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._use_reboot_counter

    def get_reboot_counter_limit(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        assert self._use_reboot_counter, "Reboot counter disabled"
        return self._reboot_counter_limit

    def get_use_remote_notify(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._use_remote_notify

    def get_debug_mode(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._debug_mode

    def get_use_working_hours(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        return self._use_working_hours

    def get_work_start(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        assert self._use_working_hours, "Working hours disabled"
        return self._work_start

    def get_work_end(self):
        # don't do anything if we don't have a config file read
        assert self._has_config, CONFIG_ERROR
        assert self._use_working_hours, "Working hours disabled"
        return self._work_end
