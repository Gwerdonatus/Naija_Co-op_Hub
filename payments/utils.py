import requests
from django.conf import settings

def initialize_payment(email, amount, reference):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": int(amount * 100),  # Convert to kobo
        "reference": reference,
        "callback_url":"http://127.0.0.1:8000/payments/verify/"
    }
    url = f"{settings.PAYSTACK_ENDPOINT}/transaction/initialize"
    response = requests.post(url, json=data, headers=headers)
    
    return response.json()



import requests
from django.conf import settings

# A dictionary mapping bank codes to their display names (if needed)
BANK_CODES = {
    "044": "Access Bank Nigeria Plc",
    "050": "Ecobank Nigeria",
    "084": "Enterprise Bank Plc",
    "070": "Fidelity Bank Plc",
    "011": "First Bank of Nigeria Plc",
    "214": "First City Monument Bank",
    "058": "Guaranty Trust Bank Plc",
    "301": "Jaiz Bank",
    "082": "Keystone Bank Ltd",
    "014": "Mainstreet Bank Plc",
    "076": "Skye Bank Plc",
    "039": "Stanbic IBTC Plc",
    "232": "Sterling Bank Plc",
    "032": "Union Bank Nigeria Plc",
    "033": "United Bank for Africa Plc",
    "215": "Unity Bank Plc",
    "035": "WEMA Bank Plc",
    "057": "Zenith Bank International",
    "101": "Providus Bank",
    "104": "PARALLEX BANK LIMITED",
    "303": "LOTUS BANK LIMITED",
    "105": "PREMIUM TRUST BANK LTD",
    "106": "SIGNATURE BANK LTD",
    "103": "GLOBUS BANK",
    "102": "TITAN TRUST BANK",
    "067": "Polaris Bank",
    "107": "OPTIMUS BANK LTD",
    "068": "Standard Chartered Bank",
    "100": "Suntrust Bank",
}

def create_paystack_subaccount(business_name, bank_code, account_number, percentage_charge=5, description=""):
    """
    Creates a subaccount on Paystack for the seller.
    bank_code: should be the bank code selected from the dropdown.
    """
    url = f"{settings.PAYSTACK_ENDPOINT}/subaccount"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "business_name": business_name,
        "settlement_bank": bank_code,  # directly use the bank code
        "account_number": account_number,
        "percentage_charge": percentage_charge,  # commission percentage, if applicable
        "description": description,
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data.get("status") and data.get("data"):
        # Return the subaccount code from Paystack
        return data["data"].get("subaccount_code")
    else:
        raise Exception("Paystack subaccount creation failed: " + data.get("message", "Unknown error"))
