from tis.ProgressSession import ProgressSession
import argparse


psession = ProgressSession()
parser = argparse.ArgumentParser()


def login():
    if psession.login():
        print('AUTHENTICATED')
    else:
        print('WRONG PASSWORD OR USERNAME')


def get_courses():
    psession.login()
    courses = psession.courses()
    
    for course in courses:
        print(course.text)


def get_assignments():
    psession.login()
    data = psession.assignments()
    
    infos = data['infos']
    assignments = data['assignments']
    
    print('*---INFORMATION---*')
    for info in infos:
        print('{}: {}'.format(info['title'], info['text']).encode('utf-8'))
    
    print('*---ASSIGNMENTS---*')
    for ass in assignments:
        print('{}: {}'.format(ass['title'], ass['text']).encode('utf-8'))


def send_msg():
    parser.add_argument('-r')
    parser.add_argument('-s')
    parser.add_argument('-b')
    parser.add_argument('-t')
    
    args = parser.parse_args()
    
    psession.login()
    psession.sendmsg(args.r, args.s, args.b, args.t)


def get_messages():
    parser.add_argument('-d')
    parser.add_argument('-m')
    args = parser.parse_args()

    psession.login()
    
    delete = False

    if args.d:
        delete = True

    messages = psession.get_messages(args.m, delete)


def user_search():
    parser.add_argument('-s')
    args = parser.parse_args()
    
    psession.login()
    
    print(psession.user_search(args.s))
