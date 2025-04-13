# python imports
from datetime import datetime, timedelta

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
    t = timedelta((12 - today.weekday()) % 7)
    weekends.append((today + t).strftime('%m-%d-%Y'))
    # this sunday 
    t = timedelta((13 - today.weekday()) % 7)
    weekends.append((today + t).strftime('%m-%d-%Y'))
    # next saturday 
    t = timedelta((12 - today.weekday()) % 7 + 7)
    weekends.append((today + t).strftime('%m-%d-%Y'))
    # next saturday 
    t = timedelta((13 - today.weekday()) % 7 + 7)
    weekends.append((today + t).strftime('%m-%d-%Y'))

    return weekends
    

def within_time_range(string_datetime: str, start_time: datetime, end_time: datetime) -> bool:
    tee_datetime = datetime.strptime(string_datetime, '%Y-%m-%d %H:%M')
    tee_time =  tee_datetime.time()
    if start_time <= tee_time <= end_time:
        return True
    else:
        return False
    

