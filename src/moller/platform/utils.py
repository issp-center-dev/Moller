import datetime
import logging

logger = logging.getLogger(__name__)

def convert_hhmmss_to_seconds(x):
    s = 0
    for v in x.split(':'):
        s = s * 60 + int(v, 10)
    return s

def convert_seconds_to_hhmmss(x):
    return datetime.timedelta(seconds=x)

