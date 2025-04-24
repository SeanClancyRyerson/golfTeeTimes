"""
file for defining constants
"""

HENDRICKS = "Hendricks Field Golf Course"
FRANCIS = "Francis A. Byrne Golf Course"
ROCKLAND = "Rockland Lake State Park Championship Golf Course"

BOOKING_CLASS = 'booking_class'
SCHEDULE_ID = 'schedule_id'
X_AUTH = 'X-Authorization'

foreUp_mappings = {
        HENDRICKS: {
            BOOKING_CLASS: 49726,
            SCHEDULE_ID: 11075,
            X_AUTH: True
        },
        FRANCIS: {
            BOOKING_CLASS: 49772,
            SCHEDULE_ID: 11078,
            X_AUTH: True
        },
        ROCKLAND: {
            BOOKING_CLASS: 51472,
            SCHEDULE_ID: 2442,
            X_AUTH: False
        }
    }

# tee_time_obj fields
COURSE_NAME = 'course_name'
COURSE_ID = 'course_id'
SCHEDULE_ID = 'schedule_id'
TEE_ID = 'teesheet_id'
TEE_TIME = 'time'
AVAILABLE_SPOTS = 'available_spots_18'
GREEN_FEE = 'green_fee'
