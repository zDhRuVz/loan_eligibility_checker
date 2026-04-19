import requests
import json

url = "http://127.0.0.1:10000/predict"
# Profile matching Row 0 (Status=1)
payload = {
    "income": 20880, 
    "loan_amount": 116500, 
    "credit_score": 758, 
    "property_value": 118000,
    "rate_of_interest": 4.0, # Approximate median
    "term": 360,
    "model_name": "Logistic Regression"
}

try:
    response = requests.post(url, json=payload)
    print("LR Results:")
    print(json.dumps(response.json(), indent=2))
    
    payload["model_name"] = "Random Forest"
    response = requests.post(url, json=payload)
    print("\nRF Results:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
