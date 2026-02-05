import requests
import os

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")

def send_sms(mobile, otp):
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"

        payload = f"variables_values={otp}&route=otp&numbers={mobile}"
        headers = {
            'authorization': FAST2SMS_API_KEY,
            'Content-Type': "application/x-www-form-urlencoded",
        }

        response = requests.post(url, data=payload, headers=headers)
        return response.json()

    except Exception as e:
        print("SMS sending failed:", e)
        return False
