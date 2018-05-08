"""
Model for Seagul Reading

1. Emotiv Streamer
2. Notification for the subject when mind wandering
"""

import sys
import os
import time
import platform
from CCDLUtil.EEGInterface.Emotiv.EmotivInterface import EmotivStreamer
from constants import *


class Model:
  
    def __init__(self):
        self._subject_name = ""
        self._exp_num = ""
        self._streamer = None
        self._rested = False

    def get_info(self, subject_name, exp_num):
        self._subject_name = subject_name
        self._exp_num = exp_num

    def start_streamer(self):
        assert self._subject_name != "" and self._exp_num != ""
        # make sure we have Data/Resting folder
        Model._check_dir(os.path.dirname("../Data/Resting/"))
        self._streamer = EmotivStreamer("../Data/Resting/" + self._exp_num + "_eeg.csv", EMOTIV_LIB_PATH)
        self._streamer.start_recording()

    def stop_streamer(self):
        self._streamer.stop_recording()

    def rested(self):
        self._rested = True

    def is_rested(self):
        return self._rested

    @staticmethod
    def _check_dir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def __str__(self):
        return "subject name: %s, experiment number: %s" % (self._subject_name, self._exp_num)
  

def correlation():
    pass


def notify():
    # works on mac, need to modify on windows
    os = platform.system()
    if os == "Darwin":
        sys.stdout.write('\a')
        sys.stdout.flush()



notify()
