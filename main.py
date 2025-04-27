# python imports
import datetime as dt
import time
import random

from datetime import datetime, timedelta

# local imports
import const as const
import tee_times as tee
import helpers as hlpr
import email_helper as email_hlpr

"""
main driving file
"""

# PARAMS FOR FILTERING
START_TIME = dt.time(8,30,0)
END_TIME = dt.time(11,11,0)
MIN_NUM_PLAYERS = 1

MIN_WAIT = 3
MAX_WAIT = 10

# tee.get_tee_times(const.ROCKLAND)

while True:
    hlpr.console_log("Fetching new times...")
    hendricks_times = tee.get_tee_times(const.HENDRICKS)
    francis_times = tee.get_tee_times(const.FRANCIS)
    all_times = hendricks_times + francis_times
    filtered_tee_times = tee.get_filtered_tee_times(all_times, START_TIME, END_TIME, MIN_NUM_PLAYERS)
    res = email_hlpr.send_email(filtered_tee_times)
    if res:
        break
    sleep_time_seconds = hlpr.get_wait_time(MIN_WAIT, MAX_WAIT)
    hlpr.console_log(f"Sleeping for {(sleep_time_seconds/60):.1f} minutes")
    time.sleep(sleep_time_seconds)
