"""
train_models.py — Loan Default Risk Prediction
=================================================
ROOT CAUSE FIX (diagnosed 2026-04-19):
  - rate_of_interest is NaN for ~80% of defaulters in the raw dataset.
  - fillna(median) gave ALL defaulters the SAME median interest rate.
  - Models learned "median interest = default signal" (spurious correlation).
  - Feature importance: rate_of_interest was 93% in XGBoost, 76% in RF.
  - RESULT: Models ignored income/credit score entirely.

FIX:
  1. Drop rate_of_interest completely (contaminated by NaN pattern).
  2. Add ltv_ratio (loan / property_value) — a real risk signal used by banks.
  3. Add monthly_payment_burden = loan / (income * term) to encode affordability.
  4. Reduce model complexity (depth, scale_pos_weight) to prevent overfitting.
  5. Use calibrated class_weight to avoid both extremes (stuck at 1% or 99%).
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

DATA_PATH  = r"C:\Users\hp\Downloads\archive\Loan_Default.csv"
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# ── 1. Load data ──────────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv(DATA_PATH)
print(f"  Shape: {df.shape}  |  Default rate: {df['Status'].mean()*100:.1f}%")

# ── 2. Clean — handle NaN BEFORE creating engineered features ─────────────────
print("Cleaning...")
# Drop rate_of_interest — it's NaN for the majority of defaulters,
# creating a spurious NaN-pattern signal that dominates all models.
if 'rate_of_interest' in df.columns:
    df = df.drop(columns=['rate_of_interest'])
    print("  [DROPPED] rate_of_interest (NaN-contaminated, was 93% importance)")

# Drop ID before anything
if 'ID' in df.columns:
    df = df.drop(columns=['ID'])

# Fill remaining numeric NaN with median, categorical with 'Unknown'
df.fillna(df.median(numeric_only=True), inplace=True)
cat_cols = df.select_dtypes(include="object").columns
df[cat_cols] = df[cat_cols].fillna("Unknown")

df["is_business_loan"] = (df["business_or_commercial"] == "b/c").astype(int)

# One-hot encode categoricals
df = pd.get_dummies(df, drop_first=True)

# Clean column names (xgboost dislikes <, >, [, ])
df.columns = df.columns.str.replace(r'[<>\[\]]', '', regex=True)

# ── 3. Feature Engineering ────────────────────────────────────────────────────
print("Engineering features...")
# income in dataset is MONTHLY (median ~$5,760/mo)
df["loan_income_ratio"]        = df["loan_amount"] / (df["income"] + 1)
df["ltv_ratio"]                = df["loan_amount"] / (df["property_value"] + 1)   # Loan-to-Value
df["monthly_payment_burden"]   = df["loan_amount"] / (df["income"] * df["term"] + 1) # Affordability

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna(df.median(numeric_only=True), inplace=True)

# ── 4. Feature selection ──────────────────────────────────────────────────────
# FIX: Drop raw income, loan_amount, property_value as standalone features.
# Reason: These are all already encoded in the ratio features below.
#   income       → captured by loan_income_ratio, monthly_payment_burden, dtir1
#   loan_amount  → captured by loan_income_ratio, ltv_ratio, monthly_payment_burden
#   property_value → captured by ltv_ratio
# Keeping both raw values AND their derivatives causes multicollinearity in LR,
# which causes the sign of the income coefficient to invert (+risk instead of -risk).
# The fix: use ONLY ratio features so income's effect flows correctly.
selected_features = [
    'Credit_Score',
    'term',
    'loan_income_ratio',     # loan / monthly_income  → lower = safer
    'ltv_ratio',             # loan / property_value  → lower = safer
    'monthly_payment_burden',# loan / (income * term) → lower = safer
    'dtir1',                 # total_debts / income   → lower = safer
    'is_business_loan'
]

X = df[selected_features]
y = df["Status"]
print(f"  Features: {selected_features}")
print(f"  Class balance — Safe: {(y==0).sum():,}  Default: {(y==1).sum():,}")

# ── 5. Split ──────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 6. Preprocessing pipeline ─────────────────────────────────────────────────
# Log-scale the skewed ratio features; passthrough the rest
log_features  = ['loan_income_ratio', 'ltv_ratio', 'monthly_payment_burden']
pass_features = ['Credit_Score', 'term', 'dtir1', 'is_business_loan']

preprocessor = ColumnTransformer(transformers=[
    ('log',  FunctionTransformer(np.log1p, validate=True), log_features),
    ('pass', 'passthrough',                                  pass_features),
])

# ── 7. Train models ───────────────────────────────────────────────────────────

def evaluate(name, pipeline, X_te, y_te):
    preds  = pipeline.predict(X_te)
    probs  = pipeline.predict_proba(X_te)[:, 1]
    auc    = roc_auc_score(y_te, probs)
    report = classification_report(y_te, preds, target_names=["Safe","Default"], digits=3)
    print(f"\n  [{name}] AUC={auc:.4f}")
    print(report)

# --- Logistic Regression ---
print("\nTraining Logistic Regression...")
lr_pipeline = Pipeline([
    ('pre',    preprocessor),
    ('scaler', StandardScaler()),
    # C=0.1: stronger L2 regularization to prevent any remaining multicollinearity from
    # inflating coefficient signs. Lower C = stronger penalty = more cautious weights.
    ('model',  LogisticRegression(max_iter=2000, C=0.1, class_weight='balanced')),
])
lr_pipeline.fit(X_train, y_train)
evaluate("LR", lr_pipeline, X_test, y_test)

# --- KNN ---
print("\nTraining KNN...")
knn_pipeline = Pipeline([
    ('pre',    preprocessor),
    ('scaler', StandardScaler()),
    ('model',  KNeighborsClassifier(n_neighbors=7, weights='distance')),
])
knn_pipeline.fit(X_train, y_train)
evaluate("KNN", knn_pipeline, X_test, y_test)

# --- Random Forest ---
print("\nTraining Random Forest...")
# Using raw class_weight='balanced_subsample' for better generalization
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,         # Shallower = less overfitting to interest-rate artifact
    max_features='sqrt',
    min_samples_leaf=10,
    class_weight='balanced_subsample',
    random_state=42,
    n_jobs=-1,
)
rf_pipeline = Pipeline([('pre', preprocessor), ('model', rf)])
rf_pipeline.fit(X_train, y_train)
evaluate("RF", rf_pipeline, X_test, y_test)

# Print RF feature importances
feat_names_log  = [f"log({f})" for f in log_features]
feat_names_pass = pass_features
all_feat_names  = feat_names_log + feat_names_pass
print("  RF Feature Importances:")
for fname, imp in sorted(zip(all_feat_names, rf.feature_importances_), key=lambda x:-x[1]):
    print(f"    {fname:<35} {imp:.4f}  {'|'*int(imp*100)}")

# --- XGBoost ---
print("\nTraining XGBoost...")
# scale_pos_weight = natural class ratio (no extra multiplier).
# Lower colsample_bytree forces it to use non-dominant features.
spw = (y_train == 0).sum() / (y_train == 1).sum()
print(f"  scale_pos_weight = {spw:.2f}")
xgb = XGBClassifier(
    n_estimators=300,
    max_depth=5,          # Shallower: less memorization
    learning_rate=0.05,
    colsample_bytree=0.6,
    subsample=0.8,
    scale_pos_weight=spw,  # Natural ratio, no amplification
    eval_metric='logloss',
    random_state=42,
)
xgb_pipeline = Pipeline([('pre', preprocessor), ('model', xgb)])
xgb_pipeline.fit(X_train, y_train)
evaluate("XGB", xgb_pipeline, X_test, y_test)

print("  XGB Feature Importances:")
for fname, imp in sorted(zip(all_feat_names, xgb.feature_importances_), key=lambda x:-x[1]):
    print(f"    {fname:<35} {imp:.4f}  {'|'*int(imp*100)}")

# ── 8. Save ───────────────────────────────────────────────────────────────────
print(f"\nSaving models to: {MODELS_DIR}")
os.makedirs(MODELS_DIR, exist_ok=True)
pickle.dump(lr_pipeline,  open(os.path.join(MODELS_DIR, "logistic.pkl"), "wb"))
pickle.dump(knn_pipeline, open(os.path.join(MODELS_DIR, "knn.pkl"),      "wb"))
pickle.dump(rf_pipeline,  open(os.path.join(MODELS_DIR, "rf.pkl"),       "wb"))
pickle.dump(xgb_pipeline, open(os.path.join(MODELS_DIR, "xgb.pkl"),      "wb"))
print("All 4 models saved successfully!")
