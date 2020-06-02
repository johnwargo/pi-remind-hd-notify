###########################################################
#  Settings module
#
# Abstracts out all functions related to app configuration
###########################################################

import logging
import json

# the config object properties, used when validating the config
CONFIG_PROPERTIES = ["access_token", "busy_only", "debug_mode", "display_meeting_summary", "device_id",
                     "ignore_in_summary", "reboot_counter_limit", "reminder_only", "use_reboot_counter",
                     "use_remote_notify", "use_working_hours", "work_start", "work_end"]

CONFIG_ERROR = 'Configuration data not available'

# Initialize the variable that tells everyone that we have a loaded config file
_has_config: bool = False


def init():
    global _has_config

    logging.info('Settings: Opening project configuration file (config.json)')
    # Read the config file contents
    # https://martin-thoma.com/configuration-files-in-python/
    with open("config.json") as json_data_file:
        config = json.load(json_data_file)
    #  did the config read correctly?
    if config:
        _has_config = True


def has_config():
    return _has_config


def validate_config(config_object):
    # don't do anything if we don't have a config file read
    assert has_config(), CONFIG_ERROR
    # Returns a lit of missing attributes for the object
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
