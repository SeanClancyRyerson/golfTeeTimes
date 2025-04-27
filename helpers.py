# python imports
from datetime import datetime, timedelta
import random

# local imports
import const as const
import foreUP as foreUP

"""
file for genaric helper functions 
"""

def get_weekend_dates() -> list:
    weekends = []
    today = datetime.now()
    # this saturday 
    # t = timedelta((12 - today.weekday()) % 7)
    # weekends.append((today + t).strftime('%m-%d-%Y'))
    # this sunday 
    t = timedelta((13 - today.weekday()) % 7)
    weekends.append((today + t).strftime('%m-%d-%Y'))
    # next saturday 
    # t = timedelta((12 - today.weekday()) % 7 + 7)
    # weekends.append((today + t).strftime('%m-%d-%Y'))
    # next sunday 
    # t = timedelta((13 - today.weekday()) % 7 + 7)
    # weekends.append((today + t).strftime('%m-%d-%Y'))

    return weekends
    

def within_time_range(string_datetime: str, start_time: datetime, end_time: datetime) -> bool:
    tee_datetime = datetime.strptime(string_datetime, '%Y-%m-%d %H:%M')
    tee_time =  tee_datetime.time()
    if start_time <= tee_time <= end_time:
        return True
    else:
        return False
    

def console_log(log_msg: str) -> str:
    current_time = str(datetime.now().strftime('%X'))
    print(f"{current_time}: {log_msg}")


def get_wait_time(min_wait: int, max_wait: int) -> int:
    """
    values passed in should be in minutes
    """    
    return random.uniform(min_wait, max_wait)*60
