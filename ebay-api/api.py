import json
from base64 import b64encode
from requests import get, post
from datetime import datetime, timedelta


class AuthException(Exception):
    pass


class API:
    def __init__(
        self,
        appId: str,
        certId: str,
        redirectName: str,
        scope: list,
        env: str = "SANDBOX",
    ):
        self.appId = appId
        self.certId = certId
        self.credential = b64encode((appId + ":" + certId).encode()).decode("utf-8")
        self.redirectName = redirectName
        self.scope = " ".join(scope)
        self.url = (
            "https://api.sandbox.ebay.com"
            if env is "SANDBOX"
            else "https://api.ebay.com"
        )

    def getAppToken(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.credential}",
        }

        body = f"grant_type=client_credentials&scope={self.scope}"
        tokenObj = post(
            self.url + "/identity/v1/oauth2/token", data=body, headers=headers
        )

        if not tokenObj.ok:
            tokenObj.raise_for_status()

        self.token = tokenObj.json()

    # function gets the user oauth token
    # option to save the token to a json file to reduce # api requests
    def getUserAccessToken(self, code: str, saveToJSON=True):
        if saveToJSON:
            try:
                with open("user.json") as f:
                    data = json.load(f)
                    self.accessToken = data["access_token"]
                    self.tokenExpires = datetime.strptime(data["token_expires"], "%c")
                    self.refreshToken = data["refresh_token"]
                    self.refreshExpires = datetime.strptime(
                        data["refresh_expires"], "%c"
                    )
                    return
            except Exception as e:
                pass

        print("grabbing")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.credential}",
        }
        body = f"grant_type=authorization_code&code={code}&redirect_uri={self.redirectName}"
        tokenObj = post(
            self.url + "/identity/v1/oauth2/token", data=body, headers=headers
        )
        now = datetime.now()
        if not tokenObj.ok:
            tokenObj.raise_for_status()

        token = tokenObj.json()
        self.accessToken = token["access_token"]
        self.tokenExpires = now + timedelta(seconds=token["expires_in"])
        self.refreshToken = token["refresh_token"]
        self.refreshExpires = now + timedelta(seconds=token["refresh_token_expires_in"])
        if saveToJSON:
            data = {
                "access_token": self.accessToken,
                "token_expires": self.tokenExpires.strftime("%c"),
                "refresh_token": self.refreshToken,
                "refresh_expires": self.refreshExpires.strftime("%c"),
            }
            with open("user.json", "w") as f:
                json.dump(data, f)

    def _refreshAccessToken(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.credential}",
        }
        body = f"grant_type=refresh_token&refresh_token={self.refreshToken}&scope={self.scope}"

        tokenObj = post(self.url, data=body, headers=headers)
        now = datetime.now()
        if not tokenObj.ok:
            tokenObj.raise_for_status()

        token = tokenObj.json()
        self.accessToken = token["access_token"]
        self.tokenExpires = now + timedelta(seconds=token["expires_in"])

    # authenticated get/post requests
    def get(self, uri: str, query: list = None, headers: dict = None):
        if datetime.now() > self.refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() > self.tokenExpires:
            self._refreshAccessToken()

        reqHeaders = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.accessToken}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }
        if headers is not None:
            headers = {**headers, **reqHeaders}
        else:
            headers = reqHeaders

        if query:
            res = get(self.url + uri + "?" + "&".join(query), headers=headers)
        else:
            res = get(self.url + uri, headers=headers)

        if not res.ok:
            print(res.text)
            res.raise_for_status()

        return res.json()

    def post(self, uri: str, body: dict = {}, headers: dict = None):
        if datetime.now() > self.refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() > self.tokenExpires:
            self._refreshAccessToken()

        reqHeaders = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.accessToken}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }
        if headers is not None:
            headers = {**headers, **reqHeaders}
        else:
            headers = reqHeaders

        res = post(self.url + uri, json=body, headers=headers)

        if not res.ok:
            res.raise_for_status()

        return res.json()

