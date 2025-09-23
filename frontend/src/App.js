import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  NavLink,
  Link,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import {
  BarChart3,
  Users,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  Activity,
  Target,
  PieChart,
} from "lucide-react";

// Import components
import Dashboard from "./components/Dashboard";
import CustomerList from "./components/CustomerList";
import CustomerDetail from "./components/CustomerDetail";
import Analytics from "./components/Analytics";
import ChurnPrediction from "./components/ChurnPrediction";
import RevenueForecasting from "./components/RevenueForecasting";
import PipelineHealth from "./components/PipelineHealth";
import VietnamDashboard from "./components/VietnamDashboard";

import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: "Dashboard", href: "/", icon: BarChart3 },
    { name: "Customers", href: "/customers", icon: Users },
    { name: "Analytics", href: "/analytics", icon: PieChart },
    { name: "Churn Prediction", href: "/churn-prediction", icon: AlertTriangle },
    { name: "Revenue Forecast", href: "/revenue-forecasting", icon: TrendingUp },
    { name: "Pipeline Health", href: "/pipeline-health", icon: Target },
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
              <span className="text-xl font-bold text-gray-900">
                Customer AI
              </span>
            </div>
          </div>

          <nav className="space-y-1">
            <Link
              to="/"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              📊 Dashboard
            </Link>
            <Link
              to="/customers"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              👥 Customers
            </Link>
            <Link
              to="/analytics"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              📈 Analytics
            </Link>
            <Link
              to="/churn-prediction"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              🤖 Churn Prediction
            </Link>
            <Link
              to="/revenue-forecasting"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              💰 Revenue Forecast
            </Link>
            <Link
              to="/pipeline-health"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              🔄 Pipeline Health
            </Link>
            <Link
              to="/vietnam-dashboard"
              className="block px-4 py-2 text-sm rounded-md hover:bg-blue-700 transition-colors bg-green-600"
            >
              🇻🇳 Vietnam Dashboard
            </Link>
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
                <Route path="/churn-prediction" element={<ChurnPrediction />} />
                <Route path="/revenue-forecasting" element={<RevenueForecasting />} />
                <Route path="/pipeline-health" element={<PipelineHealth />} />
                <Route
                  path="/vietnam-dashboard"
                  element={<VietnamDashboard />}
                />
              </Routes>
            </div>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
