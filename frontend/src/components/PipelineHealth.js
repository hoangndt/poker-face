import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Target, TrendingUp, Calendar, DollarSign, Users, AlertCircle } from 'lucide-react';
import { pipelineAPI } from '../services/api';
import toast from 'react-hot-toast';

const PipelineHealth = () => {
  const [pipelineHealth, setPipelineHealth] = useState(null);
  const [pipelineForecast, setPipelineForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPipelineData();
  }, []);

  const fetchPipelineData = async () => {
    try {
      const [healthRes, forecastRes] = await Promise.all([
        pipelineAPI.getPipelineHealth(),
        pipelineAPI.getPipelineForecast()
      ]);
      
      setPipelineHealth(healthRes.data);
      setPipelineForecast(forecastRes.data);
    } catch (error) {
      toast.error('Failed to load pipeline data');
      console.error('Pipeline error:', error);
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

  const stageData = pipelineHealth?.pipeline_by_stage ? [
    { stage: 'Leads', value: pipelineHealth.pipeline_by_stage.leads },
    { stage: 'MQLs', value: pipelineHealth.pipeline_by_stage.mqls },
    { stage: 'SQLs', value: pipelineHealth.pipeline_by_stage.sqls }
  ] : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const upcomingOpportunities = pipelineForecast?.opportunities || [];
  const highProbabilityOpps = upcomingOpportunities.filter(opp => opp.probability > 70);
  const mediumProbabilityOpps = upcomingOpportunities.filter(opp => opp.probability >= 30 && opp.probability <= 70);
  const lowProbabilityOpps = upcomingOpportunities.filter(opp => opp.probability < 30);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Sales Pipeline Health
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Monitor pipeline performance and forecast accuracy
          </p>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Pipeline Value</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${(pipelineHealth?.total_pipeline_value || 0).toLocaleString()}
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
                <Target className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Weighted Pipeline</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${(pipelineHealth?.weighted_pipeline || 0).toLocaleString()}
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
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Win Rate</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {((pipelineHealth?.win_rate || 0) * 100).toFixed(1)}%
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Velocity</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {pipelineHealth?.pipeline_velocity || 0} days
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline by Stage */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Pipeline by Stage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stageData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="stage" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pipeline Health Score */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Pipeline Health Indicators</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-500">Coverage Ratio</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
                <span className="text-sm font-medium text-gray-900">3.2x</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-500">Stage Progression</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '68%' }}></div>
                </div>
                <span className="text-sm font-medium text-gray-900">Good</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-500">Velocity Health</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '55%' }}></div>
                </div>
                <span className="text-sm font-medium text-gray-900">Average</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-500">Forecast Accuracy</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '82%' }}></div>
                </div>
                <span className="text-sm font-medium text-gray-900">High</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Forecast Summary */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            90-Day Pipeline Forecast
          </h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{highProbabilityOpps.length}</span>
                  </div>
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-green-900">High Probability (&gt;70%)</div>
                  <div className="text-lg font-bold text-green-600">
                    ${highProbabilityOpps.reduce((sum, opp) => sum + opp.forecasted_revenue, 0).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{mediumProbabilityOpps.length}</span>
                  </div>
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-yellow-900">Medium Probability (30-70%)</div>
                  <div className="text-lg font-bold text-yellow-600">
                    ${mediumProbabilityOpps.reduce((sum, opp) => sum + opp.forecasted_revenue, 0).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{lowProbabilityOpps.length}</span>
                  </div>
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-red-900">Low Probability (&lt;30%)</div>
                  <div className="text-lg font-bold text-red-600">
                    ${lowProbabilityOpps.reduce((sum, opp) => sum + opp.forecasted_revenue, 0).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Opportunities */}
      {upcomingOpportunities.length > 0 && (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Upcoming Opportunities (Next 90 Days)
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Expected Close
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Probability
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Weighted Revenue
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {upcomingOpportunities.slice(0, 10).map((opportunity) => (
                    <tr key={opportunity.customer_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {opportunity.customer_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(opportunity.expected_close_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${opportunity.forecasted_revenue.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          opportunity.probability > 70 ? 'bg-green-100 text-green-800' :
                          opportunity.probability >= 30 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {opportunity.probability}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${opportunity.weighted_revenue.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Pipeline Recommendations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-4">Pipeline Optimization Recommendations</h3>
        <div className="space-y-2">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            </div>
            <div className="ml-3 text-sm text-blue-800">
              Focus on converting {mediumProbabilityOpps.length} medium probability opportunities to improve forecast accuracy
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            </div>
            <div className="ml-3 text-sm text-blue-800">
              Pipeline velocity of {pipelineHealth?.pipeline_velocity || 0} days is above average - maintain current momentum
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            </div>
            <div className="ml-3 text-sm text-blue-800">
              Consider increasing lead generation to maintain healthy pipeline coverage ratio
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelineHealth;