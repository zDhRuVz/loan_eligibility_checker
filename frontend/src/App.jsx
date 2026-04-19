import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Predict from './pages/Predict';
import Dashboard from './pages/Dashboard';
import Insights from './pages/Insights';

function Layout() {
  const location = useLocation();
  const [bgImage, setBgImage] = useState('/bg/home_bg.png');

  useEffect(() => {
    switch(location.pathname) {
      case '/': return setBgImage('/bg/home_bg.png');
      case '/predict': return setBgImage('/bg/predict_bg.png');
      case '/dashboard': return setBgImage('/bg/dashboard_bg.png');
      case '/insights': return setBgImage('/bg/insights_bg.png');
      default: return setBgImage('/bg/home_bg.png');
    }
  }, [location.pathname]);

  return (
    <div 
      className="min-h-screen flex flex-col text-slate-50 relative bg-transition bg-cover bg-center bg-no-repeat bg-fixed bg-slate-900"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      {/* Heavy blending overlay preventing visual text camouflage */}
      <div className="absolute inset-0 bg-slate-900/60 z-0"></div>
      
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/insights" element={<Insights />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}

export default App;
