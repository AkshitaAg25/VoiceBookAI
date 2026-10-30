from flask import Flask, request, jsonify, session, send_from_directory
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import calendartest
from calendartest import MY_CALENDAR_ID

from inputstring import process_request
import os

frontend_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Frontend"
)

app = Flask(__name__)
app.secret_key = "voicebook-development-secret"

@app.route("/")
def home():
    return send_from_directory(frontend_folder, "index.html")

@app.route("/style.css")
def stylesheet():
    return send_from_directory(frontend_folder, "style.css")

@app.route("/config.js")
def configuration():
    return send_from_directory(frontend_folder, "config.js")

def execute_appointment(details):
    service = calendartest.authenticate_service_account()
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
        return "Your appointment has been booked successfully."
    
    elif(task=="delete"):
        target_date=details["existing_date"]
        time_of_appointment= datetime.strptime(
            f"{target_date} {details['existing_time']}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
     
        calendartest.delete_appointment(service, calendar_id,time_of_appointment)
        return "Your appointment cancellation has been processed."
    
    elif(task=="check"):
        appointment_date = details["date"]
        target_date = datetime.strptime(
            f"{appointment_date} {details['time']}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        calendartest.check_event(service,calendar_id, target_date)
        return "Your appointment check has been completed."

    elif(task=="reschedule"):
        target_date=details["existing_date"]
        time_of_appointment= datetime.strptime(
            f"{target_date} {details['existing_time']}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        calendartest.delete_appointment(service, calendar_id,time_of_appointment)

        summary="Appointment for "+details["name"]
        start_time = datetime.strptime(
            f"{details['new_date']} {details['new_time']}",
            "%Y-%m-%d %H:%M"
            ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

        end_time = start_time + timedelta(hours=1)

        calendartest.create_new_event(service, calendar_id, summary,start_time,end_time,description="")
        return "Your appointment has been rescheduled."

@app.route("/api/request", methods=["POST"])
def receive_request():

    data = request.get_json()

    user_input = data.get("message", "").strip()

    conversation = session.get("conversation", "")

    if conversation == "":
        conversation = user_input
    else:
        if "the person's name" in session.get("missing_fields", []):
            conversation += "\nAdditional information: for " + user_input
        else:
            conversation += "\nAdditional information: " + user_input

    session["conversation"] = conversation

    result = process_request(conversation)
    session["missing_fields"] = result.get("missing_fields", [])

    if result["status"] == "missing_info":

        return jsonify(result)

    elif result["status"] == "ready":

        details = result["details"]

        message = execute_appointment(details)

        session.pop("conversation", None)
        session.pop("missing_fields", None)

        return jsonify({
            "status": "completed",
            "message": message
        })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
# str="5pm on monday"
# date=dateparser.parse(str)
# start_time=date.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
# end_time=start_time+timedelta(hours=1)
# calendar_id=MY_CALENDAR_ID
# descrption="try"
# summary="trying orchestration"

# calendartest.create_new_event(service, calendar_id, summary,start_time,end_time,description="")


