import React, { useState, useEffect } from 'react';
import {
  RefreshCw,
  Download,
  Settings,
  TrendingUp,
  TrendingDown,
  Users,
  Target,
  DollarSign
} from 'lucide-react';
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
  Line
} from 'recharts';
import { sprintAPI } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const analyticsRes = await sprintAPI.getDashboardAnalytics();
      setAnalyticsData(analyticsRes.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard error:', error);
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

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Format numbers for charts (short notation)
  const formatChartNumber = (value) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return value.toString();
  };



  // Generate chart data from API or use defaults
  const salesByQuarterData = analyticsData?.historical_sales || [
    { quarter: 'Q1 2024', amount: 1600000, target: 1500000 },
    { quarter: 'Q2 2024', amount: 2400000, target: 2000000 },
    { quarter: 'Q3 2024', amount: 1100000, target: 1800000 },
    { quarter: 'Q4 2024', amount: 2950000, target: 2500000 }
  ];

  const potentialSalesByStageData = analyticsData?.stage_analysis?.map((item, index) => ({
    stage: item.stage,
    amount: item.amount,
    percentage: ((item.amount / (analyticsData?.summary?.total_pipeline || 1)) * 100).toFixed(1)
  })).filter(item => item.amount > 0) || [
    { stage: 'Prospecting', amount: 975000, percentage: 16.7 },
    { stage: 'Qualification', amount: 835000, percentage: 14.3 },
    { stage: 'Needs Analysis', amount: 1200000, percentage: 20.5 },
    { stage: 'Value Proposition', amount: 950000, percentage: 16.2 },
    { stage: 'Id. Decision Makers', amount: 875000, percentage: 15.0 },
    { stage: 'Perception Analysis', amount: 650000, percentage: 11.1 },
    { stage: 'Proposal/Price Quote', amount: 385000, percentage: 6.6 },
    { stage: 'Negotiation/Review', amount: 130000, percentage: 2.2 }
  ];

  const salesByCountryData = analyticsData?.country_analysis?.map((item, index) => {
    const total = analyticsData?.summary?.total_pipeline || 1;
    return {
      country: item.country,
      amount: item.amount,
      percentage: ((item.amount / total) * 100).toFixed(1)
    };
  }).filter(item => item.amount > 0) || [
    { country: 'United States', amount: 4284000, percentage: 20.1 },
    { country: 'Germany', amount: 2899000, percentage: 13.6 },
    { country: 'United Kingdom', amount: 2480000, percentage: 11.6 },
    { country: 'Canada', amount: 1837000, percentage: 8.6 },
    { country: 'France', amount: 1650000, percentage: 7.7 },
    { country: 'Australia', amount: 1420000, percentage: 6.6 },
    { country: 'Japan', amount: 1290000, percentage: 6.0 },
    { country: 'Netherlands', amount: 1100000, percentage: 5.1 }
  ];

  const salesByLeadSourceData = analyticsData?.lead_source_analysis || [
    { source: 'Web', amount: 760000 },
    { source: 'Inquiry', amount: 540000 },
    { source: 'Phone Inquiry', amount: 350000 },
    { source: 'Partner Referral', amount: 75000 },
    { source: 'Purchased List', amount: 200000 },
    { source: 'Other Sources', amount: 500000 }
  ];

  const expectedRevenueByAccountData = analyticsData?.top_accounts?.map((item, index) => {
    const total = analyticsData?.top_accounts?.reduce((sum, acc) => sum + acc.amount, 0) || 1;
    return {
      account: item.account,
      amount: item.amount,
      percentage: ((item.amount / total) * 100).toFixed(1)
    };
  }) || [
    { account: 'Express Logistics', amount: 150000, percentage: 13.6 },
    { account: 'GenePoint', amount: 120000, percentage: 10.9 },
    { account: 'Grand Hotels & Resorts Ltd', amount: 250000, percentage: 22.7 },
    { account: 'United Oil & Gas Corp.', amount: 180000, percentage: 16.4 },
    { account: 'University of Arizona', amount: 90000, percentage: 8.2 },
    { account: 'Other', amount: 310000, percentage: 28.2 }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white -mx-8 shadow-sm border-b border-gray-200">
        <div className="px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sales Forecast Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">
                Dashboard for sales team to track past sales and future sales by amount, close date, status, country, and lead source.
              </p>
              <p className="text-xs text-gray-500 mt-1">
                As of Apr 22, 2023, 2:30 PM | Viewing as Gillian Bruce
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                <Settings className="h-4 w-4 mr-2" />
                Edit
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                Subscribe
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="py-6">
        {/* Top Row - Main Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-6 gap-6 mb-6">
          {/* Sales by Quarter */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow border h-full">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Sales by Quarter</h3>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500">Sum of Amount</div>
                  <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                    <span>$0</span>
                    <span>$200k</span>
                    <span>$400k</span>
                    <span>$600k</span>
                    <span>$1M</span>
                    <span>$1.4k</span>
                    <span>$1.6k</span>
                  </div>
                </div>
              </div>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={salesByQuarterData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tickFormatter={formatChartNumber} />
                    <YAxis dataKey="quarter" type="category" width={60} />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Bar dataKey="amount" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
                <div className="mt-2 text-center">
                  <button className="text-blue-600 text-xs hover:underline">
                    View Report (Closed Won Opportunities by Quarter)
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Potential Sales by Stage */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow border h-full">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Potential Sales by Stage</h3>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500">Sum of Amount: $2.1M</div>
                </div>
              </div>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={potentialSalesByStageData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                      label={({ percentage }) => `${percentage}%`}
                    >
                      {potentialSalesByStageData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-2 grid grid-cols-2 gap-1">
                  {potentialSalesByStageData.slice(0, 4).map((item, index) => (
                    <div key={item.stage} className="flex items-center text-xs">
                      <div
                        className="w-3 h-3 rounded mr-2"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <span className="text-gray-600 truncate">{item.stage}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-2 text-center">
                  <button className="text-blue-600 text-xs hover:underline">
                    View Report (Opportunities by Stage)
                  </button>
                </div>
              </div>
            </div>
          </div>

            <div className="lg:col-span-2 space-y-4">
                {/* Total Sales */}
                <div className="">
                    <div className="bg-white rounded-lg shadow border">
                        <div className="p-3 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-medium text-gray-900">Total Sales</h3>
                                <button className="text-gray-400 hover:text-gray-600">
                                    <Settings className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                        <div className="p-4 flex flex-col items-center justify-center h-full">
                            <div className="text-center">
                                <div className="text-3xl font-bold text-green-600 mb-2">
                                  {analyticsData?.summary?.total_sales ? formatChartNumber(analyticsData.summary.total_sales) : '$4.2M'}
                                </div>
                                <div className="text-xs text-gray-500 mb-3">Closed Won</div>
                                <div className="space-y-1">
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-green-500 rounded mr-2"></div>
                                        <span>Closed Won</span>
                                    </div>
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-blue-500 rounded mr-2"></div>
                                        <span>Revenue Recognized</span>
                                    </div>
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-purple-500 rounded mr-2"></div>
                                        <span>Completed Projects</span>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-3 text-center">
                                <button className="text-blue-600 text-xs hover:underline">
                                    View Report (Closed Won Revenue by Quarter)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Total Potential Sales */}
                <div className="">
                    <div className="bg-white rounded-lg shadow border">
                        <div className="p-3 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-medium text-gray-900">Total Potential Sales</h3>
                                <button className="text-gray-400 hover:text-gray-600">
                                    <Settings className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                        <div className="p-4 flex flex-col items-center justify-center h-full">
                            <div className="text-center">
                                <div className="text-3xl font-bold text-blue-600 mb-2">
                                  {analyticsData?.summary?.total_pipeline ? formatChartNumber(analyticsData.summary.total_pipeline) : '$21.4M'}
                                </div>
                                <div className="text-xs text-gray-500 mb-3">Pipeline Stages</div>
                                <div className="space-y-1">
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-blue-500 rounded mr-2"></div>
                                        <span>Prospecting</span>
                                    </div>
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-yellow-500 rounded mr-2"></div>
                                        <span>Qualification</span>
                                    </div>
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-orange-500 rounded mr-2"></div>
                                        <span>Proposal</span>
                                    </div>
                                    <div className="flex items-center text-xs">
                                        <div className="w-2 h-2 bg-purple-500 rounded mr-2"></div>
                                        <span>Negotiation</span>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-3 text-center">
                                <button className="text-blue-600 text-xs hover:underline">
                                    View Report (Opportunities by Stage)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Lead Performance Row */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          {/* Lead Performance Analytics */}
          <div className="lg:col-span-4">
            <div className="bg-white rounded-lg shadow border">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Lead Performance Analytics</h3>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500">Lead Generation & Conversion Metrics</div>
                </div>
              </div>
              <div className="p-6">
                {(() => {
                  // Calculate lead performance metrics
                  const currentMonth = analyticsData?.monthly_trends?.[analyticsData.monthly_trends.length - 1];
                  const previousMonth = analyticsData?.monthly_trends?.[analyticsData.monthly_trends.length - 2];

                  const currentContacts = currentMonth?.contacts || 0;
                  const previousContacts = previousMonth?.contacts || 0;
                  const contactsGrowth = previousContacts > 0 ? ((currentContacts - previousContacts) / previousContacts * 100) : 0;

                  const currentDeals = currentMonth?.deals || 0;
                  const previousDeals = previousMonth?.deals || 0;
                  const dealsGrowth = previousDeals > 0 ? ((currentDeals - previousDeals) / previousDeals * 100) : 0;

                  const currentRevenue = currentMonth?.revenue || 0;
                  const previousRevenue = previousMonth?.revenue || 0;
                  const revenueGrowth = previousRevenue > 0 ? ((currentRevenue - previousRevenue) / previousRevenue * 100) : 0;

                  // Calculate conversion rates
                  const leadToQualifiedRate = currentContacts > 0 ? (currentDeals / currentContacts * 100) : 0;
                  const qualifiedToConvertedRate = currentDeals > 0 ? (currentRevenue > 0 ? 100 : 0) : 0;

                  // Calculate average deal size for current month
                  const avgDealSize = currentDeals > 0 ? (currentRevenue / currentDeals) : 0;

                  // Calculate total metrics for the period
                  const totalContacts = analyticsData?.monthly_trends?.reduce((sum, month) => sum + month.contacts, 0) || 0;
                  const totalDeals = analyticsData?.monthly_trends?.reduce((sum, month) => sum + month.deals, 0) || 0;
                  const totalRevenue = analyticsData?.monthly_trends?.reduce((sum, month) => sum + month.revenue, 0) || 0;

                  return (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                      {/* New Leads */}
                      <div className="text-center">
                        <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mx-auto mb-3">
                          <Users className="h-6 w-6 text-blue-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">{currentContacts}</div>
                        <div className="text-sm text-gray-600 mb-2">New Leads</div>
                        <div className={`flex items-center justify-center text-xs ${contactsGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {contactsGrowth >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                          {Math.abs(contactsGrowth).toFixed(1)}% vs last month
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Total: {totalContacts}</div>
                      </div>

                      {/* Qualified Leads */}
                      <div className="text-center">
                        <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mx-auto mb-3">
                          <Target className="h-6 w-6 text-green-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">{currentDeals}</div>
                        <div className="text-sm text-gray-600 mb-2">Qualified Leads</div>
                        <div className={`flex items-center justify-center text-xs ${dealsGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {dealsGrowth >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                          {Math.abs(dealsGrowth).toFixed(1)}% vs last month
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Total: {totalDeals}</div>
                      </div>

                      {/* Converted Revenue */}
                      <div className="text-center">
                        <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full mx-auto mb-3">
                          <DollarSign className="h-6 w-6 text-purple-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">{formatChartNumber(currentRevenue)}</div>
                        <div className="text-sm text-gray-600 mb-2">Monthly Revenue</div>
                        <div className={`flex items-center justify-center text-xs ${revenueGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {revenueGrowth >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                          {Math.abs(revenueGrowth).toFixed(1)}% vs last month
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Total: {formatCurrency(totalRevenue)}</div>
                      </div>

                      {/* Conversion Rates */}
                      <div className="text-center">
                        <div className="space-y-4">
                          <div>
                            <div className="text-lg font-bold text-gray-900">{leadToQualifiedRate.toFixed(1)}%</div>
                            <div className="text-xs text-gray-600">Lead → Qualified</div>
                            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${Math.min(leadToQualifiedRate, 100)}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="text-lg font-bold text-gray-900">{analyticsData?.summary?.win_rate ? (analyticsData.summary.win_rate * 100).toFixed(1) : '23.0'}%</div>
                            <div className="text-xs text-gray-600">Win Rate</div>
                            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                              <div
                                className="bg-green-600 h-2 rounded-full"
                                style={{ width: `${analyticsData?.summary?.win_rate ? analyticsData.summary.win_rate * 100 : 23}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Performance Insights */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {(() => {
                      const currentMonth = analyticsData?.monthly_trends?.[analyticsData.monthly_trends.length - 1];
                      const avgDealSize = currentMonth?.deals > 0 ? (currentMonth.revenue / currentMonth.deals) : 0;
                      const totalPipelineValue = analyticsData?.summary?.total_pipeline || 0;
                      const avgDealSizeOverall = analyticsData?.summary?.avg_deal_size || 0;

                      return (
                        <>
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-lg font-semibold text-gray-900">{formatCurrency(avgDealSize)}</div>
                            <div className="text-sm text-gray-600">Avg Deal Size (Current)</div>
                            <div className="text-xs text-gray-500 mt-1">
                              Overall: {formatCurrency(avgDealSizeOverall)}
                            </div>
                          </div>
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-lg font-semibold text-gray-900">{formatChartNumber(totalPipelineValue)}</div>
                            <div className="text-sm text-gray-600">Total Pipeline Value</div>
                            <div className="text-xs text-gray-500 mt-1">
                              Active opportunities
                            </div>
                          </div>
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-lg font-semibold text-gray-900">
                              {analyticsData?.summary?.total_contacts || 0}
                            </div>
                            <div className="text-sm text-gray-600">Total Contacts</div>
                            <div className="text-xs text-gray-500 mt-1">
                              All time leads
                            </div>
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>

                {/* Trend Chart */}
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-4">3-Month Trend</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={analyticsData?.monthly_trends?.slice(-3) || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip
                        formatter={(value, name) => {
                          if (name === 'revenue') return [formatCurrency(value), 'Revenue'];
                          return [value, name === 'contacts' ? 'New Leads' : 'Qualified Leads'];
                        }}
                      />
                      <Line yAxisId="left" type="monotone" dataKey="contacts" stroke="#3B82F6" strokeWidth={2} name="contacts" />
                      <Line yAxisId="left" type="monotone" dataKey="deals" stroke="#10B981" strokeWidth={2} name="deals" />
                      <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#8B5CF6" strokeWidth={2} name="revenue" />
                    </LineChart>
                  </ResponsiveContainer>
                  <div className="flex justify-center space-x-6 mt-2">
                    <div className="flex items-center text-xs">
                      <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                      <span>New Leads</span>
                    </div>
                    <div className="flex items-center text-xs">
                      <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                      <span>Qualified Leads</span>
                    </div>
                    <div className="flex items-center text-xs">
                      <div className="w-3 h-3 bg-purple-500 rounded mr-2"></div>
                      <span>Revenue</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Row - Additional Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Sales & Potential Sales by Country */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow border h-96">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Sales & Potential Sales by Country</h3>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500">Sum of Amount</div>
                </div>
              </div>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={150}>
                  <PieChart>
                    <Pie
                      data={salesByCountryData}
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      fill="#8884d8"
                      dataKey="amount"
                      label={({ percentage }) => `${percentage}%`}
                    >
                      {salesByCountryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-2 text-center text-xl font-bold text-teal-600">
                  {salesByCountryData.length > 0 ? formatChartNumber(salesByCountryData.reduce((sum, item) => sum + item.amount, 0)) : '$10.8M'}
                </div>
                <div className="mt-2 space-y-1 max-h-20 overflow-y-auto">
                  {salesByCountryData.slice(0, 4).map((item, index) => (
                    <div key={item.country} className="flex items-center justify-between text-xs">
                      <div className="flex items-center min-w-0 flex-1">
                        <div
                          className="w-2 h-2 rounded mr-2 flex-shrink-0"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        ></div>
                        <span className="text-gray-600 truncate">{item.country}</span>
                      </div>
                      <span className="text-gray-900 ml-2 flex-shrink-0">{formatChartNumber(item.amount)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Sales & Potential Sales by Lead Source */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow border h-96">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Sales & Potential Sales by Lead Source</h3>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500">Sum of Amount</div>
                </div>
              </div>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={salesByLeadSourceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="source" angle={-45} textAnchor="end" height={80} />
                    <YAxis tickFormatter={formatChartNumber} />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Bar dataKey="amount" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Expected Revenue by Account */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow border h-96">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Expected Revenue by Account</h3>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500">Sum of Expected Revenue</div>
                </div>
              </div>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={120}>
                  <PieChart>
                    <Pie
                      data={expectedRevenueByAccountData}
                      cx="50%"
                      cy="50%"
                      outerRadius={50}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {expectedRevenueByAccountData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-2 text-center text-xl font-bold text-teal-600">$1.1M</div>
                <div className="mt-2 space-y-1 max-h-24 overflow-y-auto">
                  {expectedRevenueByAccountData.slice(0, 4).map((item, index) => (
                    <div key={item.account} className="flex items-center justify-between text-xs">
                      <div className="flex items-center min-w-0 flex-1">
                        <div
                          className="w-2 h-2 rounded mr-2 flex-shrink-0"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        ></div>
                        <span className="text-gray-600 truncate">{item.account}</span>
                      </div>
                      <span className="text-gray-900 ml-2 flex-shrink-0">{formatChartNumber(item.amount)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>


      </div>
    </div>
  );
};

export default Dashboard;