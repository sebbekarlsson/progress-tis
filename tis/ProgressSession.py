import requests
import xml.etree.ElementTree as ET
import re
from lxml import html


class ProgressSession(object):

    def __init__(self):
        self.base_url = 'https://progress.thorengruppen.se/'
        self.s = requests.Session()
        self.COMMANDS =\
        [
            'courses'
        ]

    def courses(self):
        r = self.s.get(
            self.base_url + self.courses_url,
            allow_redirects=True
        )

        print(r.text.encode('utf-8'))
        

    def login(self):
        self.username = input('Username: ')
        self.password = input('Password: ')

        request_1 = self.s.get(
            "https://progress.thorengruppen.se"
        )

        root = ET.fromstring(request_1.text)
        self.token_form = root.find(".//*[@name='__RequestVerificationToken']").get('value')

        request_2 = self.s.post(
            "https://login.thorengruppen.se/account/signin?ReturnUrl=%2fissue%2fwsfed%3fwa%3dwsignin1.0%26wtrealm%3dhttps%253a%252f%252fprogress.thorengruppen.se%252f%26wctx%3drm%253d0%2526id%253dpassive%2526ru%253d%25252f%26wct%3d2015-11-26T21%253a08%253a06Z&wa=wsignin1.0&wtrealm=https%3a%2f%2fprogress.thorengruppen.se%2f&wctx=rm%3d0%26id%3dpassive%26ru%3d%252f&wct=2015-11-26T21%3a08%3a06Z",
            data={
                'UserName': self.username,
                'Password': self.password,
                'EnableSSO': 'false',
                '__RequestVerificationToken': self.token_form,
                'submit': 'submit'
            },
            allow_redirects=True
        )

        root_2 = ET.fromstring(request_2.text)

        try:
            self.token_auth = root_2.find(".//*[@name='wresult']").get('value')
        except AttributeError:
            return False

        request_3 = self.s.post(
            "https://progress.thorengruppen.se/",
            data={
                'wa': 'wsignin1.0',
                'wresult': self.token_auth,
                'wctx': 'm=0&amp;id=passive&amp;ru=%2f',
                'submit': 'submit'
            },
            allow_redirects=True
        )
        
        root_3 = html.fromstring(request_3.text)

        self.authed = ('Kurser' in request_3.text)

        if self.authed:
            self.school_name = re.search(r'schools/(.*)/', request_3.text).group(1).split('/')[0]
            self.courses_url = e = root_3.xpath('.//a[text()="Kurser"]')[0].get('href')

        return self.authed

    def handle_commands(self):
        cmd = ''
        while cmd != 'exit':
            cdm = input('> ')
            
            if cdm in self.COMMANDS:
                result = getattr(self, cdm)()
                print('EXECUTED')
            else:
                print('No such command')
