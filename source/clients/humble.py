'''
    inspired by https://github.com/MestreLion/humblebundle
'''

from typing import Iterator
import re
import json

import requests
from requests.cookies import RequestsCookieJar

from ..constants import Service, Validation
from secrets import HUMBLE_AUTH_COOKIE, HUMBLE_CSRF_COOKIE


list_from_page = '''
(function() {
    var l = [];
    $("div.js-library-holder div.js-subproducts-holder div.subproduct-selector div.text-holder > h2").each(
        function(i, el) { l.push(el.textContent) }
    );
    return l
})();
'''


DOMAIN = 'www.humblebundle.com'
BASE_URL = 'https://' + DOMAIN
KEYS_URL = BASE_URL + '/home/keys'
ORDER_URL = BASE_URL + '/api/v1/order/'

KEYS_RE = re.compile(r'^.*gamekeys\s*=\s*(\[.*\])', re.MULTILINE)
PLATFORM_FILTER = {'linux', 'mac', 'windows'}


class Connector:

    def __init__(self):
        expires = int(HUMBLE_AUTH_COOKIE.split('|')[1]) + 730 * 24 * 60 * 60
        jar = RequestsCookieJar()
        jar.set(
            '_simpleauth_sess',
            HUMBLE_AUTH_COOKIE,
            version = 0,
            port = None,
            domain = DOMAIN,
            path = '/',
            secure = True,
            expires = expires,
            discard = False,
            comment = None,
            comment_url = None,
            rest={}
        )
        jar.set('csrf_cookie', HUMBLE_CSRF_COOKIE)
        self.cookies = jar

    def call_api(self, url, method='GET'):
        return requests.request(method, url, cookies=self.cookies)

    def get_list(self) -> Iterator[dict]:
        resp = self.call_api(KEYS_URL).text
        keys = json.loads(KEYS_RE.search(resp).groups()[0])
        distinct = set()
        for key in keys:
            resp = self.call_api(ORDER_URL + key).json()
            for g in resp['subproducts']:
                key = g['machine_name']
                if any(d['platform'] in PLATFORM_FILTER for d in g['downloads']) and key not in distinct:
                    yield {'service': Service.HUMBLE, 'key': key,
                            'name': g['human_name'], 'validation': Validation.TODO}
                    distinct.add(key)
