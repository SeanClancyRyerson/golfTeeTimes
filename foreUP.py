# python imports

# local imports
import const as const

"""
file for foreUP functions/info
"""

def get_foreUP_url(course: str, date: str) -> str:
    return f'https://foreupsoftware.com/index.php/api/booking/times?time=all&date={date}&holes=all&players=0&booking_class={const.foreUp_mappings[course][const.BOOKING_CLASS]}&schedule_id={const.foreUp_mappings[course][const.SCHEDULE_ID]}&schedule_ids[]=11078&schedule_ids[]=11075&schedule_ids[]=11077&specials_only=0&api_key=no_limits'

def get_foreUP_headers() -> dict:
    foreUP_api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJmb3JldXBzb2Z0d2FyZS5jb20iLCJhdWQiOiJmb3JldXBzb2Z0d2FyZS5jb20iLCJpYXQiOjE3NDUyMzg5NTYsImV4cCI6MTc0NzgzMDk1NiwidWlkIjoiOTkzNzM4NjI2IiwibGV2ZWwiOjAsImNpZCI6IjIyNTI2IiwiZW1wbG95ZWUiOmZhbHNlLCJpc192aXNpdG9yIjp0cnVlfQ.R3FppBPRi5UfuJxlOu9ZQBIFx7G07YXAa3UWQZ6Zn23AcomoWd9rLyeSNJ9qNZn19d-k8olaco1Ses3DyRsFCQ"
    foreUP_auth = "Bearer " + foreUP_api_key
    foreUP_headers = { 'X-Authorization':  foreUP_auth }
    return foreUP_headers