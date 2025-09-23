import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingDown, Users, RefreshCw } from 'lucide-react';
import { aiAPI, customerAPI } from '../services/api';
import toast from 'react-hot-toast';

const ChurnPrediction = () => {
  const [churnRiskCustomers, setChurnRiskCustomers] = useState([]);
  const [riskThreshold, setRiskThreshold] = useState(0.7);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchChurnPredictions();
  }, [riskThreshold]);

  const fetchChurnPredictions = async () => {
    try {
      const response = await aiAPI.getChurnRiskCustomers(riskThreshold);
      setChurnRiskCustomers(response.data.at_risk_customers || []);
    } catch (error) {
      toast.error('Failed to load churn predictions');
      console.error('Churn prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      await fetchChurnPredictions();
      toast.success('Churn analysis updated successfully');
    } catch (error) {
      toast.error('Failed to update analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (probability) => {
    if (probability > 0.8) return 'bg-red-500';
    if (probability > 0.6) return 'bg-orange-500';
    return 'bg-yellow-500';
  };

  const getRiskLevel = (probability) => {
    if (probability > 0.8) return 'Critical';
    if (probability > 0.6) return 'High';
    return 'Medium';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Churn Prediction & Prevention
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered churn prediction with actionable recommendations
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <button
            onClick={runAnalysis}
            disabled={analyzing}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`-ml-1 mr-2 h-4 w-4 ${analyzing ? 'animate-spin' : ''}`} />
            {analyzing ? 'Analyzing...' : 'Refresh Analysis'}
          </button>
        </div>
      </div>

      {/* Risk Threshold Control */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Risk Threshold</h3>
            <p className="mt-1 text-sm text-gray-500">
              Adjust the sensitivity of churn risk detection
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">
              Threshold: {(riskThreshold * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.1"
              value={riskThreshold}
              onChange={(e) => setRiskThreshold(parseFloat(e.target.value))}
              className="w-32"
            />
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">At Risk Customers</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {churnRiskCustomers.length}
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
                <TrendingDown className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Risk Score</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {churnRiskCustomers.length > 0 
                      ? (churnRiskCustomers.reduce((sum, c) => sum + c.churn_probability, 0) / churnRiskCustomers.length * 100).toFixed(1)
                      : 0}%
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
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Critical Risk</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {churnRiskCustomers.filter(c => c.churn_probability > 0.8).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* At Risk Customers */}
      {churnRiskCustomers.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Customers at Risk of Churning
            </h3>
            <div className="space-y-4">
              {churnRiskCustomers.map((customer) => (
                <div key={customer.customer_id} className="border border-gray-200 rounded-lg p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h4 className="text-lg font-medium text-gray-900">
                          {customer.customer_name}
                        </h4>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white ${getRiskColor(customer.churn_probability)}`}>
                          {getRiskLevel(customer.churn_probability)} Risk
                        </span>
                      </div>
                      
                      <div className="mt-2">
                        <div className="text-sm text-gray-600">
                          <strong>Churn Probability:</strong> {(customer.churn_probability * 100).toFixed(1)}%
                        </div>
                      </div>

                      {/* Risk Factors */}
                      <div className="mt-3">
                        <h5 className="text-sm font-medium text-gray-900 mb-2">Risk Factors:</h5>
                        <div className="flex flex-wrap gap-2">
                          {customer.risk_factors.map((factor, index) => (
                            <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              {factor}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mt-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">Risk Level</span>
                          <span className="font-medium">{(customer.churn_probability * 100).toFixed(1)}%</span>
                        </div>
                        <div className="mt-1 relative">
                          <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                            <div 
                              style={{ width: `${customer.churn_probability * 100}%` }}
                              className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${getRiskColor(customer.churn_probability)}`}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-4 flex space-x-3">
                    <button className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                      Contact Customer
                    </button>
                    <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      Create Retention Plan
                    </button>
                    <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No High-Risk Customers</h3>
            <p className="mt-1 text-sm text-gray-500">
              Great news! No customers are currently at high risk of churning at the {(riskThreshold * 100).toFixed(0)}% threshold.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setRiskThreshold(0.3)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Lower Threshold to See More
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChurnPrediction;