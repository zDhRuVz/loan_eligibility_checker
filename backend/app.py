import os
import pickle
import numpy as np
import pandas as pd
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

print(f"DEBUG: sys.version: {sys.version}")

# Initialize FastAPI app
app = FastAPI(title="Loan Default Risk Prediction API")

# Setup CORS using environment variable (default to * if empty or missing)
allowed_origins_str = os.getenv("ALLOWED_ORIGINS") or "*"
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
if not allowed_origins:
    allowed_origins = ["*"]
print(f"DEBUG: Setting allowed origins to: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models (Pipelines for LR/KNN, Raw for RF/XGB)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Pre-initialize models 
lr_model = knn_model = rf_model = xgb_model = None
model_errors = {}

def load_pkl(filename):
    path = os.path.join(MODELS_DIR, filename)
    try:
        if not os.path.exists(path):
            return None, f"File not found at {path}"
        with open(path, "rb") as f:
            return pickle.load(f), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}"

# Load models independently
lr_model, err = load_pkl("logistic.pkl")
if err: model_errors["lr"] = err

knn_model, err = load_pkl("knn.pkl")
if err: model_errors["knn"] = err

rf_model, err = load_pkl("rf.pkl")
if err: model_errors["rf"] = err

xgb_model, err = load_pkl("xgb.pkl")
if err: model_errors["xgb"] = err

model_map = {
    "Logistic Regression": lr_model,
    "KNN": knn_model,
    "Random Forest": rf_model,
    "XGBoost": xgb_model
}

class PredictRequest(BaseModel):
    income: float
    loan_amount: float
    credit_score: float
    property_value: float
    rate_of_interest: float
    term: float
    model_name: str
    monthly_debts: float = 0.0
    is_business_loan: bool = False

import sklearn
import xgboost as xgb_lib

@app.get("/")
@app.get("/status")
def status():
    # Gather file metadata
    sizes = {}
    if os.path.exists(MODELS_DIR):
        for f in os.listdir(MODELS_DIR):
            if f.endswith(".pkl"):
                sizes[f] = f"{os.path.getsize(os.path.join(MODELS_DIR, f)) / (1024*1024):.2f} MB"

    return {
        "status": "API is running",
        "allowed_origins": allowed_origins,
        "models_loaded": {
            "lr": lr_model is not None,
            "knn": knn_model is not None,
            "rf": rf_model is not None,
            "xgb": xgb_model is not None
        },
        "model_errors": model_errors,
        "model_file_sizes": sizes,
        "sys_info": {
            "python": sys.version,
            "platform": sys.platform,
            "scikit-learn": sklearn.__version__,
            "xgboost": xgb_lib.__version__
        }
    }

@app.post("/predict")
def predict_risk(data: PredictRequest):
    try:
        selected_model = model_map.get(data.model_name)
        if selected_model is None:
            # Fallback to XGBoost if possible
            selected_model = xgb_model or lr_model
            if selected_model is None:
                raise ValueError(f"Model '{data.model_name}' (and fallbacks) are not loaded on server. Errors: {model_errors}")

        # 1. Type Casting & Normalization
        income_annual = float(data.income)
        loan_amount = float(data.loan_amount)
        credit_score = float(max(500, min(900, data.credit_score)))
        property_value = float(data.property_value)
        rate_of_interest = float(data.rate_of_interest)
        term = float(data.term)
        monthly_debts = float(data.monthly_debts)
        is_business_loan = int(data.is_business_loan)
        
        income_monthly = income_annual / 12.0
        
        # 2. Safe Feature Engineering
        model_loan_income_ratio = loan_amount / (income_monthly + 1.0)
        ltv_ratio = loan_amount / (property_value + 1.0)
        monthly_payment_burden = loan_amount / (income_monthly * term + 1.0)
        annual_lir = loan_amount / (income_annual + 1.0)
        
        monthly_mortgage_est = loan_amount / term if term > 0 else 0
        dtir1 = ((monthly_debts + monthly_mortgage_est) / (max(income_monthly, 1.0))) * 100.0
        
        # 3. Build features DataFrame
        features_df = pd.DataFrame([{
            'Credit_Score':           credit_score,
            'term':                   term,
            'loan_income_ratio':      model_loan_income_ratio,
            'ltv_ratio':              ltv_ratio,
            'monthly_payment_burden': monthly_payment_burden,
            'dtir1':                  dtir1,
            'is_business_loan':       is_business_loan
        }])
        
        # 4. Pipeline/Model Execution
        classification = int(selected_model.predict(features_df)[0])
        risk_probability = float(selected_model.predict_proba(features_df)[0][1] * 100)
        
        # UX Improvement: Clamp Probability
        risk_probability = max(1, min(99, risk_probability))
        
        # 5. Common Sense Interceptor
        financial_strain = False
        if annual_lir > 100:
            risk_probability = max(risk_probability, 75.0)
            financial_strain = True
        elif annual_lir > 40:
            risk_probability = max(risk_probability, 40.0)
            financial_strain = True
        
        # 6. Categorize Risk
        if risk_probability < 20:
            risk_level = "Low"
        elif 20 <= risk_probability <= 50:
            risk_level = "Medium"
        else:
            risk_level = "High"
            
        # 7. Generate comparisons
        comparisons = {}
        for m_name, m_model in model_map.items():
            if m_model is not None:
                prob = m_model.predict_proba(features_df)[0][1] * 100
                comparisons[m_name] = round(max(1, min(99, prob)), 2)
            else:
                comparisons[m_name] = "LOAD_ERROR"

        return {
            "risk_percent": round(risk_probability, 2),
            "risk_level": risk_level,
            "classification_output": classification,
            "model_used": data.model_name if data.model_name in model_map else "Selected",
            "comparisons": comparisons,
            "loan_income_ratio": round(annual_lir, 2),
            "financial_strain": financial_strain
        }
        
    except Exception as e:
        import traceback
        error_msg = f"ERROR: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
