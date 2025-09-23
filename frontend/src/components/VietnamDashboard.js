import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts';
import api from '../services/api';

const VietnamDashboard = () => {
  const [dataQuality, setDataQuality] = useState(null);
  const [csInterventions, setCsInterventions] = useState(null);
  const [gradionScore, setGradionScore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch Vietnam-specific data
        const [qualityRes, csRes] = await Promise.all([
          api.get('/vietnam/data-quality-report'),
          api.get('/vietnam/cs-intervention-queue')
        ]);
        
        setDataQuality(qualityRes.data);
        setCsInterventions(csRes.data);
      } catch (error) {
        console.error('Error fetching Vietnam dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const testGradionScoring = async () => {
    try {
      const response = await api.post('/vietnam/gradion-lead-score', {
        email: 'test@gradion.com',
        company_name: 'Gradion Test Company',
        industry: 'technology',
        company_size: 50,
        website_activity: 8,
        email_engagement: 7,
        content_downloads: 5,
        webinar_attendance: 3,
        demo_requests: 2,
        book_consultant: false
      });
      setGradionScore(response.data);
    } catch (error) {
      console.error('Error testing Gradion scoring:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          🇻🇳 Vietnam Market Dashboard
          <span className="text-lg bg-green-100 text-green-800 px-3 py-1 rounded-full">
            Gradion Optimized
          </span>
        </h1>
        <p className="text-gray-600 mt-2">
          Addressing specific pain points in your Vietnamese customer lifecycle
        </p>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Data Quality Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {dataQuality?.data_quality_score || 0}%
              </p>
            </div>
            <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 text-sm">📊</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            HubSpot MQL/SQL consistency
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">CS Interventions</p>
              <p className="text-2xl font-bold text-red-600">
                {csInterventions?.total_at_risk || 0}
              </p>
            </div>
            <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-red-600 text-sm">🚨</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Customers needing attention
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Critical Risk</p>
              <p className="text-2xl font-bold text-red-700">
                {csInterventions?.by_risk_level?.critical || 0}
              </p>
            </div>
            <div className="h-8 w-8 bg-red-200 rounded-full flex items-center justify-center">
              <span className="text-red-700 text-sm">⚠️</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Immediate escalation needed
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Gradion Scoring</p>
              <button 
                onClick={testGradionScoring}
                className="text-sm bg-blue-600 text-white px-3 py-1 rounded"
              >
                Test Scoring
              </button>
            </div>
            <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-sm">🎯</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            ≤109→MQL, ≥110→SQL
          </p>
        </div>
      </div>

      {/* Data Quality Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="border-b border-gray-200 pb-4 mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              📋 Data Quality Issues
              <span className="text-sm bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                {dataQuality?.inconsistent_records || 0} issues found
              </span>
            </h3>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm">
                <span>Missing Required Fields</span>
                <span className="text-red-600">{dataQuality?.missing_required_fields || 0}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                <div 
                  className="bg-red-500 h-2 rounded-full" 
                  style={{ width: `${Math.min((dataQuality?.missing_required_fields || 0) / 100 * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span>Invalid Email Formats</span>
                <span className="text-orange-600">{dataQuality?.invalid_emails || 0}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                <div 
                  className="bg-orange-500 h-2 rounded-full" 
                  style={{ width: `${Math.min((dataQuality?.invalid_emails || 0) / 50 * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span>Duplicate Records</span>
                <span className="text-yellow-600">{dataQuality?.duplicate_records || 0}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                <div 
                  className="bg-yellow-500 h-2 rounded-full" 
                  style={{ width: `${Math.min((dataQuality?.duplicate_records || 0) / 30 * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="border-b border-gray-200 pb-4 mb-4">
            <h3 className="text-lg font-semibold text-gray-900">CS Intervention Queue</h3>
          </div>
          <div className="space-y-3">
            {csInterventions?.customers?.slice(0, 5).map((customer, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium text-sm">{customer.name}</p>
                  <p className="text-xs text-gray-600">Risk: {customer.risk_level}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold">{customer.score}%</p>
                  <p className="text-xs text-gray-500">{customer.next_action}</p>
                </div>
              </div>
            )) || (
              <p className="text-gray-500 text-sm">No interventions needed</p>
            )}
          </div>
        </div>
      </div>

      {/* Gradion Scoring Test Result */}
      {gradionScore && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="border-b border-gray-200 pb-4 mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              🎯 Gradion Lead Scoring Test
              <span className={`text-sm px-3 py-1 rounded-full ${
                gradionScore.classification === 'SQL' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
              }`}>
                {gradionScore.classification}
              </span>
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded">
              <p className="text-2xl font-bold text-gray-900">{gradionScore.score}</p>
              <p className="text-sm text-gray-600">Total Score</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded">
              <p className="text-lg font-semibold text-gray-900">{gradionScore.classification}</p>
              <p className="text-sm text-gray-600">Classification</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded">
              <p className="text-sm text-gray-900">{gradionScore.reasoning}</p>
              <p className="text-xs text-gray-600">Reasoning</p>
            </div>
          </div>
        </div>
      )}

      {/* Customer Success Risk Visualization */}
      {csInterventions && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="border-b border-gray-200 pb-4 mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Customer Success Risk Levels</h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: 'Low Risk', value: csInterventions.by_risk_level?.low || 0, color: '#10B981' },
                    { name: 'Medium Risk', value: csInterventions.by_risk_level?.medium || 0, color: '#F59E0B' },
                    { name: 'High Risk', value: csInterventions.by_risk_level?.high || 0, color: '#EF4444' },
                    { name: 'Critical Risk', value: csInterventions.by_risk_level?.critical || 0, color: '#DC2626' }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {csInterventions && [
                    { name: 'Low Risk', value: csInterventions.by_risk_level?.low || 0, color: '#10B981' },
                    { name: 'Medium Risk', value: csInterventions.by_risk_level?.medium || 0, color: '#F59E0B' },
                    { name: 'High Risk', value: csInterventions.by_risk_level?.high || 0, color: '#EF4444' },
                    { name: 'Critical Risk', value: csInterventions.by_risk_level?.critical || 0, color: '#DC2626' }
                  ].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Vietnamese Market Insights */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <div className="border-b border-gray-200 pb-4 mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            🌏 Vietnamese Market Insights
            <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
              Gradion-Specific
            </span>
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-900">Lead Qualification</h4>
            <p className="text-sm text-blue-700 mt-2">
              Scores ≤109 are classified as MQL (Marketing Qualified Lead).
              Scores ≥110 automatically become SQL (Sales Qualified Lead).
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-semibold text-green-900">Book Consultant Override</h4>
            <p className="text-sm text-green-700 mt-2">
              Any lead that requests to "Book Consultant" immediately gets SQL classification,
              regardless of their score.
            </p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h4 className="font-semibold text-purple-900">Cultural Considerations</h4>
            <p className="text-sm text-purple-700 mt-2">
              Vietnamese customers prefer relationship-building and may require longer nurturing cycles.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VietnamDashboard;