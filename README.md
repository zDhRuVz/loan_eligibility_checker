# Loan Default Risk Prediction System

A full-stack machine learning application that predicts the risk of loan default based on financial parameters.

## Architecture
- **Backend**: FastAPI (Python) - Hosted on Render
- **Frontend**: React + Vite + Tailwind CSS - Hosted on Vercel

---

## 🚀 Deployment Guide

### 1. Backend (Render)
1. **Create a New Web Service** on Render.
2. **Connect your Repository** (or use the `backend` subdirectory if it's a monorepo).
3. **Environment Settings**:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - `ALLOWED_ORIGINS`: `https://your-frontend-domain.vercel.app` (or `*` for testing)
   - `PYTHON_VERSION`: `3.11.0`

### 2. Frontend (Vercel)
1. **Create a New Project** on Vercel.
2. **Configure Project**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
3. **Environment Variables**:
   - `VITE_API_URL`: `https://your-backend-url.onrender.com` (Use the URL provided by Render)
4. **Deploy**: Vercel will automatically run `npm run build` and deploy the `dist` folder.

---

## 🛠️ Local Development

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run server: `uvicorn app:app --reload`

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Create a `.env` file with `VITE_API_URL=http://localhost:8000`
4. Run dev: `npm run dev`

---

## 📊 Models Included
- Logistic Regression
- KNN (K-Nearest Neighbors)
- Random Forest
- XGBoost (Extreme Gradient Boosting)
