import webuntis
import datetime
import os
from dotenv import load_dotenv
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Schreibrechte für den Kalender anfordern
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    # Der Token speichert deine Anmeldung, damit das Fenster nicht jedes Mal kommt
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Wenn kein gültiger Token da ist, öffne das Login-Fenster
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Speichere den Token für das nächste Mal
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

class Event:
    def __init__(self, name="N/A", date="N/A", startTime="N/A", endTime="N/A", teacher="N/A", room="N/A", text="N/A", homework="N/A"):
        self.name = name
        self.date = date
        self.startTime = startTime
        self.endTime = endTime
        self.teacher = teacher
        self.room = room
        self.text = text
        self.homework = homework

allEvents = []

load_dotenv()

with webuntis.Session(
    server=os.getenv('SERVER'),
    username=os.getenv('USERNAME'),
    password=os.getenv('PASSWORD'),
    school=os.getenv('SCHOOL'),
    useragent='UntisAPIExtractor'
).login() as s:
   
    my_id = s.login_result['personId']
    my_type = s.login_result['personType']
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    friday = monday + datetime.timedelta(days=4)
        
    table = s.timetable(student=my_id, start=monday, end=friday)

    for period in table:
        subject = period.subjects[0].long_name if period.subjects else "Freistunde"
        #teacher = period.teachers[0].id if period.teachers else "N/A"
        room = period.rooms[0].name if period.rooms else "N/A"
        date = period.start.date()
        startTime = period.start.strftime('%H:%M')
        endTime = period.end.strftime('%H:%M')

        #print(f"Fach: {subject}, Raum: {room}, start Zeit: {startTime}, end Zeit: {endTime}, Datum: {date}\n")
        newEvent = Event(
            name = subject,
            room = room,
            date = date,
            startTime = startTime,
            endTime = endTime
        )

        allEvents.append(newEvent)


    #for events in allEvents:
    #print(f"{events.name}, {events.date}, {events.startTime}, {events.endTime}, {events.teacher}, {events.room}, {events.text}, {events.homework}")

def add_event_to_google(service, event_obj):
    google_event = {
        'summary': event_obj.name,
        'location': event_obj.room,
        'description': f"Lehrstoff: {event_obj.text}\nHausaufgaben: {event_obj.homework}",
        'start': {
            'dateTime': f"{event_obj.date}T{event_obj.startTime}:00",
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': f"{event_obj.date}T{event_obj.endTime}:00",
            'timeZone': 'Europe/Berlin',
        },
    }

    event = service.events().insert(calendarId='primary', body=google_event).execute()
    print(f"Termin erstellt: {event.get('htmlLink')}")

service = get_calendar_service()
for ev in allEvents:
    add_event_to_google(service, ev)

