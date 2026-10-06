import requests
from config import API_URL, API_TOKEN

headers = {"Accept": "application/json"}

if API_TOKEN.strip():
    headers["Authorization"] = f"Token {API_TOKEN.strip()}"

print("Testing Django Current Notice API...")
print("URL:", API_URL)

try:
    response = requests.get(
        API_URL,
        headers=headers,
        timeout=8
    )

    print("HTTP Status:", response.status_code)
    print("Response:")
    print(response.text)

except requests.RequestException as exc:
    print("Request failed:")
    print(exc)
