import webbrowser
import requests
import json
from typing import List, Optional

from ..constants import Service, Validation

CLIENT_ID = "46899977096215655"
CLIENT_SECRET = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
AUTH_URL = "https://auth.gog.com/auth?client_id={}&redirect_uri=https%3A//embed.gog.com" \
               "/on_login_success%3Forigin%3Dclient&response_type=code&layout=client2".format(CLIENT_ID)
TOKEN_URL = "https://auth.gog.com/token"
REDIRECT_URL = "https://embed.gog.com/on_login_success?origin=client"
API_BASE = 'https://embed.gog.com'
CLIENT_VERSION = "1.2.17.9" # Just for their statistics
USER_AGENT = "GOGGalaxyClient/{} pygogapi/0.1".format(CLIENT_VERSION)

AUTH_PATH = 'gog_auth.json'


# TODO: gestire fallimento in tutte le richieste


class Connector:

    def gog_browser_auth(self):
        print(
            'Opening your browser to allow you to log in.\n'
            'After completing the login you will be redirected to a blank page.\n'
            'Copy the code from the URL and paste it here.'
        )
        webbrowser.open(AUTH_URL)
        login_code = input("insert code: ")
        auth_info = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": login_code,
            "redirect_uri": REDIRECT_URL
        }
        resp = requests.get(TOKEN_URL, params=auth_info).text
        with open(AUTH_PATH, 'w') as f:
            f.write(resp)
        self.auth = json.loads(resp)

    def refresh_token(self, auth: dict):
        params = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": auth["refresh_token"]
        }
        resp = requests.get(TOKEN_URL, params=params).text
        with open(AUTH_PATH, 'w') as f:
            f.write(resp)
        self.auth = json.loads(resp)

    def __init__(self):
        try:
            with open(AUTH_PATH, 'r') as f:
                auth = json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            self.gog_browser_auth()
        else:
            self.refresh_token(auth)

    def call_api(self, url: str, params: Optional[dict]=None, method: str='GET') -> dict:
        headers = {
            'User-Agent': USER_AGENT,
            'Authorization': 'Bearer ' + self.auth['access_token']
        }
        resp = requests.request(method, API_BASE + url, headers=headers, params=params)
        return resp.json()

    def get_list(self) -> List[dict]:
        games = self.call_api("/account/getFilteredProducts?mediaType=1")['products']
        for game in games:
            yield {'service': Service.GOG, 'key': str(game['id']), 'name': game['title'], 'validation': Validation.TODO}


