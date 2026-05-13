import requests 
from icalendar import Event as iCalEvent
from icalendar import Calendar
from datetime import date, timedelta, datetime
import pytz
import os
from dotenv import load_dotenv
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



load_dotenv()



SERVER = os.getenv('SERVER')
SCHOOL = os.getenv('SCHOOL')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
SCOPES = ['https://www.googleapis.com/auth/calendar']



allEvents = []




def login(session: requests.Session) -> dict:
    resp = session.post(
        f"https://{SERVER}/WebUntis/jsonrpc.do",
        params={"school": SCHOOL},
        json={
            "id": "1",
            "method": "authenticate",
            "params": {
                "user": USERNAME,
                "password": PASSWORD,
                "client": "WebUntisInternalExample",
            },
            "jsonrpc": "2.0",
        },
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Login failed: {data['error']}")
    return data["result"]





def get_jwt(session: requests.Session) -> str:
    resp = session.get(f"https://{SERVER}/WebUntis/api/token/new")
    resp.raise_for_status()
    return resp.text.strip()






def get_tenant_id(session: requests.Session) -> str:
    resp = session.get(f"https://{SERVER}/WebUntis/api/app/config")
    resp.raise_for_status()
    cfg = resp.json()
    
    return (
        cfg.get("tenantId")
        or cfg.get("data", {}).get("tenantId")
        or ""
    )






def internal_headers(jwt: str, tenant_id: str) -> dict:
    return {
        "Authorization": f"Bearer {jwt}",
        "tenant-id": str(tenant_id),
        "X-Requested-With": "XMLHttpRequest",
    }








def get_timetable(session: requests.Session, headers: dict, student_id: int, start: date, end: date) -> list:
    resp = session.get(
        f"https://{SERVER}/WebUntis/api/rest/view/v1/timetable/entries",
        params={
            "start":          start.isoformat(),
            "end":            end.isoformat(),
            "format":         2,
            "resourceType":   "STUDENT",
            "resources":      student_id,
            "periodTypes":    "",
            "timetableType":  "MY_TIMETABLE",
            "layout":         "START_TIME",
        },
        headers=headers,
    )
    resp.raise_for_status()

    entries = []
    for day in resp.json().get("days", []):
        for entry in day.get("gridEntries", []):
            entry["_date"] = day["date"]
            entries.append(entry)
    return entries






def get_homework(session: requests.Session, headers: dict,
                 start: date, end: date) -> list:

    resp = session.get(
        f"https://{SERVER}/WebUntis/api/homeworks/lessons",
        params={
            "startDate": start.strftime("%Y%m%d"),
            "endDate":   end.strftime("%Y%m%d"),
        },
        headers=headers,
    )
    resp.raise_for_status()

    raw = resp.json().get("data", {})
    lessons = {l["id"]: l for l in raw.get("lessons", [])}
    homeworks = raw.get("homeworks", [])

    return homeworks, lessons






def logout(session: requests.Session) -> None:
    session.post(
        f"https://{SERVER}/WebUntis/jsonrpc.do",
        params={"school": SCHOOL},
        json={"id": "1", "method": "logout", "params": {}, "jsonrpc": "2.0"},
    )







def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)






def add_event_to_google(service, event_obj):
    google_event = {
        'summary': event_obj.name,
        'location': event_obj.room,
        'description': f"Course content: {event_obj.text}\n\nHomework: {event_obj.homework}",
        'start': {
            'dateTime': f"{event_obj.startTime}",
            'timeZone': os.getenv('TIMEZONE'),
        },
        'end': {
            'dateTime': f"{event_obj.endTime}",
            'timeZone': os.getenv('TIMEZONE'),
        },
        'colorId': event_obj.color
    }

    event = service.events().insert(calendarId='primary', body=google_event).execute()
    print(f"Appointment created: {event.get('htmlLink')}")






def format_datetime(dt_str: str) -> str:
    tz = pytz.timezone(os.getenv('TIMEZONE', 'Europe/Berlin'))
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
    dt_aware = tz.localize(dt)
    return dt_aware.isoformat()  





def find_homework(homeworks, lessons, subject_short):
    results = []
    for hw in homeworks:
        lesson = lessons.get(hw.get("lessonId", -1), {})
        if lesson.get("subject") == subject_short:
            results.append(hw.get("text", ""))
    return "\n".join(results) if results else ""



today = date.today()
thisWeekDate = f"{today - timedelta(days=today.weekday())}-{today - timedelta(days=today.weekday()) + timedelta(days=4)}"

def export_ics(events: list, filename: str = f"timetable-{thisWeekDate}.ics"):
    cal = Calendar()
    cal.add('prodid', '-//WebUntis Export//DE')
    cal.add('version', '2.0')

    for ev in events:
        ical_event = iCalEvent()
        ical_event.add('summary', ev.name)
        ical_event.add('location', ev.room)
        ical_event.add('description', f"Lehrer: {ev.teacher}\n\nLehrstoff: {ev.text}\n\nHausaufgaben: {ev.homework}")
        ical_event.add('dtstart', datetime.fromisoformat(ev.startTime))
        ical_event.add('dtend', datetime.fromisoformat(ev.endTime))
        cal.add_component(ical_event)

    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"→ Exported .ics file as {filename}")





class Event:
    def __init__(self, name="N/A", startTime="N/A", endTime="N/A", teacher="N/A", room="N/A", text="N/A", homework="N/A", color='8'):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.teacher = teacher
        self.room = room
        self.text = text
        self.homework = homework
        self.color = color





def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })




    # 1. Login
    print("→ Login …\n\n")
    login_data = login(session)
    student_id = login_data.get("personId")
    print(f"   Loged in as Person-ID {student_id}")





    # 2. JWT + Tenant-ID for internal API
    jwt       = get_jwt(session)
    tenant_id = get_tenant_id(session)
    print(f"   JWT received, Tenant-ID: {tenant_id}\n\n")

    headers = internal_headers(jwt, tenant_id)





    # Set the time to the current week
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)





   # 3. Homework
    try:
        homeworks, lessons = get_homework(session, headers, monday, friday + timedelta(days=14))
        if not homeworks:
            pass
        for hw in homeworks:
            due  = str(hw.get("dueDate", "?")) #AUF DAUER WEG
            text = hw.get("text", "(kein Text)")
            print(f"  Fetched Homework: Deadline: {due} –  {text}")
    except Exception as ex:
        print(f"  Error: {ex}\n\n")
    print("\n\n")



    # 4. Aditional Text
    # Coming Soon





    # 5. Timetable
    try:
        entries = get_timetable(session, headers, student_id, monday, friday)
        for e in entries:
            status = e.get("status", "OK")
            start  = e.get("duration", {}).get("start", "?")
            end_t  = e.get("duration", {}).get("end", "?")

            raum = ", ".join(
                p.get("current", p).get("shortName", "?")
                for p in e.get("position1", [])
                if isinstance(p, dict)
            )
            fach = ", ".join(
                p.get("current", p).get("longName", "?")
                for p in e.get("position2", [])
                if isinstance(p, dict)
            )
            lehrer = ", ".join(
                p.get("current", p).get("longName", "?")
                for p in e.get("position3", [])
                if isinstance(p, dict)
            )
            fach_short = ", ".join(
                p.get("current", p).get("shortName", "?")
                for p in e.get("position2", [])
                if isinstance(p, dict)
            )


            flag = "CHANGED" if status == "CHANGED" else ""
            flag = "CANCELLED" if status == "CANCELLED" else flag
            print(f"  Fetched class: {start} – {end_t}  {fach:<20} Lehrer: {lehrer:<8} Raum: {raum} {flag}") 

            if flag == "CHANGED":
                colorCode = '2'
            elif flag == "CANCELLED":
                colorCode = '11'
            else:
                colorCode = '8'

            newEvent = Event(
                name = fach,
                room = raum,
                startTime = format_datetime(start),
                endTime = format_datetime(end_t),
                teacher = lehrer,
                homework = "None :)" if find_homework(homeworks, lessons, fach_short) == "" else find_homework(homeworks, lessons, fach_short), 
                color = colorCode,
            )
            allEvents.append(newEvent)

        print("")
        print("")
    except Exception as ex:
        print(f"  Error: {ex}")


  



    # 6. Logout
    logout(session)
    print("\n→ Loged out.")




    # 7. Put everything in Google Calender or export it as an .ics
    print("\n\n")
    exportAs = os.getenv('EXPORTAS')
    if exportAs == 'Google-Calendar':
        service = get_calendar_service()
        for ev in allEvents:
            add_event_to_google(service, ev)
    elif exportAs == '.ics':
        export_ics(allEvents)
    else:
        print(f"\n Wrong specification of what you want the calender to be exported as.\n You used {exportAs} but the only choices are 'Google-Calender' or '.ics'\n")



if __name__ == "__main__":
    main()


        



