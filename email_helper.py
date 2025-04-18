# python imports
import smtplib
from email.message import EmailMessage

# local imports
import tee_times as tee
import helpers as hlpr
import private as pvt

"""
file for email related functions
"""

def send_email(tee_times: list) -> bool:
    hlpr.console_log("Sending email...")
    if len(tee_times) == 0:
        hlpr.console_log("No good tee times. Email not sent...")
        return False
    else:
        try:
            tee_time_email = EmailMessage()
            tee_time_email['Subject'] = "Potential Tee Times"
            tee_time_email['From'] = pvt.TEE_TIME_EMAIL
            tee_time_email['To'] = ', '.join(pvt.EMAIL_RECIPIENTS)
            tee_time_email.preamble = 'The following are tee_times fitting your filters.\n'
            tee_time_email.set_content(tee.tee_times_to_string(tee_times))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                s.login(pvt.TEE_TIME_EMAIL, pvt.GSMTP_KEY)
                s.sendmail(pvt.TEE_TIME_EMAIL, pvt.SCR_EMAIL, str(tee_time_email))
                s.quit()
                hlpr.console_log("Email sent!")

            return True
        except Exception as e:
            print(e)
            return False
