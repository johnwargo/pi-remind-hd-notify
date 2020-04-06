"""
Particle Module

Exposes methods to trigger Particle Cloud methods for the Remote Notify device
"""

import requests

import config

PARTICLE_HOST = 'https://api.particle.io/v1/devices/'
PARTICLE_VERB_1 = '/setStatus'
PARTICLE_VERB_2 = '/getStatus'


class Particle:
    access_token = ""
    device_id = ""

    def __init__(self):
        access_token = config.ACCESS_TOKEN
        device_id = config.DEVICE_ID

    def config_is_valid(self):
        return self.access_token and self.device_id

    def set_status(self, status):
        return self.invoke_particle_cloud(PARTICLE_VERB_1, status)
        # url = PARTICLE_HOST + self.device_id + PARTICLE_VERB_1
        # body = "access_token={}&params={}".format(self.access_token, status)
        # headers = {"Content-Type": "application/x-www-form-urlencoded",
        #            "Content-Length": len(body)}
        # try:
        #     res = requests.post(url, headers=headers, data=body)
        #     if res.status_code not in (200, 201):
        #         print("Particle Cloud returned {}".format(res.status_code))
        #         return -1
        #     else:
        #         print(res)
        #         return int(res.text)
        # except requests.exceptions.RequestException as e:
        #     print("Exception attempting to connect to the Particle Cloud")
        #     print(e.response.json())
        #     return -1

    def get_status(self):
        return self.invoke_particle_cloud(PARTICLE_VERB_2, "")
        # url = PARTICLE_HOST + self.device_id + PARTICLE_VERB_2
        # body = "access_token ={}".format(self.access_token)
        # headers = {"Content-Type": "application/x-www-form-urlencoded",
        #            "Content-Length": len(body)}
        # try:
        #     res = requests.post(url, headers=headers, data=body)
        #     if res.status_code not in (200, 201):
        #         print("Particle Cloud returned {}".format(res.status_code))
        #         return -1
        #     else:
        #         print(res)
        #         return int(res.text)
        # except requests.exceptions.RequestException as e:
        #     print("Exception attempting to connect to the Particle Cloud")
        #     print(e.response.json())
        #     return -1

    def invoke_particle_cloud(self, verb_string, status):
        url = PARTICLE_HOST + self.device_id + verb_string
        if status:
            body = "access_token={}&params={}".format(self.access_token, status)
        else:
            body = "access_token={}".format(self.access_token)
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length": len(body)}
        try:
            res = requests.post(url, headers=headers, data=body)
            if res.status_code not in (200, 201):
                print("Particle Cloud returned {}".format(res.status_code))
                return -1
            else:
                print(res)
                return int(res.text)
        except requests.exceptions.RequestException as e:
            print("Exception attempting to connect to the Particle Cloud")
            print(e.response.json())
            return -1
