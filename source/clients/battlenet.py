import webbrowser
from typing import List
import hashlib
from datetime import date

import requests
from requests.auth import HTTPBasicAuth

from secrets import BLIZZARD_KEY, BLIZZARD_SECRET

REGION = 'eu'
AUTH_URL = 'https://{}.battle.net/oauth/authorize'.format(REGION)
TOKEN_URL = 'https://{}.battle.net/oauth/token'.format(REGION)
REDIRECT_URI = 'https%3A%2F%2Flocalhost%2Foauth2callback'
OTHER_REDIRECT_URI = r'https://localhost/oauth2callback'
SCOPE = ''


AUTH_PATH = 'blizzard_auth.json'


class Connector:

    @staticmethod
    def browser_auth():
        print(
            'Opening your browser to allow you to log in.\n'
            'After completing the login you will be redirected to a broken url.\n'
            'Copy the code parameter from the URL and paste it here.'
        )
        hashtoken = hashlib.sha256((date.today().strftime('%Y%m%d') + BLIZZARD_SECRET).encode('utf-8')).hexdigest()
        auth_info = {
            'client_id': BLIZZARD_KEY,
            'scope': SCOPE,  #	The space separated scope values you wish to request from the player.
            'state': hashtoken,
            'redirect_uri':	REDIRECT_URI,
            'response_type': 'code',
        }
        webbrowser.open('{}?{}'.format(
            AUTH_URL,
            '&'.join('{}={}'.format(k, v) for k, v in auth_info.items())
        ))
        login_code = input("insert code: ")
        print('login code "{}"'.format(login_code))
        token_info = {
             'code': login_code,
             'redirect_uri': OTHER_REDIRECT_URI,
             'grant_type': 'authorization_code',
             'client_id': BLIZZARD_KEY,
             'client_secret': BLIZZARD_SECRET,
             'scope': SCOPE
        }
        #resp = requests.post(TOKEN_URL, data=token_info, auth=HTTPBasicAuth(BLIZZARD_KEY, BLIZZARD_SECRET))
        resp = requests.post(TOKEN_URL, data=token_info)
        with open(AUTH_PATH, 'w') as f:
            f.write(resp.text)
        return resp

    def __init__(self):
        pass

    def get_list(self) -> List[dict]:
        # there is not an API for this right now :/
        return NotImplemented


