import requests
import xml.etree.ElementTree as ET
import re
from lxml import html
import getpass
from .urls import urls


class ProgressSession(object):

    def __init__(self):
        self.base_url = 'https://progress.thorengruppen.se/'
        self.s = requests.Session()
        self.COMMANDS =\
        [
            'courses',
            'assignments'
        ]

    def courses(self):
        r = self.s.get(
            self.base_url + self.courses_url,
            allow_redirects=True
        )
        root = html.fromstring(r.text)
        courses = root.xpath(".//div[@class='well'][1]/table/tr/td[3]")
        for course in courses:
            print(course.text)
    
    
    def assignments(self):
        r = self.s.get(
            self.base_url + self.assignments_url,
            allow_redirects=True
        )
        root = html.fromstring(r.text)
        assignments = root.xpath(".//div[@class='well'][1]/table/tr")
        for assignment in assignments:
            title = assignment.find('.//td[1]/a').text
            status = assignment.find('.//td[5]').text
            
            print('{} -> {}'.format(title, status))


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

        return self.authed

    def handle_commands(self):
        cmd = ''
        while cmd != 'exit':
            cdm = input('> ')
            
            if cdm in self.COMMANDS:
                result = getattr(self, cdm)()
            else:
                print('No such command')
