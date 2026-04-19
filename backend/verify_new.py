import requests
import json

url = "http://127.0.0.1:10000/predict"

# TEST 1: Extreme low income — should trigger the interceptor
case1 = {
    "income": 1200,
    "loan_amount": 200000,
    "credit_score": 750,
    "property_value": 250000,
    "rate_of_interest": 3.5,
    "term": 360,
    "model_name": "XGBoost"
}
r1 = requests.post(url, json=case1)
d1 = r1.json()
print("=== LOW INCOME (income=1200/yr, loan=200k) ===")
print("  Risk:    ", d1.get("risk_percent"), "%", d1.get("risk_level"))
print("  LIR:     ", d1.get("loan_income_ratio"), "x")
print("  Strain:  ", d1.get("financial_strain"))

# TEST 2: Normal profile
case2 = {
    "income": 79200,
    "loan_amount": 166500,
    "credit_score": 685,
    "property_value": 238000,
    "rate_of_interest": 3.99,
    "term": 144,
    "model_name": "XGBoost"
}
r2 = requests.post(url, json=case2)
d2 = r2.json()
print("\n=== NORMAL CASE (income=79200, loan=166500) ===")
print("  Risk:    ", d2.get("risk_percent"), "%", d2.get("risk_level"))
print("  LIR:     ", d2.get("loan_income_ratio"), "x")
print("  Strain:  ", d2.get("financial_strain"))
print("  Comparisons:")
for k, v in d2.get("comparisons", {}).items():
    print("   ", k, "->", v, "%")

# TEST 3: Known default profile from dataset
case3 = {
    "income": 20880,
    "loan_amount": 116500,
    "credit_score": 758,
    "property_value": 118000,
    "rate_of_interest": 4.0,
    "term": 360,
    "model_name": "Logistic Regression"
}
r3 = requests.post(url, json=case3)
d3 = r3.json()
print("\n=== KNOWN DEFAULT PROFILE (income=20880, loan=116500) ===")
print("  Risk:    ", d3.get("risk_percent"), "%", d3.get("risk_level"))
print("  LIR:     ", d3.get("loan_income_ratio"), "x")
print("  Comparisons:")
for k, v in d3.get("comparisons", {}).items():
    print("   ", k, "->", v, "%")
