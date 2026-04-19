import { useState } from 'react';
import { Loader2, AlertCircle, Activity } from 'lucide-react';
import clsx from 'clsx';

export default function Predict() {
  const DEFAULTS = {
    income: 79200,
    loan_amount: 166500,
    credit_score: 685,
    property_value: 238000,
    rate_of_interest: 3.99,
    term: 144,
    monthly_debts: 0,
    is_business_loan: false
  };

  const [formData, setFormData] = useState({
    income: '',
    loan_amount: '',
    credit_score: '',
    property_value: '',
    rate_of_interest: '',
    term: '',
    monthly_debts: '',
    is_business_loan: false,
    model_name: 'XGBoost',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Live Loan-to-Income Ratio (computed on the fly from form fields)
  const liveIncome = formData.income === '' ? DEFAULTS.income : Number(formData.income);
  const liveLoan = formData.loan_amount === '' ? DEFAULTS.loan_amount : Number(formData.loan_amount);
  const liveLIR = liveIncome > 0 ? (liveLoan / liveIncome).toFixed(1) : null;

  const models = ['Logistic Regression', 'KNN', 'Random Forest', 'XGBoost'];

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    // Fallback and Payload Generation
    const payload = {
      income: formData.income === '' ? DEFAULTS.income : Number(formData.income),
      loan_amount: formData.loan_amount === '' ? DEFAULTS.loan_amount : Number(formData.loan_amount),
      credit_score: formData.credit_score === '' ? DEFAULTS.credit_score : Number(formData.credit_score),
      property_value: formData.property_value === '' ? DEFAULTS.property_value : Number(formData.property_value),
      rate_of_interest: formData.rate_of_interest === '' ? DEFAULTS.rate_of_interest : Number(formData.rate_of_interest),
      term: formData.term === '' ? DEFAULTS.term : Number(formData.term),
      monthly_debts: formData.monthly_debts === '' ? DEFAULTS.monthly_debts : Number(formData.monthly_debts),
      is_business_loan: formData.is_business_loan,
      model_name: formData.model_name
    };

    // Validation
    const numericFields = ['income', 'loan_amount', 'credit_score', 'property_value', 'rate_of_interest', 'term'];
    for (let field of numericFields) {
      if (payload[field] < 0) {
        setError("Inputs cannot be negative.");
        setLoading(false);
        return;
      }
    }
    if (payload.loan_amount === 0) {
      setError("Loan amount must be greater than zero.");
      setLoading(false);
      return;
    }

    try {
      const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      // No need to throw error now as we have a safe fallback
      const API_URL = `${BASE_URL}/predict`;
      
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch prediction");
      }

      const data = await response.json();
      // Artificial delay for smooth UI experience
      setTimeout(() => {
        setResult(data);
        setLoading(false);
      }, 600);
      
    } catch (err) {
      console.error(err);
      setError("Could not connect to the backend server. Make sure it is running.");
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch(level) {
      case 'Low': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30';
      case 'Medium': return 'text-orange-400 bg-orange-400/10 border-orange-400/30';
      case 'High': return 'text-red-400 bg-red-400/10 border-red-400/30';
      default: return 'text-slate-400 bg-slate-800';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
      {/* Form Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl">
        <h2 className="text-2xl font-bold mb-6">Enter Loan Details</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex justify-between">
                <span>Income (Annual)</span>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">Converted to monthly</span>
              </label>
              <input type="number" step="0.01" name="income" value={formData.income} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.income}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Loan Amount</label>
              <input type="number" step="0.01" name="loan_amount" value={formData.loan_amount} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.loan_amount}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex justify-between">
                <span>Credit Score</span>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">Range: 500-900</span>
              </label>
              <input type="number" name="credit_score" value={formData.credit_score} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.credit_score}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Property Value</label>
              <input type="number" step="0.01" name="property_value" value={formData.property_value} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.property_value}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Interest Rate (%)</label>
              <input type="number" step="0.01" name="rate_of_interest" value={formData.rate_of_interest} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.rate_of_interest}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Term (Months)</label>
              <input type="number" step="1" name="term" value={formData.term} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.term}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Total Monthly Debts ($)</label>
              <input type="number" step="0.01" name="monthly_debts" value={formData.monthly_debts} onChange={handleChange} placeholder={`e.g. ${DEFAULTS.monthly_debts}`}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition" />
            </div>

            <div className="space-y-2 flex flex-col justify-center">
              <label className="text-sm font-medium text-slate-300 mb-2">Loan Type</label>
              <label className="flex items-center space-x-3 cursor-pointer p-2 rounded-lg hover:bg-slate-800/50 transition border border-transparent hover:border-slate-700/50">
                <input type="checkbox" name="is_business_loan" checked={formData.is_business_loan} onChange={handleChange} 
                  className="w-5 h-5 rounded border-slate-700 bg-slate-800 text-blue-500 focus:ring-blue-500" />
                <span className="text-sm text-slate-300">This is a Business Loan</span>
              </label>
            </div>
            
          </div>
          
          <div className="pt-2">
            <label className="text-sm font-medium text-slate-300 mb-2 block">Select Model</label>
            <select name="model_name" value={formData.model_name} onChange={handleChange}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none">
              {models.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-red-400 bg-red-400/10 p-3 rounded-lg border border-red-500/20 text-sm">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          {/* Live Loan-to-Income Ratio indicator */}
          {liveLIR !== null && (
            <div className={clsx(
              "flex items-center justify-between text-sm px-4 py-2.5 rounded-lg border",
              Number(liveLIR) > 100
                ? 'bg-red-500/10 border-red-500/30 text-red-400'
                : Number(liveLIR) > 40
                  ? 'bg-orange-500/10 border-orange-500/30 text-orange-400'
                  : 'bg-slate-800/60 border-slate-700 text-slate-400'
            )}>
              <span>Loan-to-Income Ratio</span>
              <span className="font-bold tabular-nums">
                {liveLIR}x
                {Number(liveLIR) > 100 && <span className="ml-2 text-xs uppercase tracking-wider">⚠ Extreme</span>}
                {Number(liveLIR) > 40 && Number(liveLIR) <= 100 && <span className="ml-2 text-xs uppercase tracking-wider">⚠ High</span>}
              </span>
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full mt-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-all flex justify-center items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin w-5 h-5" /> : "Run Prediction"}
          </button>
        </form>
      </div>

      {/* Result Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl flex flex-col justify-center items-center text-center min-h-[400px]">
        {loading ? (
          <div className="flex flex-col items-center gap-4 text-slate-400 animate-pulse">
            <Loader2 className="w-12 h-12 animate-spin text-blue-500" />
            <p>Analyzing risk profile...</p>
          </div>
        ) : result ? (
          <div className="space-y-6 w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-2xl font-medium text-slate-300">Analysis Result</h3>
            
            <div className={clsx("p-8 rounded-2xl border flex flex-col items-center justify-center space-y-2 relative overflow-hidden", getRiskColor(result.risk_level))}>
              <span className="text-sm font-bold uppercase tracking-widest opacity-80 z-10">Risk Level</span>
              <span className="text-6xl font-black z-10 tracking-tight">{result.risk_level}</span>
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
            </div>

            <div className="grid grid-cols-2 gap-4">
               <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <span className="block text-slate-400 text-sm mb-1">Probability</span>
                  <span className="text-2xl font-bold">{result.risk_percent}%</span>
               </div>
               <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <span className="block text-slate-400 text-sm mb-1">Target Model</span>
                  <span className="text-lg font-bold text-blue-400">{result.model_used}</span>
               </div>
            </div>
            
            <p className="text-sm text-slate-500 mt-4">
              Classification flag: {result.classification_output === 1 ? 'Expected Default' : 'No Default'}
            </p>

            {/* Financial Strain Badge */}
            {result.financial_strain && (
              <div className="flex items-center gap-2 text-orange-400 bg-orange-400/10 border border-orange-400/30 px-4 py-2.5 rounded-lg text-sm font-medium">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>Financial Strain Detected — LIR: <strong>{result.loan_income_ratio}x</strong>. Risk boosted by safety interceptor.</span>
              </div>
            )}

            {result.comparisons && (
              <div className="mt-6 text-left bg-slate-800/40 p-4 rounded-xl border border-slate-700/50">
                <h4 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Model Comparisons</h4>
                <div className="grid grid-cols-2 gap-y-3 gap-x-4">
                  {Object.entries(result.comparisons).map(([model, prob]) => (
                    <div key={model} className="flex justify-between items-center text-sm border-b border-slate-700/30 pb-1">
                      <span className="text-slate-400">{model}</span>
                      <span className={clsx("font-medium", model === result.model_used ? "text-blue-400" : "text-slate-200")}>{prob}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-slate-500 flex flex-col items-center gap-4">
            <Activity className="w-16 h-16 opacity-20" />
            <p>Input parameters to view prediction</p>
          </div>
        )}
      </div>
    </div>
  );
}
