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
from correlation import get_baseline
import pandas as pd
import numpy as np


class Model:
  
    def __init__(self, view, text_num):
        self._subject_name = ""
        self._exp_num = ""
        self._rest_file_path = "../Data/Resting/" + self._exp_num + "_eeg.csv"
        self._read_file_path = "../Data/Reading/" + self._exp_num + "_eeg.csv"
        self._streamer = None
        self._fs = 128
        ### resting related ###
        self._rested = False
        self._baseline_value = None
        self._start_rest_time = None
        self._finish_rest_time = None
        self._csv_line = None
        ### reading related ###
        self._start_read_time = None
        self._finish_read_time = None
        self._last_ping_time = None
        self._is_reading = False
        self._text_num = text_num
        self._text = None
        # load text
        with open("../Text/passage_" + str(self._text_num) + ".txt", "r") as f:
            self._text = [line.strip() + "." for line in f.read().split("\n")]
        ### VIEW ###
        # model should actually avoid dependent on view, but oh well, Peiyun needs it done tomorrow
        self.view = view

    def get_info(self, subject_name, exp_num):
        self._subject_name = subject_name
        self._exp_num = exp_num
        self._rest_file_path = "../Data/Resting/" + self._exp_num + "_eeg.csv"

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
        self._streamer.stop_recording()
        self._calculate_baseline()
        self._finish_rest_time = time.time()
        # return the length of csv file
        self._csv_line = pd.read_csv(self._rest_file_path).shape[0]

    def start_reading(self):
        self._is_reading = True
        self._start_read_time = time.time()
        self._start_streamer(False)

    @threaded(False)
    def detection(self):
        sys.stdout.flush()
        # last least 30 seconds apart
        while self._is_reading:
            if self._last_ping_time is None or time.time() - self._last_ping_time > 30:
                # take some data from out buffer queue
                data = []
                i = 0
                while i < 2 * self._fs:
                    # blocking call
                    data.append(self._streamer.out_buffer_queue.get())
                    sys.stdout.flush()
                    i += 1
                data = np.asarray(data)
                data.reshape((-1, 2 * self._fs))
                #self.ping_and_get_answer()

    def ping_and_get_answer(self):
        answer = self.view.get_pinged("Hello")

    def _start_streamer(self, rest):
        #assert self._subject_name != "" and self._exp_num != ""
        # make sure we have Data/Resting folder
        if rest:
            Model._check_dir(os.path.dirname("../Data/Resting/"))
            self._streamer = EmotivStreamer(self._rest_file_path, EMOTIV_LIB_PATH)
        else:
            Model._check_dir(os.path.dirname("../Data/Reading/"))
            self._streamer = EmotivStreamer(self._read_file_path, EMOTIV_LIB_PATH)
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
