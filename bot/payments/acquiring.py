import requests
from bot.config import TOKENS_DATA
BASE_URL = "https://acquiring.foreignpay.ru"
TOKEN = TOKENS_DATA["Digital_api"]
async def create_invoice(amount: int, description: str):

    endpoint = "/webhook/partner_sbp/transaction"

    # Request headers
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # Request payload
    payload = {
        "amount": amount,  # Amount in RUB (required)
        "description": description,  # Description (required)
    }

    try:
        # Make the POST request
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            json=payload
        )

        # Check if the request was successful
        return response.json() if response.status_code == 200 else Exception(f"Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

async def check_invoice_status(invoice_id: str):

    endpoint = f"/webhook/check_transaction"

    # Request headers
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "transaction_uuid": invoice_id,
    }

    try:
        # Make the POST request
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            json=payload
        )

        # Check if the request was successful
        return response.json() if response.status_code == 200 else Exception(f"Error: {response.status_code} - {response.text}") 

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

async def get_balance():
    
    endpoint = "/webhook/my_balance"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers
        )

        # Check if the request was successful
        return response.json() if response.status_code == 200 else Exception(f"Error: {response.status_code} - {response.text}") 

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

