"""
Model for Seagul Reading

1. Emotiv Streamer
2. Notification for the subject when mind wandering
"""

import sys
import platform


class Model():
  
  def __init__(self):
    self._subject_name = ""
    self._exp_num = ""

  def get_info(self, subject_name, exp_num):
    self._subject_name = subject_name
    self._exp_num = exp_num
  
  def __str__(self):
    return "subject name: %s, experiment number: %s" % (self._subject_name, self._exp_num) 
  
      


def start_streamer():
  pass



def correlation():
  pass


def notify():
  # works on mac, need to modify on windows
  os = platform.system()
  if os == "Darwin":
    sys.stdout.write('\a')
    sys.stdout.flush()



notify()
