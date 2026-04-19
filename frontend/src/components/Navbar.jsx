import { Link, useLocation } from 'react-router-dom';
import { Activity, Home, LineChart, FileText } from 'lucide-react';
import clsx from 'clsx';

export default function Navbar() {
  const location = useLocation();

  const links = [
    { name: 'Home', path: '/', icon: <Home className="w-4 h-4" /> },
    { name: 'Predict', path: '/predict', icon: <Activity className="w-4 h-4" /> },
    { name: 'Model Compare', path: '/dashboard', icon: <LineChart className="w-4 h-4" /> },
    { name: 'Insights', path: '/insights', icon: <FileText className="w-4 h-4" /> },
  ];

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0 bg-blue-500 p-2 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight text-white">TrustLens</span>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {links.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={clsx(
                      'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200',
                      isActive 
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    )}
                  >
                    {item.icon}
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
