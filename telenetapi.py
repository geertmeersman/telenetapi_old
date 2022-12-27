import json
import math
import requests

TELENET_BYTE_BASE = 1024

def display_bytes(n, base=TELENET_BYTE_BASE):
    if n <= 0:
        return f"0.00B"

    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    power = min(math.floor(math.log(n, base)), len(units))

    n /= base**power
    unit = units[power]
    return f"{n:4.2f}{unit}"


class TelenetSession(object):
    def __init__(self):
        self.s = requests.Session()
        self.s.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"

    def login(self, username, password):
        # Get OAuth2 state / nonce
        r = self.s.get(
            "https://api.prd.telenet.be/ocapi/oauth/userdetails",
            headers={
                "x-alt-referer": "https://www2.telenet.be/nl/klantenservice/#/pages=1/menu=selfservice"
            },
            timeout=10,
        )

        # Return if already authenticated
        if r.status_code == 200:
            return

        assert r.status_code == 401
        state, nonce = r.text.split(",", maxsplit=2)

        # Log in
        r = self.s.get(
            f'https://login.prd.telenet.be/openid/oauth/authorize?client_id=ocapi&response_type=code&claims={{"id_token":{{"http://telenet.be/claims/roles":null,"http://telenet.be/claims/licenses":null}}}}&lang=nl&state={state}&nonce={nonce}&prompt=login',
            timeout=10,
        )
        r = self.s.post(
            "https://login.prd.telenet.be/openid/login.do",
            data={
                "j_username": username,
                "j_password": password,
                "rememberme": True,
            },
            timeout=10,
        )
        assert r.status_code == 200

        self.s.headers["X-TOKEN-XSRF"] = self.s.cookies.get("TOKEN-XSRF")

    def userdetails(self):
        r = self.s.get(
            "https://api.prd.telenet.be/ocapi/oauth/userdetails",
            headers={
                "x-alt-referer": "https://www2.telenet.be/nl/klantenservice/#/pages=1/menu=selfservice",
            },
        )
        assert r.status_code == 200
        return r.json()

    def internet(self):
        r = self.s.get(
            "https://api.prd.telenet.be/ocapi/public/?p=internetusage,internetusagereminder",
            headers={
                "x-alt-referer": "https://www2.telenet.be/nl/klantenservice/#/pages=1/menu=selfservice",
            },
            timeout=10,
        )
        assert r.status_code == 200
        return r.json()

    def mobile(self):
        r = self.s.get(
            "https://api.prd.telenet.be/ocapi/public/?p=mobileusage",
            headers={
                "x-alt-referer": "https://www2.telenet.be/nl/klantenservice/#/pages=1/menu=selfservice",
            },
            timeout=10,
        )
        assert r.status_code == 200
        return r.json()
