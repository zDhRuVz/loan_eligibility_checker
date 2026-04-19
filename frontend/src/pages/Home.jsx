import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck, Zap, Database } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center text-center mt-16 space-y-12">
      <div className="max-w-3xl space-y-6">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
          Predict Loan Approvals with AI Precision
        </h1>
        <p className="text-lg md:text-xl text-slate-400">
          Leverage our ensemble of machine learning models to analyze lending risk instantly. Designed for modern fintech resilience.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link 
            to="/predict" 
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105"
          >
            Start Predicting <ArrowRight className="w-5 h-5" />
          </Link>
          <Link 
            to="/dashboard" 
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 hover:text-white px-6 py-3 rounded-xl font-semibold transition-all"
          >
            Compare Models
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mt-16">
        <div className="glass-panel p-6 rounded-2xl flex flex-col items-center text-center space-y-4">
          <div className="bg-blue-500/20 p-4 rounded-full">
            <Zap className="w-8 h-8 text-blue-400" />
          </div>
          <h3 className="text-xl font-bold">Fast Inference</h3>
          <p className="text-slate-400 text-sm">Powered by FastAPI, get predictions in milliseconds using an optimized ML pipeline.</p>
        </div>
        <div className="glass-panel p-6 rounded-2xl flex flex-col items-center text-center space-y-4">
          <div className="bg-emerald-500/20 p-4 rounded-full">
            <ShieldCheck className="w-8 h-8 text-emerald-400" />
          </div>
          <h3 className="text-xl font-bold">Robust Models</h3>
          <p className="text-slate-400 text-sm">Validating against 4 different algorithms including scaled Logistic Regression and extreme gradient boosting.</p>
        </div>
        <div className="glass-panel p-6 rounded-2xl flex flex-col items-center text-center space-y-4">
          <div className="bg-purple-500/20 p-4 rounded-full">
            <Database className="w-8 h-8 text-purple-400" />
          </div>
          <h3 className="text-xl font-bold">Data Driven</h3>
          <p className="text-slate-400 text-sm">Trained on over 140,000 historic credit events properly handled for class imbalancing.</p>
        </div>
      </div>
    </div>
  );
}
