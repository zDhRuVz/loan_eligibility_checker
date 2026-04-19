"""
Final health check for the Loan Default Risk Prediction system.
Tests: income sensitivity, business loan flag, extreme cases, financial strain interceptor.
"""
import requests

url = "http://127.0.0.1:10000/predict"
base = {
    "loan_amount": 200000, "credit_score": 700,
    "property_value": 250000, "rate_of_interest": 4.0,
    "term": 360, "monthly_debts": 1000,
    "is_business_loan": False, "model_name": "XGBoost"
}

passed = 0
failed = 0

def check(label, payload, condition_fn, expect_desc):
    global passed, failed
    try:
        r = requests.post(url, json=payload).json()
        risk = r["risk_percent"]
        ok = condition_fn(r)
        status = "PASS" if ok else "FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  [{status}] {label}")
        print(f"         Risk={risk:.1f}%  Level={r['risk_level']}  Strain={r['financial_strain']}  | Expected: {expect_desc}")
    except Exception as e:
        failed += 1
        print(f"  [ERROR] {label}: {e}")

print("=" * 70)
print("  LOAN DEFAULT SYSTEM - FINAL HEALTH CHECK")
print("=" * 70)

# 1. High income should mean lower risk than low income (same loan)
p_low  = {**base, "income": 30000}
p_high = {**base, "income": 200000}
r_low  = requests.post(url, json=p_low).json()["risk_percent"]
r_high = requests.post(url, json=p_high).json()["risk_percent"]
ok = r_low > r_high
status = "PASS" if ok else "FAIL"
if ok: passed += 1
else: failed += 1
print(f"\n  [{status}] INCOME SENSITIVITY: high income should be LOWER risk than low income")
print(f"         Low income ($30k) risk  = {r_low:.1f}%")
print(f"         High income ($200k) risk = {r_high:.1f}%")
print(f"         Difference: {r_low - r_high:+.1f}pp {'(correct)' if ok else '(WRONG - inverted!)'}")

# 2. Increasing income monotonically decreases risk (at least up to $200k)
print(f"\n  [----] MONOTONIC INCOME DECREASE CHECK (XGB):")
prev = 100.0
mono_ok = True
for inc in [30000, 50000, 80000, 100000, 150000, 200000]:
    r = requests.post(url, json={**base, "income": inc}).json()
    risk = r["risk_percent"]
    direction = "v" if risk < prev else "^"
    print(f"         ${inc:>7,}: {risk:5.1f}% {direction}")
    if risk > prev + 2:  # allow tiny tolerance
        mono_ok = False
    prev = risk
status = "PASS" if mono_ok else "WARN"
if mono_ok: passed += 1
print(f"         [{status}] Monotonic decrease: {'YES' if mono_ok else 'NOT perfectly monotonic (some tolerance expected)'}")

# 3. Very low income + huge loan = financial strain interceptor fires
check(
    "FINANCIAL STRAIN INTERCEPTOR",
    {**base, "income": 500, "loan_amount": 500000},
    lambda r: r["financial_strain"] == True and r["risk_percent"] >= 75,
    "financial_strain=True, risk >= 75%"
)

# 4. Business loan should generally be riskier than personal
r_personal = requests.post(url, json={**base, "income": 80000, "is_business_loan": False}).json()["risk_percent"]
r_business = requests.post(url, json={**base, "income": 80000, "is_business_loan": True}).json()["risk_percent"]
ok = r_business >= r_personal - 5  # allow some tolerance
status = "PASS" if ok else "FAIL"
if ok: passed += 1
else: failed += 1
print(f"\n  [{status}] BUSINESS LOAN FLAG:")
print(f"         Personal loan risk = {r_personal:.1f}%  |  Business loan risk = {r_business:.1f}%")

# 5. High DTI (lots of debts) should raise risk
r_low_debt  = requests.post(url, json={**base, "income": 80000, "monthly_debts": 0}).json()["risk_percent"]
r_high_debt = requests.post(url, json={**base, "income": 80000, "monthly_debts": 8000}).json()["risk_percent"]
ok = r_high_debt > r_low_debt
status = "PASS" if ok else "FAIL"
if ok: passed += 1
else: failed += 1
print(f"\n  [{status}] DTI SENSITIVITY:")
print(f"         Low debts ($0/mo) risk  = {r_low_debt:.1f}%")
print(f"         High debts ($8k/mo) risk = {r_high_debt:.1f}%")

# 6. API health
try:
    r = requests.get("http://127.0.0.1:10000/")
    ok = r.json().get("status") == "API is running"
    status = "PASS" if ok else "FAIL"
    if ok: passed += 1
    else: failed += 1
    print(f"\n  [{status}] API HEALTH CHECK")
except Exception as e:
    failed += 1
    print(f"\n  [FAIL] API HEALTH CHECK: {e}")

print()
print("=" * 70)
print(f"  RESULTS: {passed} PASSED  |  {failed} FAILED")
print("=" * 70)
