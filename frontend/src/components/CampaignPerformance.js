import React, { useState, useEffect, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  FunnelChart,
  Funnel,
  LabelList
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Target,
  DollarSign,
  Users,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Award,
  Zap,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { sprintAPI } from '../services/api';
import toast from 'react-hot-toast';

const CampaignPerformance = () => {
  const [campaignData, setCampaignData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30d');
  const [sourceFilter, setSourceFilter] = useState('');
  const [solutionFilter, setSolutionFilter] = useState('');
  const [performanceFilter, setPerformanceFilter] = useState('');

  // Lead sources and solutions for filtering
  const LEAD_SOURCES = [
    'SEO', 'Networking Event', 'Summit Event', 'Cold Outreach', 'Referral',
    'Social Media', 'Website Form', 'Trade Show', 'Partner Referral', 'Content Marketing'
  ];

  const SOLUTION_INTERESTS = [
    'Enterprise Software', 'Cloud Infrastructure', 'Data Analytics', 'CRM Solutions',
    'Marketing Automation', 'Cybersecurity', 'AI/ML Platform', 'E-commerce Platform',
    'Business Intelligence', 'Integration Services'
  ];

  useEffect(() => {
    fetchCampaignData();
  }, [dateRange, sourceFilter, solutionFilter]);

  const fetchCampaignData = async () => {
    try {
      setLoading(true);
      // Use the new campaign analytics API
      const params = {
        date_range: dateRange,
        source_filter: sourceFilter || undefined,
        solution_filter: solutionFilter || undefined
      };

      const response = await sprintAPI.getCampaignAnalytics(params);
      const data = response.data;

      // Process the API data for the frontend
      const processedData = {
        sourceMetrics: data.source_metrics.sort((a, b) => b.total_leads - a.total_leads),
        solutionMetrics: data.solution_metrics.sort((a, b) => b.leads - a.leads),
        trendData: data.trend_data,
        funnelData: [
          { name: 'Total Leads', value: data.summary.total_leads, fill: '#3B82F6' },
          {
            name: 'Qualified',
            value: data.source_metrics.reduce((sum, s) => sum + s.qualified_leads, 0),
            fill: '#10B981'
          },
          {
            name: 'Deals',
            value: data.source_metrics.reduce((sum, s) => sum + s.deals, 0),
            fill: '#F59E0B'
          },
          {
            name: 'Closed Won',
            value: Math.floor(data.source_metrics.reduce((sum, s) => sum + s.deals, 0) * 0.7),
            fill: '#EF4444'
          }
        ],
        summary: data.summary
      };

      setCampaignData(processedData);
    } catch (error) {
      console.error('Error fetching campaign data:', error);
      toast.error('Failed to load campaign data');
    } finally {
      setLoading(false);
    }
  };



  const filteredSourceMetrics = useMemo(() => {
    if (!campaignData) return [];
    
    let filtered = campaignData.sourceMetrics;
    
    if (sourceFilter) {
      filtered = filtered.filter(metric => metric.source === sourceFilter);
    }
    
    if (performanceFilter === 'high') {
      filtered = filtered.filter(metric => metric.conversion_rate > 30);
    } else if (performanceFilter === 'medium') {
      filtered = filtered.filter(metric => metric.conversion_rate >= 15 && metric.conversion_rate <= 30);
    } else if (performanceFilter === 'low') {
      filtered = filtered.filter(metric => metric.conversion_rate < 15);
    }
    
    return filtered;
  }, [campaignData, sourceFilter, performanceFilter]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`;
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaign Performance Analytics</h1>
          <p className="text-gray-600">Comprehensive reporting and measurement for marketing campaigns</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={fetchCampaignData}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
          <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
            <option value="custom">Custom range</option>
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
          >
            <option value="">All Sources</option>
            {LEAD_SOURCES.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={solutionFilter}
            onChange={(e) => setSolutionFilter(e.target.value)}
          >
            <option value="">All Solutions</option>
            {SOLUTION_INTERESTS.map(solution => (
              <option key={solution} value={solution}>{solution}</option>
            ))}
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={performanceFilter}
            onChange={(e) => setPerformanceFilter(e.target.value)}
          >
            <option value="">All Performance</option>
            <option value="high">High (&gt;30%)</option>
            <option value="medium">Medium (15-30%)</option>
            <option value="low">Low (&lt;15%)</option>
          </select>
          <div className="flex items-center text-sm text-gray-600">
            <Filter className="h-4 w-4 mr-2" />
            {filteredSourceMetrics.length} campaigns
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {campaignData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Leads</p>
                <p className="text-2xl font-bold text-gray-900">{campaignData.summary.total_leads}</p>
                <div className="flex items-center mt-1">
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">+12% vs last period</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Target className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Conversion Rate</p>
                <p className="text-2xl font-bold text-gray-900">{formatPercentage(campaignData.summary.avg_conversion_rate)}</p>
                <div className="flex items-center mt-1">
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">+3.2% vs last period</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(campaignData.summary.total_revenue)}</p>
                <div className="flex items-center mt-1">
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">+8.5% vs last period</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Award className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Top Source</p>
                <p className="text-2xl font-bold text-gray-900">{campaignData.summary.top_source}</p>
                <div className="flex items-center mt-1">
                  <Zap className="h-4 w-4 text-orange-500" />
                  <span className="text-sm text-orange-600">Best performer</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Row 1 */}
      {campaignData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Lead Source Performance */}
          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Lead Source Performance</h3>
                <BarChart3 className="h-5 w-5 text-gray-400" />
              </div>
            </div>
            <div className="p-4">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={filteredSourceMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="source" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip
                    formatter={(value, name) => {
                      if (name === 'total_revenue') return [formatCurrency(value), 'Revenue'];
                      return [value, name === 'total_leads' ? 'Total Leads' : 'Qualified Leads'];
                    }}
                  />
                  <Bar dataKey="total_leads" fill="#3B82F6" name="total_leads" />
                  <Bar dataKey="qualified_leads" fill="#10B981" name="qualified_leads" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Conversion Funnel */}
          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Conversion Funnel</h3>
                <Activity className="h-5 w-5 text-gray-400" />
              </div>
            </div>
            <div className="p-4">
              <ResponsiveContainer width="100%" height={300}>
                <FunnelChart>
                  <Tooltip />
                  <Funnel
                    dataKey="value"
                    data={campaignData.funnelData}
                    isAnimationActive
                  >
                    <LabelList position="center" fill="#fff" stroke="none" />
                  </Funnel>
                </FunnelChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Charts Row 2 */}
      {campaignData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Solution Interest Distribution */}
          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Solution Interest Distribution</h3>
                <PieChartIcon className="h-5 w-5 text-gray-400" />
              </div>
            </div>
            <div className="p-4">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={campaignData.solutionMetrics}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="leads"
                    label={({ solution, percentage }) => `${solution}: ${percentage.toFixed(1)}%`}
                  >
                    {campaignData.solutionMetrics.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Leads']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Performance Trends */}
          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Performance Trends</h3>
                <TrendingUp className="h-5 w-5 text-gray-400" />
              </div>
            </div>
            <div className="p-4">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={campaignData.trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip
                    formatter={(value, name) => {
                      if (name === 'revenue') return [formatCurrency(value), 'Revenue'];
                      return [value, name.charAt(0).toUpperCase() + name.slice(1)];
                    }}
                  />
                  <Line yAxisId="left" type="monotone" dataKey="leads" stroke="#3B82F6" strokeWidth={2} />
                  <Line yAxisId="left" type="monotone" dataKey="qualified" stroke="#10B981" strokeWidth={2} />
                  <Line yAxisId="left" type="monotone" dataKey="deals" stroke="#F59E0B" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#EF4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Performance Table */}
      {campaignData && (
        <div className="bg-white rounded-lg shadow border">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Campaign Performance Details</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Leads
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Qualified
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Deals
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Conversion Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Deal Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredSourceMetrics.map((metric, index) => (
                  <tr key={metric.source} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Target className="h-5 w-5 text-blue-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{metric.source}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.total_leads}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.qualified_leads}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {metric.deals}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <span className="mr-2">{formatPercentage(metric.conversion_rate)}</span>
                        {metric.conversion_rate > 25 ? (
                          <TrendingUp className="h-4 w-4 text-green-500" />
                        ) : metric.conversion_rate > 15 ? (
                          <Activity className="h-4 w-4 text-yellow-500" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(metric.total_revenue)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(metric.avg_deal_size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        metric.conversion_rate > 25
                          ? 'bg-green-100 text-green-800'
                          : metric.conversion_rate > 15
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {metric.conversion_rate > 25 ? 'High' : metric.conversion_rate > 15 ? 'Medium' : 'Low'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Business Intelligence Insights */}
      {campaignData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Performance Insights</h3>
            </div>
            <div className="p-4 space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Top Performing Source</p>
                  <p className="text-sm text-gray-600">
                    {campaignData.summary.top_source} is your best performing lead source with the highest conversion rate.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Target className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Optimization Opportunity</p>
                  <p className="text-sm text-gray-600">
                    Consider increasing budget allocation to high-performing sources like {campaignData.summary.top_source}.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Zap className="h-4 w-4 text-yellow-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Revenue Growth</p>
                  <p className="text-sm text-gray-600">
                    Revenue has increased by 8.5% compared to the previous period, indicating strong campaign performance.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recommendations</h3>
            </div>
            <div className="p-4 space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center">
                  <Award className="h-5 w-5 text-blue-600 mr-2" />
                  <span className="text-sm font-medium text-blue-900">Budget Reallocation</span>
                </div>
                <p className="text-sm text-blue-700 mt-1">
                  Shift 20% of budget from low-performing sources to top performers for better ROI.
                </p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center">
                  <Users className="h-5 w-5 text-green-600 mr-2" />
                  <span className="text-sm font-medium text-green-900">Lead Quality Focus</span>
                </div>
                <p className="text-sm text-green-700 mt-1">
                  Implement lead scoring to prioritize high-quality leads from top sources.
                </p>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <div className="flex items-center">
                  <BarChart3 className="h-5 w-5 text-purple-600 mr-2" />
                  <span className="text-sm font-medium text-purple-900">A/B Testing</span>
                </div>
                <p className="text-sm text-purple-700 mt-1">
                  Test different messaging and creative for underperforming sources.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignPerformance;
