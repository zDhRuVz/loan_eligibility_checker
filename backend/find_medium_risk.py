import pickle
import pandas as pd
import numpy as np

DATA_PATH = r"C:\Users\hp\Downloads\archive\Loan_Default.csv"

# Load models
with open('models/rf.pkl', 'rb') as f:
    rf = pickle.load(f)

print("Loading data...")
df = pd.read_csv(DATA_PATH)
df.fillna(df.median(numeric_only=True), inplace=True)
df["loan_income_ratio"] = df["loan_amount"] / (df["income"] + 1)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna(df.median(numeric_only=True), inplace=True)

selected_features = [
    'income',
    'loan_amount',
    'Credit_Score',
    'property_value',
    'rate_of_interest',
    'term',
    'loan_income_ratio'   
]

X = df[selected_features]

# Predict all and find a few with ~ 50%
probs = rf.predict_proba(X)[:, 1] * 100
medium_indices = np.where((probs >= 40) & (probs <= 60))[0]

if len(medium_indices) > 0:
    for idx in medium_indices[:3]:
        print(f"Index: {idx}, Prob: {probs[idx]:.2f}%")
        print(X.iloc[idx].to_dict())
else:
    print("Could not find any row with 40-60%. Try 30-70%")
    medium_indices = np.where((probs >= 30) & (probs <= 70))[0]
    for idx in medium_indices[:3]:
        print(f"Index: {idx}, Prob: {probs[idx]:.2f}%")
        print(X.iloc[idx].to_dict())
