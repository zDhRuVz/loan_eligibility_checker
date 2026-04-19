import requests

url = 'http://127.0.0.1:10000/predict'
payload = {
    'income': 50000, 
    'loan_amount': 200000, 
    'credit_score': 700, 
    'property_value': 250000,
    'rate_of_interest': 4.0, 
    'term': 360,
    'monthly_debts': 1000,
    'is_business_loan': False,
    'model_name': 'XGBoost'
}

for inc in [30000, 50000, 100000, 200000, 500000, 1000000]:
    payload['income'] = inc
    try:
        r = requests.post(url, json=payload).json()
        print(f"Income: {inc:7} | LR: {r['comparisons']['Logistic Regression']:5.1f} | RF: {r['comparisons']['Random Forest']:5.1f} | XGB: {r['comparisons']['XGBoost']:5.1f} | LIR: {r['loan_income_ratio']}")
    except Exception as e:
        print("Error:", e)
