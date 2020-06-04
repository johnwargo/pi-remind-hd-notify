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

    def __init__(self):
        global _config
        self._busy_only = None
        self._debug_mode = None
        self._display_meeting_summary = None
        self._ignore_in_summary = None
        self._reminder_only = None
        self._use_remote_notify = None
        self._access_token = None
        self._device_id = None
        self._use_reboot_counter = None
        self._reboot_counter_limit = None
        self._use_working_hours = None
        self._work_end = None
        self._work_start = None

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
                logging.info('Config: {}'.format(_config))
                # make sure all the required settings are in there
                count, lst = Settings.validate_config(True)
                if count < 1:
                    logging.info('Config file validated')
                    _busy_only = self.get_config_value(_config, 'busy_only', False)
                    _debug_mode = self.get_config_value(_config, 'debug_mode', False)
                    _display_meeting_summary = self.get_config_value(_config, 'display_meeting_summary', True)
                    _ignore_in_summary = self.get_config_value(_config, 'ignore_in_summary', [])
                    _reminder_only = self.get_config_value(_config, 'reminder_only', False)
                    _use_reboot_counter = self.get_config_value(_config, 'use_reboot_counter', False)
                    _use_remote_notify = self.get_config_value(_config, 'use_remote_notify', False)
                    _use_working_hours = self.get_config_value(_config, 'use_working_hours', False)
                    logging.info('Busy only: {}'.format(_busy_only))
                    logging.info('Debug Mode: {}'.format(_debug_mode))
                    logging.info('Display Meeting Summary: {}'.format(_display_meeting_summary))
                    logging.info('Ignore in Meeting Summary: {}'.format(_ignore_in_summary))
                    logging.info('Reminder Only: {}'.format(_reminder_only))

                    logging.info('Use Reboot Counter: {}'.format(_use_reboot_counter))
                    if _use_reboot_counter:
                        _reboot_counter_limit = self.get_config_value(_config, 'reboot_counter_limit', 10)
                        logging.info('Reboot Counter Limit: {}'.format(_reboot_counter_limit))

                    logging.info('Use Remote Notify: {}'.format(_use_remote_notify))
                    # if remote notify is enabled, that's the only time we need...
                    if _use_remote_notify:
                        _access_token = self.get_config_value(_config, 'access_token', "")
                        _device_id = self.get_config_value(_config, 'device_id', "")
                        logging.info('Access Token: {}'.format(_access_token))
                        logging.info('Device ID: {}'.format(_device_id))
                    logging.debug('Use Working Hours: {}'.format(_use_working_hours))

                    if _use_working_hours:
                        # if working hours are enabled, that's the only time we need...
                        work_start = self.get_config_value(_config, 'work_start', "8:00")
                        work_end = self.get_config_value(_config, 'work_end', "17:30")
                        # convert the time string to a time value
                        _work_start = datetime.datetime.strptime(work_start, '%H:%M').time()
                        _work_end = datetime.datetime.strptime(work_end, '%H:%M').time()
                        logging.info('Work Start: {}'.format(_work_start))
                        logging.info('Work End: {}'.format(_work_end))
        else:
            logging.info('Using existing Settings class')

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings()
        return Settings.__instance

    @staticmethod
    def validate_config(show_output):
        global _config
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        # Returns a list of missing attributes for the object
        # These logging statements are info because debug won't be set until after
        # the app validates the config file
        logging.info('Validating configuration file')
        res = []
        for i, val in enumerate(CONFIG_PROPERTIES):
            # logging.info('Key[{}]: {}'.format(i, val))
            try:
                prop = _config[val]
                if show_output:
                    logging.info("Config: {}: {}".format(val, prop))
            except KeyError:
                if show_output:
                    logging.info("Config: {}: MISSING".format(val))
                res.append(val)
        return len(res) < 1, ','.join(res)

    @staticmethod
    def get_config_value(config_object, key, default_value):
        logging.info('get_config_value(_config, {}, {}'.format(key, default_value))
        try:
            value = config_object[key]
            if value:
                return value
            else:
                return default_value
        except KeyError:
            return default_value

    def get_access_token(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        assert self._use_remote_notify is True, "Remote Notify disabled"
        return self._access_token

    def get_busy_only(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._busy_only

    def get_device_id(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        assert self._use_remote_notify is True, "Remote Notify disabled"
        return self._device_id

    def get_display_meeting_summary(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._display_meeting_summary

    def get_ignore_in_summary(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._ignore_in_summary

    def get_reminder_only(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._reminder_only

    def get_use_reboot_counter(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._use_reboot_counter

    def get_reboot_counter_limit(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        assert self._use_reboot_counter is True, "Reboot counter disabled"
        return self._reboot_counter_limit

    def get_use_remote_notify(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._use_remote_notify

    def get_debug_mode(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._debug_mode

    def get_use_working_hours(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        return self._use_working_hours

    def get_work_start(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        assert self._use_working_hours is True, "Working hours disabled"
        return self._work_start

    def get_work_end(self):
        # don't do anything if we don't have a config file read
        assert _config is not None, CONFIG_ERROR
        assert self._use_working_hours is True, "Working hours disabled"
        return self._work_end

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
