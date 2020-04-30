###########################################################
# Particle Module
#
# Exposes methods to trigger Particle Cloud methods for
# the Remote Notify device
###########################################################
# TODO: Clean up imports

# This project's imports (local modules)
from status import Status
#  Other imports
import logging
import requests

PARTICLE_HOST = 'https://api.particle.io/v1/devices/'
PARTICLE_VERB_1 = '/setStatus'
PARTICLE_VERB_2 = '/getStatus'


class ParticleCloud:

    def __init__(self, access_token, device_id):
        # populate the Particle config options
        self._access_token = access_token
        self._device_id = device_id
        self._status = 0

    def set_status(self, status_val):
        logging.debug('Particle Cloud: set_status()')
        return self.invoke_particle_cloud(PARTICLE_VERB_1, status_val.value)

    def get_status(self):
        logging.debug('Particle Cloud: get_status()')
        return self.invoke_particle_cloud(PARTICLE_VERB_2, -1)

    def invoke_particle_cloud(self, verb_string, status):
        logging.debug('Invoking Particle Cloud')
        logging.debug('Access token: {}'.format(self._access_token))
        logging.debug('Device ID: {}'.format(self._device_id))
        logging.debug('Status: {}'.format(status))
        # Build the URL we'll use to connect to the Particle Cloud
        url = PARTICLE_HOST + self._device_id + verb_string
        logging.debug('URL: {}'.format(url))
        if status > -1:
            # body = "access_token={}&params={}".format(self._access_token, status)
            body = {"access_token": self._access_token, "params": status}
        else:
            # body = "access_token={}".format(self._access_token)
            body = {"access_token": self._access_token}
        logging.debug('Body: {}'.format(body))
        # headers = {"Content-Type": "application/x-www-form-urlencoded",
        #            "Content-Length": len(body)}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        logging.debug('Headers: {}'.format(headers))
        logging.debug('Executing request')
        try:
            res = requests.post(url, headers=headers, data=body, timeout=5)
            if res.status_code not in (200, 201):
                logging.debug("Particle Cloud returned {}".format(res.status_code))
                return -1
            else:
                logging.debug('Result {}'.format(res))
                return res.text
        except requests.exceptions.RequestException as e:
            logging.error("Exception attempting to connect to the Particle Cloud")
            logging.error('Response: {}'.format(e.response))
            # logging.error('Response: {}'.format(e.response.json()))
            return -1
