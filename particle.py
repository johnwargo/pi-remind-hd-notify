"""
Particle Module

Exposes methods to trigger Particle Cloud methods for the Remote Notify device
"""

import config


class Particle:
    access_token = ""
    device_id = ""

    def __init__(self):
        access_token = config.ACCESS_TOKEN
        device_id = config.DEVICE_ID

    def config_is_valid(self):
        return self.access_token and self.device_id

    def set_status(self, status):
        # call the Particle API to set the remote notify status
        pass

    def get_status(self):
        # call the Particle API to get the device status
        pass
