import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from exceptions.CalendarNameNotFoundException import CalendarNameNotFoundException
from exceptions.CalendarNoEventException import CalendarNoEventException
from exceptions.CalendarNoDescriptionException import CalendarNoDescriptionException

import configparser
import datetime
import re
import gammu
from time import sleep
from random import randint


class Calendar:
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    APPLICATION_NAME = 'smsrdv'
    CLIENT_SECRET_FILE = None
    RE_TIME=r'T\d\d:\d\d'
    RE_PHONE_NUMBER=r'^\d{10}$|^\+33\d{9}$'


    def __init__(self, name='primary', template='default.tpl', config_file='default.ini', client_secret_file='client_secret.json'):
        Calendar.CLIENT_SECRET_FILE = client_secret_file
        self.credentials = Calendar.getCredentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=self.http)
        self.events = None
        self.perso = {}
        try:
            with open(template, 'r') as fic:
                self.template = fic.read()
        except:
            print('Unable to read template file', template)
            exit(1)
        try:
            self.name = self.getIdFromName(name)
        except CalendarNameNotFoundException:
            print('Calendar "{}" not found'.format(name))
            exit(2)

        config = configparser.ConfigParser()
        config.read(config_file)
        for key in config['perso']:
            self.perso[key] = config['perso'][key]

        self.gammu = gammu.StateMachine()
        self.gammu.ReadConfig()
        self.gammu.Init()
        if self.gammu.GetSecurityStatus() == 'PIN':
            print('On entre le PIN')
            self.gammu.EnterSecurityCode('PIN', self.perso['pin'])
        else:
            print('Rien à faire')

        print('Attente détection SIM')
        sleep(10)


    @staticmethod
    def getCredentials():
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.smsrdv')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'credential.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(Calendar.CLIENT_SECRET_FILE, Calendar.SCOPES)
            flow.user_agent = Calendar.APPLICATION_NAME
            credentials = tools.run_flow(flow, store) # Last parameters noauth_local_webserver ?
            print('Storing credentials to ' + credential_path)
        return credentials


    @staticmethod
    def getFutureDate(days):
        time = datetime.datetime.today() + datetime.timedelta(days) 
        time = time.replace(hour=0, minute=0, second=0, microsecond=0)
        return time.isoformat() + 'Z'


    def getIdFromName(self, name):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['summary'] == name:
                    return calendar_list_entry['id']
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        raise CalendarNameNotFoundException()


    def getTomorrowEvents(self):
        timeMin = Calendar.getFutureDate(days=1)
        timeMax = Calendar.getFutureDate(days=2)
        eventsResult = self.service.events().list(
            calendarId=self.name, timeMin=timeMin, timeMax=timeMax, singleEvents=True,
            orderBy='startTime').execute()
        self.events = eventsResult.get('items', [])

        if not self.events:
            raise CalendarNoEventException()


    def sendSMS(self):
        for event in self.events:
            date = event['start'].get('dateTime', event['start'].get('date'))
            time = re.search(Calendar.RE_TIME, date).group(0)[1:]
            name = event['summary']
            if 'description' in event:
                phoneNumber = event['description'].split('\n')[0].replace(' ', '')
                if re.search(Calendar.RE_PHONE_NUMBER, phoneNumber) is None:
                    print('Format de numéro de téléphone invalide :', phoneNumber)
                    continue
                msg = self.template.replace('[heure]', time) \
                                   .replace('[nom]', name) \
                                   .replace('[montel]', self.perso['phone_number']) \
                                   .replace('[signature]', self.perso['signature'])
                msgToSend = {
                    'Text' : msg,
                    'SMSC' : {'Location' : 1},
                    'Number' : phoneNumber,
                }
                print('- On envoie le message :')
                print(msg)
                self.gammu.SendSMS(msgToSend)
                delay = randint(3, 15)
                print('Attente de : {}s'.format(delay))
                sleep(delay)
            else:
                print('Événement "{}" sans description !'.format(name))



if __name__ == '__main__':
    c = Calendar('Test')
    c.getTomorrowEvents()
    c.sendSMS()
