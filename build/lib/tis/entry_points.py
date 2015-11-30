from tis.ProgressSession import ProgressSession


psession = ProgressSession()


def login():
    return psession.login()
