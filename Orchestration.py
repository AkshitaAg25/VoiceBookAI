import dateparser
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import calendartest
from calendartest import MY_CALENDAR_ID

str="8 October at 4pm"

date=dateparser.parse(str)
start_time=date.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
end_time=start_time+timedelta(hours=1)
calendar_id=MY_CALENDAR_ID
descrption="try"
summary="trying orchestration"

service = calendartest.authenticate_service_account()

calendartest.create_new_event(service, calendar_id, summary,start_time,end_time,description="")
