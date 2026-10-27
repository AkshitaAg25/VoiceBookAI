import dateparser
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import calendartest
from calendartest import MY_CALENDAR_ID

from inputstring import run_voicebook

service = calendartest.authenticate_service_account()

details=run_voicebook()
print(details)
calendar_id=MY_CALENDAR_ID
task=details["task"]

if(task=="book"):
    appointment_date = details["date"]
    start_time = datetime.strptime(
        f"{appointment_date} {details['time']}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    end_time = start_time + timedelta(hours=1)
    summary="Appointment for "+details["name"]
    calendartest.create_new_event(service, calendar_id, summary,start_time,end_time,description="")
elif(task=="delete"):
    target_date=details["existing_date"]
    time_of_appointment= datetime.strptime(
        f"{target_date} {details['existing_time']}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
     
    calendartest.delete_appointment(service, calendar_id,time_of_appointment)
elif(task=="check"):
    appointment_date = details["date"]
    target_date = datetime.strptime(
        f"{appointment_date} {details['time']}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    calendartest.check_event(service,calendar_id, target_date)

elif(task=="reschedule"):
    target_date=details["existing_date"]
    time_of_appointment= datetime.strptime(
        f"{target_date} {details['existing_time']}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    calendartest.delete_appointment(service, calendar_id,time_of_appointment)

    summary="Appointment for "+details["name"]
    start_time = datetime.strptime(
        f"{details["new_date"]} {details['new_time']}",
        "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    end_time = start_time + timedelta(hours=1)

    calendartest.create_new_event(service, calendar_id, summary,start_time,end_time,description="")


# str="5pm on monday"
# date=dateparser.parse(str)
# start_time=date.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
# end_time=start_time+timedelta(hours=1)
# calendar_id=MY_CALENDAR_ID
# descrption="try"
# summary="trying orchestration"

# calendartest.create_new_event(service, calendar_id, summary,start_time,end_time,description="")


