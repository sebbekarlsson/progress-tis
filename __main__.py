from tis.ProgressSession import ProgressSession
from pyfiglet import Figlet


figlet = Figlet(font='slant')
progress_session = ProgressSession()

while progress_session.login() is False:
    print('Wrong password or username!')

print(figlet.renderText('TIS-Progress'))

progress_session.handle_commands()
