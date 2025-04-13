# python imports
import datetime as dt

# local imports
import const as const
import tee_times as tee
import email_helper as email_hlpr

"""
main driving file
"""
hendricks_times = tee.get_tee_times(const.HENDRICKS)
francis_times = tee.get_tee_times(const.FRANCIS)
all_times = hendricks_times + francis_times


# PARAMS FOR FILTERING
START_TIME = dt.time(8,30,0)
END_TIME = dt.time(11,30,0)
NUM_PLAYERS = 2

filtered_tee_times = tee.get_filtered_tee_times(all_times, START_TIME, END_TIME, NUM_PLAYERS)

res = email_hlpr.send_email(filtered_tee_times)
