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
        saveToJSON: bool = False,
    ):
        self.appId = appId
        self.certId = certId
        self.credential = b64encode((appId + ":" + certId).encode()).decode("utf-8")
        self.redirectName = redirectName
        self.scope = " ".join(scope)
        self.saveToJSON = saveToJSON
        self.env = env
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
    def getUserAccessToken(self, code: str):
        if self.saveToJSON:
            try:
                with open("user.json") as f:
                    data = json.load(f)
                    accessToken = data["access_token"]
                    tokenExpires = datetime.strptime(data["token_expires"], "%c")
                    refreshToken = data["refresh_token"]
                    refreshExpires = datetime.strptime(data["refresh_expires"], "%c")
                    return
            except Exception as e:
                pass

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
        accessToken = token["access_token"]
        tokenExpires = now + timedelta(seconds=token["expires_in"])
        refreshToken = token["refresh_token"]
        refreshExpires = now + timedelta(seconds=token["refresh_token_expires_in"])
        data = {
            "accessToken": accessToken,
            "tokenExpires": tokenExpires.strftime("%c"),
            "refreshToken": refreshToken,
            "refreshExpires": refreshExpires.strftime("%c"),
        }
        if self.saveToJSON:
            with open("user.json", "w") as f:
                json.dump(data, f)
        return data

    def _refreshAccessToken(self, token: dict):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.credential}",
        }
        body = f"grant_type=refresh_token&refresh_token={token['refreshToken']}&scope={self.scope}"

        tokenObj = post(
            self.url + "/identity/v1/oauth2/token", data=body, headers=headers
        )
        now = datetime.now()
        if not tokenObj.ok:
            tokenObj.raise_for_status()

        token = tokenObj.json()
        accessToken = token["access_token"]
        tokenExpires = now + timedelta(seconds=token["expires_in"])
        data = {
            "accessToken": accessToken,
            "tokenExpires": tokenExpires.strftime("%c"),
            "refreshToken": token["refreshToken"],
            "refreshExpires": token["refreshExpires"],
        }
        if self.saveToJSON:
            with open("user.json", "w") as f:
                json.dump(data, f)
        return data

    def getUser(self, token: dict = None):
        refreshExpires = datetime.strptime(token["refreshExpires"], "%c")
        tokenExpires = datetime.strptime(token["tokenExpires"], "%c")
        accessToken = token["accessToken"]
        refreshToken = token["refreshToken"]
        if datetime.now() > refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() > tokenExpires:
            self._refreshAccessToken(token)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {accessToken}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }

        res = (
            get(
                "https://apiz.sandbox.ebay.com/commerce/identity/v1/user",
                headers=headers,
            )
            if self.env == "SANDBOX"
            else get("https://apiz.ebay.com/commerce/identity/v1/user", headers=headers)
        )

        if not res.ok:
            print(res.text)
            res.raise_for_status()

        return res.json()

    # authenticated get/post requests
    def get(
        self, uri: str, query: list = None, token: dict = None, headers: dict = None
    ):
        refreshExpires = datetime.strptime(token["refreshExpires"], "%c")
        tokenExpires = datetime.strptime(token["tokenExpires"], "%c")
        accessToken = token["accessToken"]
        refreshToken = token["refreshToken"]
        if datetime.now() > refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() > tokenExpires:
            self._refreshAccessToken(token)

        reqHeaders = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {accessToken}",
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

    def post(self, uri: str, body: dict = {}, token: dict = None, headers: dict = None):
        refreshExpires = token["refreshExpires"].strptime("%c")
        tokenExpires = token["tokenExpires"].strptime("%c")
        accessToken = token["accessToken"]
        refreshToken = token["refreshToken"]
        if datetime.now() > refreshExpires:
            raise AuthException("Auth and refresh expired. Please login.")
        elif datetime.now() > tokenExpires:
            self._refreshAccessToken(token)

        reqHeaders = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {accessToken}",
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

