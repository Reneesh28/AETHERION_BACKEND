import pyotp
from SmartApi import SmartConnect

API_KEY = "lxoG0C8s"
CLIENT_ID = "AABO952598"
MPIN = "2005"
TOTP_SECRET = "PSGZCB6IELF77IMQMFY5P2276A"

try:
    api = SmartConnect(api_key=API_KEY)

    totp = pyotp.TOTP(TOTP_SECRET).now()

    session = api.generateSession(CLIENT_ID, MPIN, totp)

    if session.get("status"):
        print("✅ Login Successful")

        feed_token = api.getfeedToken()
        print("✅ Feed Token Generated:", feed_token)

    else:
        print("❌ Login Failed:", session)

except Exception as e:
    print("❌ Error:", e)