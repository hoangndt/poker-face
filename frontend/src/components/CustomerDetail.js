import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Building, 
  MapPin, 
  DollarSign, 
  Calendar,
  AlertTriangle,
  TrendingUp,
  Activity
} from 'lucide-react';
import { customerAPI, aiAPI } from '../services/api';
import toast from 'react-hot-toast';

const CustomerDetail = () => {
  const { id } = useParams();
  const [customer, setCustomer] = useState(null);
  const [journey, setJourney] = useState(null);
  const [churnPrediction, setChurnPrediction] = useState(null);
  const [clv, setClv] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchCustomerData();
    }
  }, [id]);

  const fetchCustomerData = async () => {
    try {
      const [customerRes, journeyRes] = await Promise.all([
        customerAPI.getCustomer(id),
        customerAPI.getCustomerJourney(id)
      ]);
      
      setCustomer(customerRes.data);
      setJourney(journeyRes.data);
      
      // Get AI predictions if customer is active
      if (customerRes.data.Customer_Flag) {
        try {
          const [churnRes, clvRes] = await Promise.all([
            aiAPI.predictChurn(id),
            aiAPI.calculateCLV(id)
          ]);
          setChurnPrediction(churnRes.data);
          setClv(clvRes.data);
        } catch (error) {
          console.log('AI predictions not available:', error);
        }
      }
    } catch (error) {
      toast.error('Failed to load customer data');
      console.error('Customer detail error:', error);
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

  if (!customer) {
    return (
      <div className="text-center py-12">
        <div className="text-sm text-gray-500">Customer not found</div>
      </div>
    );
  }

  const getStageDisplay = () => {
    if (customer.Churn_Flag) return { label: 'Churned', color: 'bg-red-100 text-red-800' };
    if (customer.Customer_Flag) return { label: 'Customer', color: 'bg-green-100 text-green-800' };
    if (customer.SQL_Flag) return { label: 'SQL', color: 'bg-blue-100 text-blue-800' };
    if (customer.MQL_Flag) return { label: 'MQL', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Lead', color: 'bg-gray-100 text-gray-800' };
  };

  const stage = getStageDisplay();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center space-x-5">
            <div className="flex-shrink-0">
              <div className="h-20 w-20 rounded-full bg-gray-300 flex items-center justify-center">
                <span className="text-xl font-medium text-gray-700">
                  {customer.first_name?.[0]}{customer.last_name?.[0]}
                </span>
              </div>
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">
                {customer.first_name} {customer.last_name}
              </h1>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${stage.color}`}>
                  {stage.label}
                </span>
                {customer.Industry && (
                  <span className="text-sm text-gray-500">{customer.Industry}</span>
                )}
                {customer.Region && (
                  <span className="text-sm text-gray-500">{customer.Region}</span>
                )}
              </div>
            </div>
            {churnPrediction && (
              <div className="flex-shrink-0">
                <div className={`p-4 rounded-lg ${
                  churnPrediction.churn_probability > 0.7 ? 'bg-red-100' :
                  churnPrediction.churn_probability > 0.4 ? 'bg-yellow-100' : 'bg-green-100'
                }`}>
                  <div className="text-sm font-medium text-gray-900">Churn Risk</div>
                  <div className={`text-lg font-bold ${
                    churnPrediction.churn_probability > 0.7 ? 'text-red-600' :
                    churnPrediction.churn_probability > 0.4 ? 'text-yellow-600' : 'text-green-600'
                  }`}>
                    {(churnPrediction.churn_probability * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">ACV</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${(customer.ACV_USD || 0).toLocaleString()}
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
                  <dt className="text-sm font-medium text-gray-500 truncate">LTV</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${(customer.LTV_USD || 0).toLocaleString()}
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
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">NPS Score</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {customer.NPS_Score || 'N/A'}
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Tenure</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {customer.Customer_Tenure_Months || 0} months
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contact Information */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Contact Information
            </h3>
            <div className="space-y-4">
              <div className="flex items-center">
                <Mail className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-sm text-gray-900">{customer.email}</span>
              </div>
              {customer.Industry && (
                <div className="flex items-center">
                  <Building className="h-5 w-5 text-gray-400 mr-3" />
                  <span className="text-sm text-gray-900">{customer.Industry}</span>
                </div>
              )}
              {customer.Region && (
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-gray-400 mr-3" />
                  <span className="text-sm text-gray-900">{customer.Region}</span>
                </div>
              )}
              {customer.Decision_Maker_Role && (
                <div className="flex items-center">
                  <User className="h-5 w-5 text-gray-400 mr-3" />
                  <span className="text-sm text-gray-900">{customer.Decision_Maker_Role}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Engagement Metrics */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Engagement Metrics
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-500">Monthly Logins</span>
                <span className="text-sm text-gray-900">{customer.Logins_Per_Month || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-500">Active Features</span>
                <span className="text-sm text-gray-900">{customer.Active_Features_Used || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-500">Usage Hours</span>
                <span className="text-sm text-gray-900">{customer.Product_Usage_Hours || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-500">Support Tickets</span>
                <span className="text-sm text-gray-900">{customer.Tickets_Raised || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Journey */}
      {journey && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Customer Journey
            </h3>
            <div className="flow-root">
              <ul className="-mb-8">
                {journey.stages.map((stage, stageIndex) => (
                  <li key={stageIndex}>
                    <div className="relative pb-8">
                      {stageIndex !== journey.stages.length - 1 ? (
                        <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                            <Activity className="h-4 w-4 text-white" />
                          </span>
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-gray-900">
                              Entered <span className="font-medium">{stage.stage}</span> stage
                            </p>
                            {stage.score && (
                              <p className="text-sm text-gray-500">Score: {stage.score}</p>
                            )}
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500">
                            {stage.date ? new Date(stage.date).toLocaleDateString() : 'N/A'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {(churnPrediction || clv) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Churn Prediction */}
          {churnPrediction && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Churn Risk Analysis
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-500">Risk Level</span>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${
                      churnPrediction.risk_level === 'High' ? 'bg-red-100 text-red-800' :
                      churnPrediction.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {churnPrediction.risk_level}
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium text-gray-500">Risk Factors:</span>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {churnPrediction.risk_factors.map((factor, index) => (
                        <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          {factor}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium text-gray-500">Recommendations:</span>
                    <ul className="mt-2 text-sm text-gray-600 space-y-1">
                      {churnPrediction.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start">
                          <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CLV Analysis */}
          {clv && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Customer Lifetime Value
                </h3>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">
                      ${clv.estimated_clv.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">
                      Estimated CLV (Confidence: {(clv.confidence * 100).toFixed(0)}%)
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium text-gray-500">Contributing Factors:</span>
                    <div className="mt-2 space-y-1">
                      {clv.contributing_factors.map((factor, index) => (
                        <div key={index} className="flex items-center text-sm text-gray-600">
                          <span className="w-1.5 h-1.5 bg-green-600 rounded-full mr-2"></span>
                          {factor}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CustomerDetail;