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
from correlation import get_baseline
import pandas as pd


class Model:
  
    def __init__(self):
        self._subject_name = ""
        self._exp_num = ""
        self._rest_file_path = "../Data/Resting" + self._exp_num + "_eeg.csv"
        self._streamer = None
        ### resting related ###
        self._rested = False
        self._baseline_value = None
        self._start_rest_time = None
        self._finish_rest_time = None
        self._csv_line = None

    def get_info(self, subject_name, exp_num):
        self._subject_name = subject_name
        self._exp_num = exp_num
        self._rest_file_path = "../Data/Resting" + self._exp_num + "_eeg.csv"

    def get_start_rest_time(self):
        assert self._start_rest_time is not None
        return self._start_rest_time

    def get_total_line_count(self):
        assert self._csv_line is not None
        return self._csv_line

    def is_rested(self):
        return self._rested

    def start_resting(self):
        self._start_rest_time = time.time()
        self._start_streamer()
        self._rested = True

    def finish_resting(self):
        self._streamer.stop_recording()
        self._calculate_baseline()
        self._finish_rest_time = time.time()
        # return the length of csv file
        self._csv_line = pd.read_csv(self._rest_file_path).shape[0]

    def _start_streamer(self):
        assert self._subject_name != "" and self._exp_num != ""
        # make sure we have Data/Resting folder
        Model._check_dir(os.path.dirname("../Data/Resting/"))
        self._streamer = EmotivStreamer(self._rest_file_path, EMOTIV_LIB_PATH)
        self._streamer.start_recording()

    def _calculate_baseline(self):
        assert not self._baseline_value and self._rested
        self._baseline_value = get_baseline(self._rest_file_path, 1, 40, 256)

    @staticmethod
    def _check_dir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def __str__(self):
        return "subject name: %s, experiment number: %s" % (self._subject_name, self._exp_num)
  

def notify():
    # works on mac, need to modify on windows
    os = platform.system()
    if os == "Darwin":
        sys.stdout.write('\a')
        sys.stdout.flush()



notify()
