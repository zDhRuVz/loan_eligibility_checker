import requests

url = "http://127.0.0.1:10000/predict"
payload = {
    "income": 50000,
    "loan_amount": 200000,
    "credit_score": 750,
    "property_value": 300000,
    "rate_of_interest": 3.5,
    "term": 360,
    "model_name": "Random Forest"
}

try:
    response = requests.post(url, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
