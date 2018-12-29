from __future__ import print_function
from selenium import webdriver
import time
import datetime
from datetime import datetime, date, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/calendar'
# it's critical the scope is either ending in calendar or calendar.events

# you need the libraries for google calendar, datetime, and selenium
# you also need the google credentials.json which is here https://developers.google.com/calendar/quickstart/python


class Shift:

    def __init__(self, day, date, position, start_time, end_time):
        self.day = day
        self.date = date
        self.position = position
        self.startTime = datetime.strptime(start_time, "%I:%M%p").strftime("%H:%M:%S")
        self.endTime = datetime.strptime(end_time, "%I:%M%p").strftime("%H:%M:%S")

    def make_event(self):
        working = False
        now = self.date + 'T' + self.startTime + '-08:00'
        now_iso = (datetime.strptime(now, "%Y-%m-%dT%H:%M:%S-08:00").isoformat() + 'Z')
        # print(now_iso)
        tomorrow_iso = ((datetime.strptime(now, "%Y-%m-%dT%H:%M:%S-08:00") + timedelta(days=1)).isoformat() + 'Z')
        # print(tomorrow_iso)
        events_result = service.events().list(calendarId='primary', timeMin=now_iso, timeMax=tomorrow_iso,
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
        for event in events:
            print(event['summary'])
            if "Work" in event['summary']:
                working = True
        if working:
            return None
        else:
            event = {
                'summary': 'Work',
                'location': '5500 Grossmont Center Dr #1, La Mesa, CA 91942',  # the address of the store you work at
                'description': self.position,  # the position you're working
                'start': {
                    'dateTime': now
                },
                'end': {
                    'dateTime': self.date + 'T' + self.endTime + '-08:00'
                }
            }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))


# you need a google chrome webdriver for this to work, and you need to specify its location below
# download it online and put one where this is pointing or wherever you feel like it just change the destination

chromeDriver = 'chromedriver.exe'
browser = webdriver.Chrome(chromeDriver)
browser.get('http://wss.target.com/selfservice')
username = browser.find_element_by_id("loginID")
password = browser.find_element_by_id("pass")
username.send_keys("70097019")  # your username in the quotes
password.send_keys("!brother_2")  # your password in the quotes
login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
login_attempt.submit()
time.sleep(7)  # the sleep dictates how many seconds to wait before trying to proceed
# if your computer, connection, or kronos sucks, probably up it a bit
qna = browser.find_element_by_id('sec_qna')
qna.click()  # this has to be a click to trick it into logging in if you're curious
login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
login_attempt.submit()
time.sleep(6)  # same as before, up this number if the program keeps bugging out
answer = browser.find_element_by_id("answer0")
# this next chunk looks for the keyword in your security questions
# there are 3 security questions but you only need to specify 2 for it to get them all
# using the first one as an example, if it sees "person" it knows the question is 'who if your favorite person'
# it them sends the answer "brother" for example
# change 'person' and 'car' if you need to recognize other questions like "what is the name of your first pet"
# then do "if "pet" send_keys "max"
# sorry for the length of this explanation but this is the sloppiest part. promise <3
if "person" in browser.page_source:
    answer.send_keys("mom")
elif "car" in browser.page_source:
    answer.send_keys("camero")
else:
    answer.send_keys("paws")  # the else is the last question and doesn't even check for the question, just send the last
    # answer
submit = browser.find_element_by_id("submit-button")
submit.click()
time.sleep(5)
# again you might need to change the sleep number here depending on your circumstances
table = browser.find_element_by_class_name("request_table_bordered")
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

for x in range(2, 9):
    # this loop cycles through the week and assembles your shift information and creates the event
    days = browser.find_element_by_xpath("//*[@id='page_content']/table[1]/tbody/tr[1]/td/table[3]/tbody/tr[1]/td["
                                         + str(x) + "]")
    shift = browser.find_element_by_xpath("//*[@id='page_content']/table[1]/tbody/tr[1]/td/table[3]/tbody/tr[3]/td["
                                          + str(x) + "]")
    if not shift.text.strip():
        continue
    shift_info = (days.text + '\n' + shift.text)

    workday = Shift(shift_info.splitlines()[0],
                    datetime.strptime(shift_info.splitlines()[1], "%m/%d/%y").strftime("%Y-%m-%d"),
                    shift_info.splitlines()[2],
                    shift_info.splitlines()[3].split('-')[0].strip(),
                    shift_info.splitlines()[3].split('-')[1].strip())
    workday.make_event()

next = browser.find_element_by_xpath("//*[@id='page_content']/table[1]/tbody/tr[1]/td/table[2]/tbody/tr[1]/td/div/a[2]")
next.click()

for x in range(2, 9):
    # this loop cycles through the week and assembles your shift information and creates the event
    days = browser.find_element_by_xpath("//*[@id='page_content']/table[1]/tbody/tr[1]/td/table[3]/tbody/tr[1]/td["
                                         + str(x) + "]")
    shift = browser.find_element_by_xpath("//*[@id='page_content']/table[1]/tbody/tr[1]/td/table[3]/tbody/tr[3]/td["
                                          + str(x) + "]")
    if not shift.text.strip():
        continue
    shift_info = (days.text + '\n' + shift.text)

    workday = Shift(shift_info.splitlines()[0],
                    datetime.strptime(shift_info.splitlines()[1], "%m/%d/%y").strftime("%Y-%m-%d"),
                    shift_info.splitlines()[2],
                    shift_info.splitlines()[3].split('-')[0].strip(),
                    shift_info.splitlines()[3].split('-')[1].strip())
    workday.make_event()