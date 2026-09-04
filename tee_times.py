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

def get_tee_times(course: str, date='') -> list:
    tee_times = []
    if date == '':
        weekends = hlpr.get_weekend_dates()
    else:
        weekends = date
    for day in weekends:
        try:
            hlpr.console_log(f"Fetching tee times for {course} on {day}...")
            
            if const.foreUp_mappings[course][const.X_AUTH]:
                r = requests.get(foreUP.get_foreUP_url(course, day), headers=foreUP.get_foreUP_headers()).json()
            else:
                r = requests.get(foreUP.get_foreUP_url(course, day)).json()

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
                    tee_time_obj['booking_class_id'] = tee.get('booking_class_id', const.foreUp_mappings[course][const.BOOKING_CLASS])
                    tee_time_obj['teesheet_side_id'] = tee.get('teesheet_side_id', tee[const.TEE_ID])
                    tee_time_obj['raw'] = tee
                    tee_times.append(tee_time_obj)
                except: 
                    continue
        except requests.exceptions as e:
            print(e)
        time.sleep(3)
    hlpr.console_log(f"A total of {len(tee_times)} tee times were fetched...")
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


def prioritize_tee_times(tee_time_list: list, preferred_time: datetime, start_time: datetime, end_time: datetime) -> list:
    """Order times as preferred, later, earlier, later, earlier within the range."""
    available = {
        datetime.strptime(item[const.TEE_TIME], '%Y-%m-%d %H:%M').time(): item
        for item in tee_time_list
    }
    ordered = []
    offset = 0
    while True:
        offsets = [0] if offset == 0 else [offset, -offset]
        found_in_range = False
        for minute_offset in offsets:
            candidate = (
                datetime.combine(dt.date.today(), preferred_time)
                + dt.timedelta(minutes=minute_offset)
            ).time()
            if start_time <= candidate <= end_time:
                found_in_range = True
                if candidate in available:
                    ordered.append(available.pop(candidate))
        if not found_in_range:
            break
        offset += 10

    ordered.extend(sorted(available.values(), key=lambda item: item[const.TEE_TIME]))
    return ordered


def tee_times_to_string(tee_times: list = []) -> str:
    output_string = ''
    for tee_time_obj in tee_times:
        line = f"{tee_time_obj[const.COURSE_NAME].strip()}\n{(datetime.strptime(tee_time_obj[const.TEE_TIME], '%Y-%m-%d %H:%M')).strftime('%A, %b %d %I:%M%p')}\nAvailable slots: {tee_time_obj[const.AVAILABLE_SPOTS]} \n\n"
        output_string += line
    return output_string