import React, { useState, useEffect } from 'react';
import {
  RefreshCw,
  Download,
  Settings
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
  Cell
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

  const salesByRegionData = analyticsData?.region_analysis?.map((item, index) => {
    const total = analyticsData?.summary?.total_pipeline || 1;
    return {
      region: item.region,
      amount: item.amount,
      percentage: ((item.amount / total) * 100).toFixed(1)
    };
  }).filter(item => item.amount > 0) || [
    { region: 'East Coast', amount: 899000, percentage: 15.4 },
    { region: 'Midwest', amount: 480000, percentage: 8.2 },
    { region: 'Southwest', amount: 337000, percentage: 5.8 },
    { region: 'West Coast', amount: 4284000, percentage: 73.4 }
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
              <h1 className="text-2xl font-bold text-gray-900">Sales Team Dream Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">
                Dashboard for sales team to track past sales and future sales by amount, close date, status, region, and lead source.
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

        {/* Bottom Row - Additional Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Sales & Potential Sales by Region */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow border h-96">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Sales & Potential Sales by Region</h3>
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
                      data={salesByRegionData}
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      fill="#8884d8"
                      dataKey="amount"
                      label={({ percentage }) => `${percentage}%`}
                    >
                      {salesByRegionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-2 text-center text-xl font-bold text-teal-600">$5.8M</div>
                <div className="mt-2 space-y-1 max-h-20 overflow-y-auto">
                  {salesByRegionData.slice(0, 4).map((item, index) => (
                    <div key={item.region} className="flex items-center justify-between text-xs">
                      <div className="flex items-center min-w-0 flex-1">
                        <div
                          className="w-2 h-2 rounded mr-2 flex-shrink-0"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        ></div>
                        <span className="text-gray-600 truncate">{item.region}</span>
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