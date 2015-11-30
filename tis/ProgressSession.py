import requests
import xml.etree.ElementTree as ET
import re
from lxml import html
import getpass
from .urls import urls
from pyfiglet import Figlet
import time
import sys
from .Messager import Messager


class ProgressSession(object):

    def __init__(self):
        self.base_url = 'https://progress.thorengruppen.se/'
        self.s = requests.Session()
        self.COMMANDS =\
        [
            'courses',
            'assignments',
            'sendmsg'
        ]
        self.figlet = Figlet(font='slant')


    def courses(self):

        print(self.figlet.renderText('Courses'))

        r = self.s.get(
            self.base_url + self.courses_url,
            allow_redirects=True
        )
        root = html.fromstring(r.text)
        courses = root.xpath(".//div[@class='well'][1]/table/tr/td[3]")
        for course in courses:
            print(course.text)


    def sendmsg(self, args):

        print(self.figlet.renderText('Messages'))

        fails = 0
        for i in range(0, int(args[3])):
            #r = self.s.post(
            #    self.base_url + '/tis/schools/{}/Message/Send'\
            #            .format(self.school_name),
            #    data={
            #        'Recipients[0].Id': args[0],
            #        'Recipients[0].ActorType': 'User',
            #        'Recipients[0].Name': 'undefined',
            #        'SendMail': 'false',
            #        'Subject': args[1],
            #        'Body': args[2]
            #    },
            #    allow_redirects=True
            #)
            #print(r.text.encode('utf-8'))
            messager = Messager(base_url=self.base_url, school_name=self.school_name, session=self.s, reciever=args[0], subject=args[1], body=args[2])
            try:
                messager.start()
            except RuntimeError:
                print('FAILED TO SEND MESSAGE')
    
    def assignments(self):

        print(self.figlet.renderText('Assignments'))

        r = self.s.get(
            self.base_url + self.assignments_url,
            allow_redirects=True
        )
        root = html.fromstring(r.text)
        assignments = root.xpath(".//div[@class='well'][1]/table/tr")
        information = root.xpath(
            """
            .//div[@class='panel panel-default'][1]
            //div[@class='row']
            //div[@class='col-md-10']
            """
        )
        
        for info in information:
            title = info.find(".//label/b").text.rstrip()
            data = info.find(".//div[@class='col-md-4']").text\
                    .rstrip('\r\n')\
                    .replace(' ', '')

            print('{}: {}'.format(title, data))

        for assignment in assignments:
            title = assignment.find('.//td[1]/a').text
            status = assignment.find('.//td[5]').text
            
            print('{}: {}'.format(title, status))


    def login(self):
        self.username = input('Username: ')
        self.password = getpass.getpass('Password: ')

        request_1 = self.s.get(
            urls['login']['login']
        )
        root = ET.fromstring(request_1.text)
        
        self.token_form = root\
                .find(".//*[@name='__RequestVerificationToken']")\
                .get('value')

        request_2 = self.s.post(
            urls['login']['authenticate'],
            data={
                'UserName': self.username,
                'Password': self.password,
                'EnableSSO': 'false',
                '__RequestVerificationToken': self.token_form,
                'submit': 'submit'
            }
        )
        root_2 = ET.fromstring(request_2.text)
        
        try:
            self.token_auth = root_2.find(".//*[@name='wresult']").get('value')
        except AttributeError:
            return False

        request_3 = self.s.post(
            urls['login']['progress'],
            data={
                'wa': 'wsignin1.0',
                'wresult': self.token_auth,
                'wctx': 'm=0&amp;id=passive&amp;ru=%2f',
                'submit': 'submit'
            }
        )
        root_3 = html.fromstring(request_3.text)
        self.authed = ('Kurser' in request_3.text)

        if self.authed:
            self.school_name = re.search(r'schools/(.*)/', request_3.text)\
                    .group(1).split('/')[0]
            self.courses_url = root_3.xpath('.//a[text()="Kurser"]')[0]\
                    .get('href')
            self.assignments_url = root_3\
                    .xpath('.//a[text()="Inlämningsuppgifter"]')[0]\
                    .get('href')
            self.messages_url = root_3\
                    .xpath('.//a[text()="Meddelanden"]')[0]\
                    .get('href')

        return self.authed

    def handle_commands(self):
        args = ''
        while args != 'exit':
            args = input('> ')
            args = args.split(' ')

            cmd = args[0]
            args.pop(0)

            if cmd in self.COMMANDS:
                if len(args) > 0:
                    result = getattr(self, cmd)(args)
                else:
                    result = getattr(self, cmd)()
            else:
                print('No such command')
