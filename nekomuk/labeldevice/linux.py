# -*- coding: utf-8 -*-
import os
import re

class LabelDevice(object):
    devices = {}
    def __init__(self):
        pattern = r"([^ +]) on (.+) type ([^ ]+) \((.+)\)(?: \[(.+)\]|)"
        lines = os.popen('mount -l').readlines()
        for line in lines:
            data = re.findall(pattern, line)[0]
            self.devices[data[1]] = {
                'filesystem': data[0],
                'path': data[1],
                'type': data[2],
                'flags': data[3],
                'label': data[4],
            }
    def get_device_by_path(self, path):
        for device in sorted(self.devices.keys(), key=len, reverse=True):
            if path.startswith(device):
                return self.devices[device]
    def get_device_by_label(self, label):
        for device in self.devices.values():
            if device['label'] == label:
                return device