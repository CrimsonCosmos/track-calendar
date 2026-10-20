"""One-time Strava authorization. Run this on YOUR computer (not in chat):

    python3 strava_mcp/authorize.py

It prints a refresh token to your terminal. Save it as the STRAVA_REFRESH_TOKEN
secret in your Claude environment settings. Never paste it into chat.
"""
import getpass
import json
import os
import urllib.parse
import urllib.request

SCOPE = "read,activity:read_all,activity:write"

cid = os.environ.get("STRAVA_CLIENT_ID") or input("Client ID: ").strip()
secret = os.environ.get("STRAVA_CLIENT_SECRET") or getpass.getpass("Client secret: ").strip()

url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode({
    "client_id": cid, "response_type": "code", "redirect_uri": "http://localhost",
    "approval_prompt": "force", "scope": SCOPE,
})
print("\n1. Open this URL, log in, and click Authorize:\n\n" + url + "\n")
print("2. The browser will then fail to load http://localhost/?code=XXXX&... That is expected.")
print("   Copy the value after 'code=' (up to the next '&') from the address bar.\n")
code = input("Paste code: ").strip()

req = urllib.request.Request("https://www.strava.com/oauth/token", data=urllib.parse.urlencode({
    "client_id": cid, "client_secret": secret, "code": code, "grant_type": "authorization_code",
}).encode())
tok = json.load(urllib.request.urlopen(req))
granted = tok.get("scope", "")
print("\nAuthorized as:", tok["athlete"].get("firstname"), tok["athlete"].get("lastname"))
print("\nSTRAVA_CLIENT_ID     =", cid)
print("STRAVA_REFRESH_TOKEN =", tok["refresh_token"])
print("(STRAVA_CLIENT_SECRET is the secret you already have.)")
print("\nNote: make sure the 'View data about your private activities' and 'Upload your activities'"
      " boxes were checked on the Strava page, or reads/writes will fail.")
