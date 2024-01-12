import datetime
import logging

logger = logging.getLogger(__name__)

def convert_hhmmss_to_seconds(x):
    s = 0
    for v in x.split(':'):
        s = s * 60 + int(v, 10)
    return s

def convert_seconds_to_hhmmss(x):
    sec = x % 60
    min = (x // 60) % 60
    #hour = (x // 60 // 60) % 24
    #day = (x // 60 // 60 // 24)
    hour = (x // 60 // 60)
    day = 0

    if day > 0:
        s = "{:d}-{:02d}:{:02d}:{:02d}".format(day,hour,min,sec)
    else:
        s = "{:02d}:{:02d}:{:02d}".format(hour,min,sec)
    return s

