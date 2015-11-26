from tis.ProgressSession import ProgressSession

progress_session = ProgressSession()

while progress_session.login() is False:
    print('Wrong password or username!')

print('Login was successful!')
print('Welcome to progress!')

progress_session.handle_commands()