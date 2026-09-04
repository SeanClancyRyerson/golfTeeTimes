# python imports
from datetime import datetime

import requests

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
    foreUP_headers = {
        'X-Authorization': foreUP_auth,
        'X-Fu-Golfer-Location': 'foreup',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return foreUP_headers


def book_tee_time(tee_time: dict, players: int) -> dict:
    course = tee_time[const.COURSE_NAME]
    mapping = const.foreUp_mappings.get(course)
    if mapping is None:
        mapping = next(
            value for value in const.foreUp_mappings.values()
            if value[const.SCHEDULE_ID] == tee_time[const.SCHEDULE_ID]
        )
    session = requests.Session()
    headers = get_foreUP_headers()
    booking_time = tee_time[const.TEE_TIME]
    pending_data = {
        'time': booking_time, 'holes': '18', 'players': str(players),
        'carts': 'false', 'schedule_id': str(tee_time[const.SCHEDULE_ID]),
        'teesheet_side_id': str(tee_time.get('teesheet_side_id', tee_time[const.TEE_ID])),
        'course_id': str(tee_time[const.COURSE_ID]),
        'booking_class_id': str(tee_time.get('booking_class_id', mapping[const.BOOKING_CLASS])),
        'duration': str(tee_time.get('duration', 1)), 'foreup_discount': 'false',
        'foreup_trade_discount_rate': '0', 'trade_min_players': '0',
        'cart_fee': '0', 'cart_fee_tax': '0',
        'green_fee': str(tee_time.get('green_fee', 0)), 'green_fee_tax': '0'
    }
    pending_response = session.post(
        'https://foreupsoftware.com/index.php/api/booking/pending_reservation',
        headers=headers, data=pending_data, timeout=30
    )
    pending_response.raise_for_status()
    pending = pending_response.json()
    if not pending.get('success') or not pending.get('reservation_id'):
        raise RuntimeError(f"ForeUP could not hold the tee time: {pending}")

    payload = dict(tee_time.get('raw', {}))
    payload.update({
        'time': booking_time,
        'start_front': payload.get(
            'start_front',
            int(datetime.strptime(booking_time, '%Y-%m-%d %H:%M').strftime('%Y%m%d%H%M'))
        ),
        'course_id': tee_time[const.COURSE_ID], 'course_name': course,
        'schedule_id': tee_time[const.SCHEDULE_ID],
        'teesheet_id': tee_time[const.SCHEDULE_ID],
        'booking_class_id': tee_time.get('booking_class_id', mapping[const.BOOKING_CLASS]),
        'teesheet_side_id': tee_time.get('teesheet_side_id', tee_time[const.TEE_ID]),
        'holes': '18', 'players': str(players), 'pay_players': str(players),
        'carts': False, 'pending_reservation_id': pending['reservation_id'],
        'validate_only': True
    })
    reservation_url = 'https://foreupsoftware.com/index.php/api/booking/users/reservations'
    validation_response = session.post(reservation_url, headers=headers, json=payload, timeout=30)
    validation_response.raise_for_status()
    validation = validation_response.json()
    if not validation.get('valid'):
        session.delete(
            f"https://foreupsoftware.com/index.php/api/booking/pending_reservation/{pending['reservation_id']}",
            headers=headers, timeout=30
        )
        raise RuntimeError(f"ForeUP rejected the reservation: {validation}")

    payload.pop('validate_only', None)
    booking_response = session.post(reservation_url, headers=headers, json=payload, timeout=30)
    booking_response.raise_for_status()
    booking = booking_response.json()
    if not booking.get('teetime_id'):
        raise RuntimeError(f"ForeUP did not confirm the reservation: {booking}")
    session.delete(
        f"https://foreupsoftware.com/index.php/api/booking/pending_reservation/{pending['reservation_id']}",
        headers=headers, timeout=30
    )
    return booking
