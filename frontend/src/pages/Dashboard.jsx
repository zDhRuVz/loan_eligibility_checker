import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function Dashboard() {
  // Static metrics based on cross-validation outputs from Untitled1.ipynb
  const data = [
    { name: 'Logistic Regression', F1: 38.6, Precision: 30.0, Recall: 60.0 },
    { name: 'KNN', F1: 57.8, Precision: 74.0, Recall: 79.0 },
    { name: 'Random Forest', F1: 83.3, Precision: 85.0, Recall: 82.0 },
    { name: 'XGBoost', F1: 83.4, Precision: 86.0, Recall: 81.0 },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">Model Performance Analytics</h2>
        <p className="text-slate-400 mt-2">Evaluation results benchmarked against the 20% test partition of our credit dataset.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        
        {/* Main Chart */}
        <div className="glass-panel p-6 rounded-2xl">
          <h3 className="text-xl font-semibold mb-6 flex items-center">F1 Score Breakdown</h3>
          <div className="h-[400px] w-full">
            <ResponsiveContainer>
              <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  cursor={{fill: '#1e293b'}} 
                  contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px'}} 
                />
                <Legend iconType="circle" />
                <Bar dataKey="F1" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Detailed Comparisons */}
        <div className="glass-panel p-6 rounded-2xl">
          <h3 className="text-xl font-semibold mb-6">Precision & Recall</h3>
          <div className="h-[400px] w-full">
            <ResponsiveContainer>
              <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  cursor={{fill: '#1e293b'}} 
                  contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px'}} 
                />
                <Legend iconType="circle" />
                <Bar dataKey="Precision" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Recall" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
