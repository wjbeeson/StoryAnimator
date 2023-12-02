import configparser

from pathlib import Path
import os
import logging

import dto

APOLLO_PATH = Path(os.getenv("APOLLO"))
if not APOLLO_PATH:
    raise Exception("APOLLO environment variable must be defined")

CONFIG_FILENAME=str(APOLLO_PATH/"config/apollo.ini")

def get_apollo_filename( relative_filename ):
    return str(APOLLO_PATH /relative_filename)


class ConfigReader(object):
    def __init__(self, active_profiles=None):
        self._profiles = ["DEFAULT"]
        self._parser = configparser.ConfigParser()
        if not self._parser.read(CONFIG_FILENAME):
            raise Exception(f"Configuration file '{CONFIG_FILENAME}' not found.")

        if active_profiles:
            self._profiles.extend(active_profiles)

    def __getitem__(self, item):
        value = None

        for profile in self._profiles:
            if item in self._parser[profile]:
                value = self._parser[profile][item]

                # some values require evaluation.  if it fails, just return the raw value
                try:
                    value = eval(value)
                except: pass

        return value


def initialize( profiles =[]):
    config = ConfigReader(profiles)

    parser = configparser.ConfigParser()
    if not parser.read(CONFIG_FILENAME):
        raise Exception(f"Configuration file '{CONFIG_FILENAME}' not found.")

    for key, _ in parser["DEFAULT"].items():

        try:
            value = config[key]
            globals()[key.upper()] = value
        except: pass




#
# default initialization to avoid breaking everything.  if you need to use different profiles,
# just call it again
#

initialize()

pass