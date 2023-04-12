import copy
from typing import Optional

import requests
from requests import Response

from thilde_event import ThildeEvent

base_header = {
    "Host": "api.tihlde.org",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.7,nb;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Length": "2",
    "Origin": "null",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
    "Content-Type": "application/json",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}
_thilde_url = "https://api.tihlde.org/"
_register_endpoint_template = "/events/{}/registrations/"
_login_endpoint = "auth/login/"


class Credentials:
    def __init__(self, username: str, password: str):
        self.password = password
        self.username = username



def get_token(credentials: Credentials) -> Optional[str]:
    payload = {'password': credentials.password, 'user_id': credentials.username}
    response = requests.post(_thilde_url + _login_endpoint, json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        return None


class RequestFactory:

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.header: {str: str} = copy.deepcopy(base_header)

    def test_credentials(self) -> bool:
        try:
            self.refresh_token()
            return True
        except Exception:
            return False

    def refresh_token(self):
        maybe_token = get_token(self.credentials)
        if maybe_token is None:
            raise Exception()
        else:
            self.header["x-csrf-token"] = maybe_token

    def send_registration_request(self, event: ThildeEvent) -> Response:
        url = _thilde_url + _register_endpoint_template.format(event.id)
        return requests.post(url, headers=self.header, json={})
