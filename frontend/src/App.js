import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  DollarSign,
  Activity,
  Target,
  PieChart
} from 'lucide-react';

// Import components
import Dashboard from './components/Dashboard';
import CustomerList from './components/CustomerList';
import CustomerDetail from './components/CustomerDetail';
import Analytics from './components/Analytics';
import ChurnPrediction from './components/ChurnPrediction';
import RevenueForecasting from './components/RevenueForecasting';
import PipelineHealth from './components/PipelineHealth';

import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Customers', href: '/customers', icon: Users },
    { name: 'Analytics', href: '/analytics', icon: PieChart },
    { name: 'Churn Prediction', href: '/churn', icon: AlertTriangle },
    { name: 'Revenue Forecast', href: '/revenue', icon: TrendingUp },
    { name: 'Pipeline Health', href: '/pipeline', icon: Target },
  ];

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Toaster position="top-right" />
        
        {/* Sidebar */}
        <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
          <div className="flex h-16 items-center justify-center border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <Activity className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">Customer AI</span>
            </div>
          </div>
          
          <nav className="mt-5 px-2">
            <div className="space-y-1">
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-blue-100 text-blue-900'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  <item.icon
                    className="mr-3 h-5 w-5 flex-shrink-0"
                    aria-hidden="true"
                  />
                  {item.name}
                </NavLink>
              ))}
            </div>
          </nav>
        </div>

        {/* Main content */}
        <div className="pl-64">
          <div className="py-6">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/customers" element={<CustomerList />} />
                <Route path="/customers/:id" element={<CustomerDetail />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/churn" element={<ChurnPrediction />} />
                <Route path="/revenue" element={<RevenueForecasting />} />
                <Route path="/pipeline" element={<PipelineHealth />} />
              </Routes>
            </div>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;