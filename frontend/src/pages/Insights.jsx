import { CheckCircle2, ChevronRight } from 'lucide-react';

export default function Insights() {
  return (
    <div className="max-w-4xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
      
      <div>
        <h2 className="text-3xl font-bold mb-4">Under the Hood: Machine Learning Architecture</h2>
        <p className="text-slate-400 text-lg">Understanding how TrustLens navigates data imbalance, missing variables, and model scaling for optimized credit risk computation.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <div className="glass-panel p-8 rounded-2xl relative overflow-hidden group hover:border-blue-500/50 transition-colors">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <svg className="w-24 h-24 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
          </div>
          <h3 className="text-xl font-bold mb-4 flex items-center text-blue-400">Class Imbalance Handling</h3>
          <p className="text-slate-300 leading-relaxed">
            In credit environments, 'Defaults' are much rarer than safe loans. We utilized the parameter <code>class_weight='balanced'</code> alongside targeted <code>scale_pos_weight</code> modifiers natively evaluating event imbalances over 148k rows.
          </p>
        </div>

        <div className="glass-panel p-8 rounded-2xl relative overflow-hidden group hover:border-emerald-500/50 transition-colors">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <svg className="w-24 h-24 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
          </div>
          <h3 className="text-xl font-bold mb-4 flex items-center text-emerald-400">Targeted Context Scaling</h3>
          <p className="text-slate-300 leading-relaxed">
            To prevent numeric instability, features are scaled universally for metric-sensitive models like KNN and Logistic Regression via <code>StandardScaler</code>. Tree-based learners like Random Forest bypass this, preserving decision boundary clarity.
          </p>
        </div>

      </div>

      <div className="glass-panel p-8 rounded-2xl">
        <h3 className="text-xl font-bold mb-6 border-b border-slate-700 pb-4">Dataset Constitution</h3>
        
        <ul className="space-y-4">
          <li className="flex items-start">
            <CheckCircle2 className="w-6 h-6 text-indigo-400 mr-3 flex-shrink-0" />
            <div>
              <strong className="block text-slate-200">Robust Sample Base</strong>
              <span className="text-slate-400">Analysis rests on an extensive 148,670 applications. Null records were safely median-imputed across boundaries.</span>
            </div>
          </li>
          <li className="flex items-start">
            <CheckCircle2 className="w-6 h-6 text-indigo-400 mr-3 flex-shrink-0" />
            <div>
              <strong className="block text-slate-200">Derived Variables</strong>
              <span className="text-slate-400">Variables like <code className="bg-slate-800 px-1 py-0.5 rounded text-sm mx-1">loan_amount / (income + 1)</code> are compiled server-side, securing prediction flows without bogging down external API requirements.</span>
            </div>
          </li>
          <li className="flex items-start">
            <CheckCircle2 className="w-6 h-6 text-indigo-400 mr-3 flex-shrink-0" />
            <div>
              <strong className="block text-slate-200">Predictive Probabilities</strong>
              <span className="text-slate-400">Logistic Regressive output intercepts provide smooth categorical distributions (Low/Med/High risk logic) to frame raw Boolean predictions (0/1).</span>
            </div>
          </li>
        </ul>
      </div>

    </div>
  );
}
