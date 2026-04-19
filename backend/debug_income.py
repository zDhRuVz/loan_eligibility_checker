"""Debug: show all features passed to model at each income level"""
import pickle, os
import numpy as np
import pandas as pd

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
lr = pickle.load(open(os.path.join(MODELS_DIR, "logistic.pkl"), "rb"))
xgb = pickle.load(open(os.path.join(MODELS_DIR, "xgb.pkl"), "rb"))

LOAN = 200000
TERM = 360
MONTHLY_DEBTS = 1000
PROP_VAL = 250000
CREDIT = 700

print(f"{'Income(A)':>12} | {'LIR':>6} | {'LTV':>6} | {'Burden':>8} | {'DTI':>6} | {'LR':>6} | {'RF':>6} | {'XGB':>6}")
print("-" * 80)

for income_annual in [30000, 50000, 80000, 100000, 150000, 200000, 300000, 500000, 1_000_000]:
    income_monthly = income_annual / 12.0
    lir = LOAN / (income_monthly + 1)
    ltv = LOAN / (PROP_VAL + 1)
    burden = LOAN / (income_monthly * TERM + 1)
    monthly_mortgage_est = LOAN / TERM
    dtir1 = ((MONTHLY_DEBTS + monthly_mortgage_est) / max(income_monthly, 1.0)) * 100.0

    row = pd.DataFrame([{
        'Credit_Score': float(CREDIT),
        'term': float(TERM),
        'loan_income_ratio': lir,
        'ltv_ratio': ltv,
        'monthly_payment_burden': burden,
        'dtir1': dtir1,
        'is_business_loan': 0
    }])

    lr_risk = lr.predict_proba(row)[0][1] * 100
    xgb_risk = xgb.predict_proba(row)[0][1] * 100

    from sklearn.ensemble import RandomForestClassifier
    rf = pickle.load(open(os.path.join(MODELS_DIR, "rf.pkl"), "rb"))
    rf_risk = rf.predict_proba(row)[0][1] * 100

    print(f"{income_annual:>12,} | {lir:>6.1f} | {ltv:>6.3f} | {burden:>8.4f} | {dtir1:>5.1f}% | {lr_risk:>5.1f}% | {rf_risk:>5.1f}% | {xgb_risk:>5.1f}%")

print()
print("LR Coefficients:")
coefs = lr.named_steps['model'].coef_[0]
log_feats = ['loan_income_ratio', 'ltv_ratio', 'monthly_payment_burden']
pass_feats = ['Credit_Score', 'term', 'dtir1', 'is_business_loan']
feat_names = [f"log({f})" for f in log_feats] + pass_feats
for name, coef in sorted(zip(feat_names, coefs), key=lambda x: -abs(x[1])):
    direction = "+risk" if coef > 0 else "-risk"
    print(f"  {name:<30} {coef:>+.4f}  ({direction})")
