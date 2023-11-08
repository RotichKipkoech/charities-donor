import requests
import base64
from datetime import datetime

def get_access_token():
    consumer_key = "6oUYc6pxKSx1qZNOfML2hcAnpAPndeVq"
    consumer_secret = "T3fmQgKGAkb6rZjl"
    api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))

    return r.json()['access_token']

def initiate_stk_push(phone_number, amount):
    access_token = get_access_token()

    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    business_short_code = "303506"
    lipa_na_mpesa_online_passkey = "71bc94670907e8ebd110827d8e6908c5a92ef2ee09502b0c3c9db9d2632d762a"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lipa_na_mpesa_online_password = base64.b64encode(
        f"{business_short_code}{lipa_na_mpesa_online_passkey}{timestamp}".encode()
    ).decode('utf-8')

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": lipa_na_mpesa_online_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://charities-donor.onrender.com",
        "AccountReference": "Charity",
        "TransactionDesc": "Donation"
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)

    return response.json()
