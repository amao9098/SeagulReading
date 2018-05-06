"""
Model for Seagul Reading

1. Emotiv Streamer
2. Notification for the subject when mind wandering
"""

import sys
import platform


class Model():
  
  def __init__():
    
    


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
