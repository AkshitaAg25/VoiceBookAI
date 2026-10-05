from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'calender-45-c95e4ef20deb.json'

MY_CALENDAR_ID = 'akshitaagarwal718@gmail.com' 

def authenticate_service_account():
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def check_event(service,calender_id, target_date):
    time_min= target_date.isoformat()
    time_max= (target_date+ timedelta(days=1)).isoformat()

    try:
            events_result = service.events().list(
                calendarId=calender_id, 
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print('No upcoming events found.')
                
            for event in events:
                # Get the start time (handles both all-day and specific-time events)
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"{start} - {event['summary']}")
                
    except Exception as e:
        print(f"An error occurred while fetching events: {e}")

def create_new_event(service, calendar_id, summary,start_time,end_time,description=""):
     event_body={
          'summary':summary,
          'description':description,
          'start':{
               'dateTime':start_time.isoformat()
          },
          'end':{
               'dateTime': end_time.isoformat()
          }
     }
     print(f"\n--- Creating Event: '{summary}' ---")
     try:
        created_event = service.events().insert(
            calendarId=calendar_id, body=event_body).execute()
        print(f"Success! Event created: {created_event.get('htmlLink')}")
     except Exception as e:
        print(f"Failed to create event: {e}")
     
def main():
    # Get the authenticated service object once
    service = authenticate_service_account()

    # --- Test Function 1: Check Events ---
    # Set the time to exactly midnight to get the whole day
    target_date = datetime(2026, 10, 6,tzinfo=ZoneInfo("Asia/Kolkata"))  #yyyy,mm,dd
    check_event(service, MY_CALENDAR_ID, target_date)

    # --- Test Function 2: Create Event ---
    # Create an event for tomorrow starting at 10:00 AM UTC and ending at 11:00 AM UTC
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    tomorrow = (now + timedelta(days=1)).replace(hour=10,minute=0,second=0,microsecond=0)
    event_start = tomorrow
    event_end = tomorrow + timedelta(hours=1)
    
    create_new_event(
        service=service, 
        calendar_id=MY_CALENDAR_ID, 
        summary="Automated Python Meeting", 
        start_time=event_start, 
        end_time=event_end,
        description="Testing my new modular functions!"
    )


if __name__ == '__main__':
    main()