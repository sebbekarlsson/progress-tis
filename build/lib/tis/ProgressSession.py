import requests
import xml.etree.ElementTree as ET
import re
from lxml import html as _html
import getpass
from .urls import urls
from .config import config
from pyfiglet import Figlet
import time
import sys
from .Messager import Messager
import html.parser


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
        self.htmlParser = html.parser.HTMLParser()

    def courses(self):

        print(self.figlet.renderText('Courses'))

        r = self.s.get(
            self.base_url + self.courses_url,
            allow_redirects=True
        )
        root = _html.fromstring(r.text)
        courses = root.xpath(".//div[@class='well'][1]/table/tr/td[3]")
        
        return courses

    def sendmsg(self, reciever, subject, body, times=1):

        print(self.figlet.renderText('Messages'))

        fails = 0
        for i in range(0, int(times)):
            messager = Messager(
                base_url=self.base_url,
                school_name=self.school_name,
                session=self.s, reciever=reciever,
                subject=subject,
                body=body
            )
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
        root = _html.fromstring(r.text)
        assignments = root.xpath(".//div[@class='well'][1]/table/tr")
        information = root.xpath(
            """
            .//div[@class='panel panel-default'][1]
            //div[@class='row']
            //div[@class='col-md-10']
            """
        )

        final_infos = []
        final_assignments = []

        for info in information:
            title = info.find(".//label/b").text.rstrip()
            data = info.find(".//div[@class='col-md-4']").text\
                    .rstrip('\r\n')\
                    .replace(' ', '')
            
            
            inf = {}
            inf['title'] = title
            inf['text'] = data
            
            final_infos.append(inf)
        
        for assignment in assignments:
            title = assignment.find('.//td[1]/a').text
            status = assignment.find('.//td[5]').text
            
            ass = {}
            ass['title'] = title
            ass['text'] = status
            
            final_assignments.append(ass)

        return {'infos': final_infos, 'assignments': final_assignments}
        
           
    def login(self):
        self.username = config['login']['username']
        self.password = config['login']['password']

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
        root_3 = _html.fromstring(request_3.text)
        self.authed = ('Kurser' in request_3.text)

        if self.authed:
            self.school_name = re.search(r'schools/(.*)/', request_3.text)\
                    .group(1).split('/')[0]
            self.courses_url = root_3.xpath('.//a[text()="Kurser"]')[0]\
                    .get('href')
            self.assignments_url = root_3\
                    .xpath(self.htmlParser.unescape('.//a[text()="Inl&auml;mningsuppgifter"]'))[0]\
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
