import threading


class Messager (threading.Thread):
    def __init__(self, base_url, school_name, session, reciever, subject, body):
        threading.Thread.__init__(self)
        self.reciever = reciever
        self.subject = subject
        self.body = body
        self.s = session
        self.base_url = base_url
        self.school_name = school_name
    def run(self):
        try:
            r = self.s.post(
                self.base_url + 'tis/schools/{}/Message/Send'\
                        .format(self.school_name),
                data={
                    'Recipients[0].Id': self.reciever,
                    'Recipients[0].ActorType': 'User',
                    'Recipients[0].Name': 'undefined',
                    'SendMail': 'true',
                    'Important': 'true',
                    'Subject': self.subject,
                    'Body': self.body
                },
                allow_redirects=True
            )
            print(r.text.encode('utf-8'))
        except:
            print('COULD NOT SEND MESSAGE')
        
