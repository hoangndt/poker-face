import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, DollarSign, Calendar, Target } from 'lucide-react';
import { aiAPI } from '../services/api';
import toast from 'react-hot-toast';

const RevenueForecasting = () => {
  const [forecast, setForecast] = useState(null);
  const [forecastPeriod, setForecastPeriod] = useState(12);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRevenueForecast();
  }, [forecastPeriod]);

  const fetchRevenueForecast = async () => {
    try {
      const response = await aiAPI.getRevenueForecast(forecastPeriod);
      setForecast(response.data);
    } catch (error) {
      toast.error('Failed to load revenue forecast');
      console.error('Revenue forecast error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const monthlyData = forecast?.monthly_forecast || [];
  const confidenceData = monthlyData.map(month => ({
    ...month,
    lower_bound: month.predicted_revenue * 0.85,
    upper_bound: month.predicted_revenue * 1.15
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Revenue Forecasting
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered revenue predictions and growth analysis
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <select
            value={forecastPeriod}
            onChange={(e) => setForecastPeriod(parseInt(e.target.value))}
            className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
          >
            <option value={6}>6 Months</option>
            <option value={12}>12 Months</option>
            <option value={24}>24 Months</option>
            <option value={36}>36 Months</option>
          </select>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Predicted Revenue</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${(forecast?.predicted_revenue || 0).toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Growth Rate</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {((forecast?.growth_rate || 0) * 100).toFixed(1)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Confidence Range</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ±{(((forecast?.confidence_interval_upper || 0) - (forecast?.predicted_revenue || 0)) / (forecast?.predicted_revenue || 1) * 100).toFixed(0)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Calendar className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Forecast Period</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {forecast?.forecast_period || `${forecastPeriod} months`}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Forecast Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Forecast Trend</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={confidenceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                `$${value.toLocaleString()}`,
                name === 'predicted_revenue' ? 'Predicted Revenue' :
                name === 'lower_bound' ? 'Lower Bound' : 'Upper Bound'
              ]}
            />
            <Line 
              type="monotone" 
              dataKey="predicted_revenue" 
              stroke="#3B82F6" 
              strokeWidth={3}
              name="predicted_revenue"
            />
            <Line 
              type="monotone" 
              dataKey="lower_bound" 
              stroke="#EF4444" 
              strokeDasharray="5 5"
              strokeWidth={1}
              name="lower_bound"
            />
            <Line 
              type="monotone" 
              dataKey="upper_bound" 
              stroke="#10B981" 
              strokeDasharray="5 5"
              strokeWidth={1}
              name="upper_bound"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Revenue Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']} />
            <Bar dataKey="predicted_revenue" fill="#8B5CF6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Seasonality Factors */}
      {forecast?.seasonality_factors && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Seasonality Analysis</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(forecast.seasonality_factors).map(([quarter, factor]) => (
              <div key={quarter} className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {(factor * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-500">{quarter}</div>
                <div className={`mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  factor > 1 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {factor > 1 ? 'Above Average' : 'Below Average'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confidence Intervals */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Forecast Confidence</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">Lower Bound (15% below)</span>
            <span className="text-lg font-semibold text-red-600">
              ${(forecast?.confidence_interval_lower || 0).toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">Predicted Revenue</span>
            <span className="text-lg font-semibold text-gray-900">
              ${(forecast?.predicted_revenue || 0).toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">Upper Bound (15% above)</span>
            <span className="text-lg font-semibold text-green-600">
              ${(forecast?.confidence_interval_upper || 0).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-4">AI Recommendations</h3>
        <div className="space-y-2">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
            </div>
            <div className="ml-3 text-sm text-blue-800">
              Based on the forecast, consider increasing marketing spend in Q4 due to higher seasonality factor
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
            </div>
            <div className="ml-3 text-sm text-blue-800">
              Focus on customer retention to maintain the {((forecast?.growth_rate || 0) * 100).toFixed(1)}% growth rate
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
            </div>
            <div className="ml-3 text-sm text-blue-800">
              Monitor pipeline health to ensure forecast accuracy within the confidence interval
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RevenueForecasting;