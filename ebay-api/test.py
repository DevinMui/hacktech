import argparse
from api import API

parser = argparse.ArgumentParser()
parser.add_argument("code")
args = parser.parse_args()
code = args.code

auth = {
    "appid": "DevinMui-hacktech-SBX-c69eabc60-dfb59748",
    "certid": "SBX-69eabc603212-8754-46a7-b707-7d89",
    "devid": "111cbf40-3850-4007-92dd-31c83fe74249",
    "redirecturi": "https://devinmui.github.io",
    "runame": "Devin_Mui-DevinMui-hackte-mlytz",
    "scope": [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/buy.offer.auction",
        "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly",
    ],
}
api = API(auth["appid"], auth["certid"], auth["runame"], auth["scope"])

api.getUserAccessToken(code)

uri = "/buy/browse/v1/item_summary/search"
query = ["q=iphone"]

num = 110510301167
_id = f"v1|{num}|0"
uri = "/buy/browse/v1/item/" + _id
item = api.get(uri)
print(item)
