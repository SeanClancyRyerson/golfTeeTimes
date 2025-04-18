# python imports
import requests
import time
import datetime as dt
from datetime import datetime

# local imports
import const as const
import helpers as hlpr
import foreUP as foreUP

"""
file for tee_time specific functions
"""

def get_tee_times(course: str) -> list:
    tee_times = []
    weekends = hlpr.get_weekend_dates()
    for day in weekends:
        try:
            hlpr.console_log(f"Fetching tee times for {course} on {day}...")
            r = requests.get(foreUP.get_foreUP_url(course, day), headers=foreUP.get_foreUP_headers()).json()
            for tee in r:
                tee_time_obj = {}
                try:
                    tee_time_obj[const.COURSE_NAME] = tee[const.COURSE_NAME]
                    tee_time_obj[const.COURSE_ID] = tee[const.COURSE_ID]
                    tee_time_obj[const.SCHEDULE_ID] = tee[const.SCHEDULE_ID]
                    tee_time_obj[const.TEE_ID] = tee[const.TEE_ID]
                    tee_time_obj[const.TEE_TIME] = tee[const.TEE_TIME]
                    tee_time_obj[const.AVAILABLE_SPOTS] = tee[const.AVAILABLE_SPOTS]
                    tee_time_obj[const.GREEN_FEE] = tee[const.GREEN_FEE]
                    tee_times.append(tee_time_obj)
                except: 
                    continue
        except requests.exceptions as e:
            print(e)
        time.sleep(3)
    return tee_times


def get_filtered_tee_times(tee_time_list: list, start_time: datetime = dt.time(0,0,0), end_time: datetime = dt.time(23,59,59), num_players: int = 1) -> list:
    filtered_tee_times = []
    hlpr.console_log(f"Searching for tee times for {num_players} player(s) between {start_time} and {end_time}...")
    for tee_time_obj in tee_time_list:
        if hlpr.within_time_range(tee_time_obj[const.TEE_TIME], start_time, end_time) and tee_time_obj[const.AVAILABLE_SPOTS] >= num_players:
            filtered_tee_times.append(tee_time_obj)
    
    if len(filtered_tee_times) != 0:
        hlpr.console_log(f"Found {filtered_tee_times} tee time(s) meeting requirements!")

    return filtered_tee_times


def tee_times_to_string(tee_times: list = []) -> str:
    output_string = ''
    for tee_time_obj in tee_times:
        line = f"{tee_time_obj[const.COURSE_NAME].strip()}\n{(datetime.strptime(tee_time_obj[const.TEE_TIME], '%Y-%m-%d %H:%M')).strftime('%A, %b %d %I:%M%p')}\nAvailable slots: {tee_time_obj[const.AVAILABLE_SPOTS]} \n\n"
        output_string += line
    return output_string