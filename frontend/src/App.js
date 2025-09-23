import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  NavLink,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { Icon } from "@iconify/react";

// Import components
import Dashboard from "./components/Dashboard";
import CustomerList from "./components/CustomerList";
import CustomerDetail from "./components/CustomerDetail";
import Analytics from "./components/Analytics";
import ChurnPrediction from "./components/ChurnPrediction";
import RevenueForecasting from "./components/RevenueForecasting";
import PipelineHealth from "./components/PipelineHealth";
import VietnamDashboard from "./components/VietnamDashboard";
import SprintBoard from "./components/SprintBoard";

import "./App.css";

function App() {

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Toaster position="top-right" />

        {/* Sidebar */}
        <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg border-r border-gray-200">
          <div className="flex h-16 items-center justify-center border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Icon icon="solar:chart-2-bold" className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">
                Customer AI
              </span>
            </div>
          </div>

          <nav className="space-y-1 p-4">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:chart-2-bold-duotone" className="h-5 w-5" />
              <span>Dashboard</span>
            </NavLink>
            <NavLink
              to="/sprint-board"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:target-bold-duotone" className="h-5 w-5" />
              <span>Sale pipeline</span>
            </NavLink>
            <NavLink
              to="/customers"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:users-group-two-rounded-bold-duotone" className="h-5 w-5" />
              <span>Customers</span>
            </NavLink>

            {/* Analytics Section */}
            <div className="border-t border-gray-200 my-2"></div>
            <NavLink
              to="/analytics"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:graph-up-bold-duotone" className="h-5 w-5" />
              <span>Analytics</span>
            </NavLink>
            <NavLink
              to="/churn-prediction"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:danger-triangle-bold-duotone" className="h-5 w-5" />
              <span>Churn Prediction</span>
            </NavLink>
            <NavLink
              to="/revenue-forecasting"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:dollar-minimalistic-bold-duotone" className="h-5 w-5" />
              <span>Revenue Forecast</span>
            </NavLink>
            <NavLink
              to="/pipeline-health"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`
              }
            >
              <Icon icon="solar:pulse-2-bold-duotone" className="h-5 w-5" />
              <span>Pipeline Health</span>
            </NavLink>

            {/* Special Dashboards */}
            <div className="border-t border-gray-200 my-2"></div>
            <NavLink
              to="/vietnam-dashboard"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'bg-green-600 text-white'
                    : 'text-gray-700 hover:bg-green-50 hover:text-green-600'
                }`
              }
            >
              <Icon icon="solar:global-bold-duotone" className="h-5 w-5" />
              <span>Vietnam Dashboard</span>
            </NavLink>
          </nav>
        </div>

        {/* Main content */}
        <div className="pl-64">
          <div className="py-6">
            <div className="mx-auto px-4 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/sprint-board" element={<SprintBoard />} />
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
