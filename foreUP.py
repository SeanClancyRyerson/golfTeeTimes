# python imports

# local imports
import const as const
import private as pvt

"""
file for foreUP functions/info
"""

def get_foreUP_url(course: str, date: str) -> str:
    return f'https://foreupsoftware.com/index.php/api/booking/times?time=all&date={date}&holes=all&players=0&booking_class={const.foreUp_mappings[course][const.BOOKING_CLASS]}&schedule_id={const.foreUp_mappings[course][const.SCHEDULE_ID]}&schedule_ids[]=11078&schedule_ids[]=11075&schedule_ids[]=11077&specials_only=0&api_key=no_limits'

def get_foreUP_headers() -> dict:
    foreUP_auth = "Bearer " + pvt.foreUP_api_key
    foreUP_headers = { 'X-Authorization':  foreUP_auth }
    return foreUP_headers
