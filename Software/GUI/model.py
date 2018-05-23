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
from CCDLUtil.Utility.Decorators import threaded
from constants import *
from correlation import get_baseline, live_power
import pandas as pd
import numpy as np
import view


class Model:
  
    def __init__(self, text_num, ping_interval=5):
        self._subject_name = ""
        self._exp_num = ""
        self._rest_file_path = "../Data/Resting/" + self._exp_num + "_eeg.csv"
        self._read_file_path = "../Data/Reading/" + self._exp_num + "_eeg.csv"
        self._streamer = None
        self._fs = 128
        ### resting related ###
        self._rested = False
        self._rest_mean = None
        self._baseline_value = None
        self._start_rest_time = None
        self._finish_rest_time = None
        self._csv_line = None
        ### reading related ###
        self._start_read_time = None
        self._finish_read_time = None
        self._is_reading = False
        self._text = None
        self._last_ping_time = None
        self._ping_interval = ping_interval
        # load text
        with open("../Text/passage_" + str(text_num) + ".txt", "r") as f:
            self._text = [line.strip() + "." for line in f.read().split("\n")]
            print(len(self._text))
        ### VIEW ###
        self.reading_view = None

    def get_info(self, subject_name, exp_num):
        self._subject_name = subject_name
        self._exp_num = exp_num
        self._rest_file_path = "../Data/Resting/" + self._exp_num + "_eeg.csv"
        self._read_file_path = "../Data/Reading/" + self._exp_num + "_eeg.csv"

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
        self._start_streamer(True)
        self._rested = True

    def finish_resting(self):
        time.sleep(1)
        self._streamer.stop_recording(stop_streamer=True)
        self._calculate_baseline()
        self._finish_rest_time = time.time()
        # return the length of csv file
        self._csv_line = pd.read_csv(self._rest_file_path).shape[0]

    def start_reading(self):
        self._is_reading = True
        self._start_streamer(False)
        self._start_read_time = time.time()
        self.check_mind_wandering()

    def _start_streamer(self, rest):
        assert self._subject_name != "" and self._exp_num != ""
        # make sure we have Data/Resting folder
        if rest:
            Model._check_dir(os.path.dirname("../Data/Resting/"))
            self._streamer = EmotivStreamer(self._rest_file_path, EMOTIV_LIB_PATH)
            self._streamer.start_recording()
        else:
            Model._check_dir(os.path.dirname("../Data/Reading/"))
            self._streamer.set_file(self._read_file_path)

    def _calculate_baseline(self):
        assert not self._baseline_value and self._rested
        self._rest_mean, self._baseline_value = get_baseline(self._rest_file_path, 1, 40, 128)

    def get_text(self, idx):
        if idx < 0 or idx >= len(self._text):
            raise ValueError("text index out of bound!")
        return self._text[idx]

    def set_view(self, reading_view):
        assert isinstance(reading_view, view.ReadingWindow)
        self.reading_view = reading_view

    @threaded(False)
    def check_mind_wandering(self):
        assert self.reading_view is not None
        while self._is_reading:
            if live_power(self._streamer, self._fs, self._rest_mean, self._baseline_value, verbose=True)\
                    and (self._last_ping_time is None or time.time() - self._last_ping_time > self._ping_interval):
                view.play_beep(duration=500)
                self._last_ping_time = time.time()
                # we don't have controllers...
                self.reading_view.flash()

    @staticmethod
    def _check_dir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def __str__(self):
        return "subject name: %s, experiment number: %s" % (self._subject_name, self._exp_num)
