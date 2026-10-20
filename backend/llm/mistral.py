import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

api_url = str(os.getenv("API_URL")).strip()
token = str(os.getenv("TOKEN")).strip()
headers = {"Authorization": f"Bearer {token}"}

# Hugging Face API
def query(payload):
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()  
    return response.json()