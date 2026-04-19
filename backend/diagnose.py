"""
DIAGNOSTIC SCRIPT - Loan Default Model
Goal: Find why XGBoost fires 74% on a normal profile and LR is stuck at 1%
"""
import pickle, os, json
import numpy as np
import pandas as pd

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_PATH  = r"C:\Users\hp\Downloads\archive\Loan_Default.csv"

# ── Load models ──────────────────────────────────────────────────────────────
models = {}
for name, fname in [("LR","logistic.pkl"),("KNN","knn.pkl"),("RF","rf.pkl"),("XGB","xgb.pkl")]:
    with open(os.path.join(MODELS_DIR, fname),"rb") as f:
        models[name] = pickle.load(f)

COLS = ['income','loan_amount','Credit_Score','property_value',
        'rate_of_interest','term','loan_income_ratio']

def predict_all(row_dict, label=""):
    df = pd.DataFrame([row_dict])
    print(f"\n{'─'*55}")
    print(f"  {label}")
    lir = row_dict['loan_income_ratio']
    print(f"  income={row_dict['income']:,.0f}  loan={row_dict['loan_amount']:,.0f}  LIR={lir:.1f}x  score={row_dict['Credit_Score']}")
    print(f"{'─'*55}")
    for name, m in models.items():
        prob = m.predict_proba(df)[0][1] * 100
        flag = m.predict(df)[0]
        bar  = "█" * int(prob / 5)
        print(f"  {name:<5}  {prob:5.1f}%  [{bar:<20}]  class={flag}")

# ════════════════════════════════════════════════════════
# 1. CHECK DATASET INCOME SCALE
# ════════════════════════════════════════════════════════
print("\n" + "═"*55)
print("  STEP 1 — Dataset Income Distribution")
print("═"*55)
df_raw = pd.read_csv(DATA_PATH)
print(df_raw[["income","loan_amount","Status"]].describe().round(0))
print(f"\nDefault rate: {df_raw['Status'].mean()*100:.1f}%")
print(f"Income median: {df_raw['income'].median():,.0f}")
print(f"Income max: {df_raw['income'].max():,.0f}")
print(f"Income min: {df_raw['income'].min():,.0f}")

# ════════════════════════════════════════════════════════
# 2. TEST REAL DATASET ROWS (known defaults vs safe)
# ════════════════════════════════════════════════════════
print("\n" + "═"*55)
print("  STEP 2 — Predict on Real Dataset Rows")
print("═"*55)

df_proc = df_raw.copy()
df_proc.fillna(df_proc.median(numeric_only=True), inplace=True)
df_proc["loan_income_ratio"] = df_proc["loan_amount"] / (df_proc["income"] + 1)
df_proc.replace([np.inf, -np.inf], np.nan, inplace=True)
df_proc.fillna(df_proc.median(numeric_only=True), inplace=True)

defaults = df_proc[df_proc["Status"]==1].head(3)
safes    = df_proc[df_proc["Status"]==0].head(3)

for i, row in defaults.iterrows():
    predict_all({c: row[c] for c in COLS}, f"REAL DEFAULT  row={i}")
for i, row in safes.iterrows():
    predict_all({c: row[c] for c in COLS}, f"REAL SAFE     row={i}")

# ════════════════════════════════════════════════════════
# 3. THE APP.PY INFERENCE PATH (as it currently runs)
# ════════════════════════════════════════════════════════
print("\n" + "═"*55)
print("  STEP 3 — App.py Inference Path (annual→monthly split)")
print("═"*55)
# Normal profile: $79,200/yr income, $166,500 loan
income_annual   = 79200
loan_amount     = 166500
income_monthly  = income_annual / 12.0           # 6600  → passed as 'income'
lir_annual      = loan_amount / (income_annual + 1)   # 2.1   → current app.py
lir_monthly     = loan_amount / (income_monthly + 1)  # 25.2  (what training may expect)

print(f"\n  income_annual={income_annual}  income_monthly={income_monthly:.0f}")
print(f"  LIR (using annual income): {lir_annual:.2f}x")
print(f"  LIR (using monthly income): {lir_monthly:.2f}x")
print(f"\n  What the dataset's median income looks like: {df_raw['income'].median():,.0f}")
print(f"  → If dataset uses MONTHLY income, we should pass monthly to the model.")
print(f"  → If dataset uses ANNUAL income,  we should pass annual to the model.")

# Predict using MONTHLY income + MONTHLY LIR  (what training trained on if monthly)
row_monthly = {
    'income': income_monthly, 'loan_amount': loan_amount,
    'Credit_Score': 685, 'property_value': 238000,
    'rate_of_interest': 3.99, 'term': 144,
    'loan_income_ratio': lir_monthly
}
predict_all(row_monthly, "NORMAL PROFILE — income=monthly, LIR=monthly")

# Predict using ANNUAL income + ANNUAL LIR  (what training trained on if annual)
row_annual = {
    'income': income_annual, 'loan_amount': loan_amount,
    'Credit_Score': 685, 'property_value': 238000,
    'rate_of_interest': 3.99, 'term': 144,
    'loan_income_ratio': lir_annual
}
predict_all(row_annual, "NORMAL PROFILE — income=annual, LIR=annual")

# ════════════════════════════════════════════════════════
# 4. XGB FEATURE IMPORTANCES
# ════════════════════════════════════════════════════════
print("\n" + "═"*55)
print("  STEP 4 — XGB Feature Importances (after log-preprocessing)")
print("═"*55)
xgb_core = models["XGB"].named_steps["model"]
pre       = models["XGB"].named_steps["pre"]
log_cols  = ['income','loan_amount','property_value','loan_income_ratio']
pass_cols = ['Credit_Score','rate_of_interest','term']
transformed_cols = log_cols + pass_cols
imp = xgb_core.feature_importances_
for col, score in sorted(zip(transformed_cols, imp), key=lambda x: -x[1]):
    bar = "█" * int(score * 200)
    print(f"  {col:<22}  {score:.4f}  {bar}")

print("\n" + "═"*55)
print("  STEP 5 — RF Feature Importances")
print("═"*55)
rf_core = models["RF"].named_steps["model"]
imp_rf  = rf_core.feature_importances_
for col, score in sorted(zip(transformed_cols, imp_rf), key=lambda x: -x[1]):
    bar = "█" * int(score * 200)
    print(f"  {col:<22}  {score:.4f}  {bar}")

# ════════════════════════════════════════════════════════
# 6. SWEEP: income vs risk (to find tipping points)
# ════════════════════════════════════════════════════════
print("\n" + "═"*55)
print("  STEP 6 — Income Sweep (log-scale, fixed loan=$166500)")
print("═"*55)
print(f"  {'Income':>10}  {'LR':>6}  {'KNN':>6}  {'RF':>6}  {'XGB':>6}")
for inc in [3000, 10000, 20000, 40000, 79200, 120000, 200000]:
    inc_m = inc / 12.0
    lir   = inc / (inc + 1)   # NOTE: using raw income (will test both)
    row = pd.DataFrame([{
        'income': inc_m, 'loan_amount': 166500,
        'Credit_Score': 685, 'property_value': 238000,
        'rate_of_interest': 3.99, 'term': 144,
        'loan_income_ratio': 166500 / (inc_m + 1)
    }])
    probs = {n: round(m.predict_proba(row)[0][1]*100,1) for n,m in models.items()}
    print(f"  {inc:>10,}  {probs['LR']:>5.1f}%  {probs['KNN']:>5.1f}%  {probs['RF']:>5.1f}%  {probs['XGB']:>5.1f}%")

print("\n  ✓ Diagnostic complete.\n")
