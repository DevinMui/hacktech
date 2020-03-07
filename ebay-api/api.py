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
        self.credential = b64encode(f"{appId}:{certId}")
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

    def getUserAccessToken(self, code: str):
        self.code = code
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.credential}",
        }
        body = f"grant_type=authorization_code&code={self.code}&redirect_uri={self.redirectName}"
        tokenObj = post(self.url, data=body, headers=headers)
        now = datetime.now()
        if not tokenObj.ok:
            tokenObj.raise_for_status()

        token = tokenObj.json()
        self.accessToken = token["access_token"]
        self.tokenExpires = now + timedelta(seconds=token["expires_in"])
        self.refreshToken = token["refresh_token"]
        self.refreshExpires = now + timedelta(seconds=token["refresh_token_expires_in"])

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
    def get(self, uri: str, query: list, headers: dict = None):
        if datetime.now() < self.refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() < self.tokenExpires:
            self._refreshAccessToken()

        headers = headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.accessToken}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            }
        )

        res = get(self.url + uri + "&=".join(query), headers=headers)

        if not res.ok:
            res.raise_for_status()

        return res.json()

    def post(self, uri: str, body: dict, headers: dict = None):
        if datetime.now() < self.refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() < self.tokenExpires:
            self._refreshAccessToken()

        headers = headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.accessToken}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            }
        )

        res = post(self.url + uri, json=body, headers=headers)

        if not res.ok:
            res.raise_for_status()

        return res.json()

