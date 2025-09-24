import React, { useState, useEffect } from 'react';
import { 
  Target, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Calendar, 
  Globe, 
  Lightbulb,
  FileText,
  Download,
  Save,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';
import { sprintAPI } from '../services/api';
import { toast } from 'react-hot-toast';

const CampaignBuilder = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [builderData, setBuilderData] = useState(null);
  const [campaignGoals, setCampaignGoals] = useState({
    campaign_type: 'Lead Generation',
    target_solution: '',
    budget_min: 10000,
    budget_max: 50000,
    timeline: '3 months',
    lead_target: 100,
    revenue_target: 500000,
    geographic_focus: 'Global',
    target_audience: 'B2B Technology Companies'
  });
  const [historicalAnalysis, setHistoricalAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [campaignTemplate, setCampaignTemplate] = useState(null);

  const steps = [
    { id: 1, title: 'Campaign Goals', icon: Target },
    { id: 2, title: 'Historical Analysis', icon: TrendingUp },
    { id: 3, title: 'AI Recommendations', icon: Lightbulb },
    { id: 4, title: 'Campaign Template', icon: FileText }
  ];

  useEffect(() => {
    fetchBuilderData();
  }, []);

  const fetchBuilderData = async () => {
    try {
      setLoading(true);
      const response = await sprintAPI.getCampaignBuilderData();
      setBuilderData(response.data);
    } catch (error) {
      console.error('Error fetching builder data:', error);
      toast.error('Failed to load campaign builder data');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalAnalysis = async () => {
    try {
      setLoading(true);
      const response = await sprintAPI.getHistoricalAnalysis({ date_range: '90d' });
      setHistoricalAnalysis(response.data.historical_analysis);
      toast.success('Historical analysis completed');
    } catch (error) {
      console.error('Error fetching historical analysis:', error);
      toast.error('Failed to analyze historical data');
    } finally {
      setLoading(false);
    }
  };

  const generateRecommendations = async () => {
    try {
      setLoading(true);
      const response = await sprintAPI.generateAICampaignSuggestions(campaignGoals);
      setRecommendations(response.data.recommendations);
      toast.success('AI recommendations generated');
    } catch (error) {
      console.error('Error generating recommendations:', error);
      toast.error('Failed to generate AI recommendations');
    } finally {
      setLoading(false);
    }
  };

  const generateTemplate = async () => {
    try {
      setLoading(true);
      const response = await sprintAPI.generateCampaignTemplate({
        campaign_goals: campaignGoals,
        recommendations: recommendations
      });
      setCampaignTemplate(response.data.campaign_template);
      toast.success('Campaign template generated');
    } catch (error) {
      console.error('Error generating template:', error);
      toast.error('Failed to generate campaign template');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (currentStep === 1) {
      // Validate campaign goals
      if (!campaignGoals.campaign_type || !campaignGoals.budget_max || !campaignGoals.lead_target) {
        toast.error('Please fill in all required fields');
        return;
      }
      setCurrentStep(2);
      await fetchHistoricalAnalysis();
    } else if (currentStep === 2) {
      setCurrentStep(3);
      await generateRecommendations();
    } else if (currentStep === 3) {
      setCurrentStep(4);
      await generateTemplate();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleGoalChange = (field, value) => {
    setCampaignGoals(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading && !builderData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading Campaign Builder...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">AI Campaign Builder</h1>
                <p className="mt-2 text-gray-600">
                  Create data-driven marketing campaigns with AI-powered recommendations
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <button className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                  <Save className="h-4 w-4 mr-2" />
                  Save Draft
                </button>
                {campaignTemplate && (
                  <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
                    <Download className="h-4 w-4 mr-2" />
                    Export Template
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isCompleted = currentStep > step.id;
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isCompleted 
                      ? 'bg-green-600 border-green-600 text-white'
                      : isActive
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white border-gray-300 text-gray-400'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="h-6 w-6" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="ml-3">
                    <p className={`text-sm font-medium ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-4 ${
                      isCompleted ? 'bg-green-600' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow">
          {currentStep === 1 && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Define Campaign Goals</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Campaign Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campaign Type *
                  </label>
                  <select
                    value={campaignGoals.campaign_type}
                    onChange={(e) => handleGoalChange('campaign_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {builderData?.campaign_types?.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Target Solution */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Solution
                  </label>
                  <select
                    value={campaignGoals.target_solution}
                    onChange={(e) => handleGoalChange('target_solution', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Any Solution</option>
                    {builderData?.available_solution_types?.map(solution => (
                      <option key={solution} value={solution}>{solution}</option>
                    ))}
                  </select>
                </div>

                {/* Budget Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget Range *
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      placeholder="Min Budget"
                      value={campaignGoals.budget_min}
                      onChange={(e) => handleGoalChange('budget_min', parseInt(e.target.value) || 0)}
                      className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      placeholder="Max Budget"
                      value={campaignGoals.budget_max}
                      onChange={(e) => handleGoalChange('budget_max', parseInt(e.target.value) || 0)}
                      className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Timeline */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timeline
                  </label>
                  <select
                    value={campaignGoals.timeline}
                    onChange={(e) => handleGoalChange('timeline', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {builderData?.timeline_options?.map(timeline => (
                      <option key={timeline} value={timeline}>{timeline}</option>
                    ))}
                  </select>
                </div>

                {/* Lead Target */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Lead Target *
                  </label>
                  <input
                    type="number"
                    placeholder="Number of leads"
                    value={campaignGoals.lead_target}
                    onChange={(e) => handleGoalChange('lead_target', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Revenue Target */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Revenue Target
                  </label>
                  <input
                    type="number"
                    placeholder="Expected revenue"
                    value={campaignGoals.revenue_target}
                    onChange={(e) => handleGoalChange('revenue_target', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Geographic Focus */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Geographic Focus
                  </label>
                  <select
                    value={campaignGoals.geographic_focus}
                    onChange={(e) => handleGoalChange('geographic_focus', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {builderData?.geographic_options?.map(geo => (
                      <option key={geo} value={geo}>{geo}</option>
                    ))}
                  </select>
                </div>

                {/* Target Audience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    placeholder="Describe your target audience"
                    value={campaignGoals.target_audience}
                    onChange={(e) => handleGoalChange('target_audience', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Historical Analysis</h2>

              {historicalAnalysis ? (
                <div className="space-y-6">
                  {/* Key Insights */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-blue-900 mb-3">Key Insights</h3>
                    <ul className="space-y-2">
                      {historicalAnalysis.key_insights?.map((insight, index) => (
                        <li key={index} className="flex items-start">
                          <CheckCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-blue-800">{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Top Performing Sources */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Top Performing Lead Sources</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {historicalAnalysis.top_performing_sources?.slice(0, 3).map((source, index) => (
                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-900">{source.source}</h4>
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              source.performance_rating === 'High'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {source.performance_rating}
                            </span>
                          </div>
                          <div className="space-y-1 text-sm text-gray-600">
                            <p>Conversion Rate: {source.conversion_rate?.toFixed(1)}%</p>
                            <p>Total Leads: {source.total_leads}</p>
                            <p>Avg Deal Size: {formatCurrency(source.avg_deal_size || 0)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Solution Demand Trends */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Solution Demand Trends</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {historicalAnalysis.solution_demand_trends?.slice(0, 6).map((solution, index) => (
                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-2">{solution.solution}</h4>
                          <div className="space-y-1 text-sm text-gray-600">
                            <p>Leads: {solution.leads}</p>
                            <p>Market Share: {solution.percentage?.toFixed(1)}%</p>
                            <p>Demand: {solution.market_demand}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-green-900 mb-3">Strategic Recommendations</h3>
                    <ul className="space-y-2">
                      {historicalAnalysis.recommendations?.map((recommendation, index) => (
                        <li key={index} className="flex items-start">
                          <Lightbulb className="h-5 w-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-green-800">{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
                  <p className="text-gray-600">Analyzing historical campaign data...</p>
                </div>
              )}
            </div>
          )}

          {currentStep === 3 && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Campaign Recommendations</h2>

              {recommendations ? (
                <div className="space-y-6">
                  {/* Target Audience */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                      <Users className="h-5 w-5 text-blue-600 mr-2" />
                      Target Audience Strategy
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Primary Segment</h4>
                        <p className="text-gray-600">{recommendations.target_audience?.primary_segment}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Company Size</h4>
                        <p className="text-gray-600">{recommendations.target_audience?.company_size}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Industries</h4>
                        <p className="text-gray-600">{recommendations.target_audience?.industries?.join(', ')}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Job Titles</h4>
                        <p className="text-gray-600">{recommendations.target_audience?.job_titles?.join(', ')}</p>
                      </div>
                    </div>
                  </div>

                  {/* Channel Strategy */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                      <Target className="h-5 w-5 text-green-600 mr-2" />
                      Channel Strategy & Budget Allocation
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Primary Channels</h4>
                        <div className="flex flex-wrap gap-2">
                          {recommendations.channel_strategy?.primary_channels?.map((channel, index) => (
                            <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                              {channel}
                            </span>
                          ))}
                        </div>
                      </div>

                      {recommendations.channel_strategy?.budget_allocation && (
                        <div>
                          <h4 className="font-medium text-gray-700 mb-2">Budget Allocation</h4>
                          <div className="space-y-2">
                            {Object.entries(recommendations.channel_strategy.budget_allocation).map(([channel, allocation]) => (
                              <div key={channel} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                <span className="text-gray-700">{channel}</span>
                                <div className="text-right">
                                  <span className="font-medium">{allocation.percentage?.toFixed(1)}%</span>
                                  <span className="text-gray-500 ml-2">({formatCurrency(allocation.budget || 0)})</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Messaging Strategy */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                      <FileText className="h-5 w-5 text-purple-600 mr-2" />
                      Messaging Strategy
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Primary Theme</h4>
                        <p className="text-gray-600">{recommendations.messaging_strategy?.primary_theme}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Value Propositions</h4>
                        <ul className="list-disc list-inside space-y-1 text-gray-600">
                          {recommendations.messaging_strategy?.value_propositions?.map((prop, index) => (
                            <li key={index}>{prop}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Content Themes</h4>
                        <div className="flex flex-wrap gap-2">
                          {recommendations.messaging_strategy?.content_themes?.map((theme, index) => (
                            <span key={index} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                              {theme}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Success Metrics */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                      <TrendingUp className="h-5 w-5 text-orange-600 mr-2" />
                      Success Metrics & KPIs
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Primary KPIs</h4>
                        <ul className="list-disc list-inside space-y-1 text-gray-600">
                          {recommendations.success_metrics?.primary_kpis?.map((kpi, index) => (
                            <li key={index}>{kpi}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Tracking Metrics</h4>
                        <ul className="list-disc list-inside space-y-1 text-gray-600">
                          {recommendations.success_metrics?.tracking_metrics?.map((metric, index) => (
                            <li key={index}>{metric}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
                  <p className="text-gray-600">Generating AI-powered recommendations...</p>
                </div>
              )}
            </div>
          )}

          {currentStep === 4 && (
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Campaign Template</h2>

              {campaignTemplate ? (
                <div className="space-y-6">
                  {/* Campaign Overview */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-blue-900 mb-4">Campaign Overview</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-blue-700 mb-1">Campaign Name</h4>
                        <p className="text-blue-800">{campaignTemplate.campaign_overview?.name}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-blue-700 mb-1">Duration</h4>
                        <p className="text-blue-800">{campaignTemplate.campaign_overview?.duration}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-blue-700 mb-1">Budget</h4>
                        <p className="text-blue-800">{formatCurrency(campaignTemplate.campaign_overview?.budget || 0)}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-blue-700 mb-1">Objective</h4>
                        <p className="text-blue-800">{campaignTemplate.campaign_overview?.objective}</p>
                      </div>
                    </div>
                  </div>

                  {/* Campaign Phases */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Campaign Phases</h3>
                    <div className="space-y-4">
                      {campaignTemplate.campaign_phases?.map((phase, index) => (
                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-3">
                            <h4 className="font-medium text-gray-900">{phase.phase_name}</h4>
                            <div className="text-right">
                              <span className="text-sm text-gray-500">{phase.duration}</span>
                              <p className="text-sm font-medium text-gray-700">
                                {formatCurrency(phase.budget_allocation || 0)}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h5 className="font-medium text-gray-700 mb-2">Activities</h5>
                              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                                {phase.activities?.map((activity, actIndex) => (
                                  <li key={actIndex}>{activity}</li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <h5 className="font-medium text-gray-700 mb-2">Deliverables</h5>
                              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                                {phase.deliverables?.map((deliverable, delIndex) => (
                                  <li key={delIndex}>{deliverable}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Team Requirements */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Team Requirements</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {campaignTemplate.team_requirements?.map((role, index) => (
                        <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900">{role.role}</h4>
                          <p className="text-sm text-gray-600">{role.allocation}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Success Message */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <CheckCircle className="h-6 w-6 text-green-600 mr-3" />
                      <div>
                        <h3 className="text-lg font-medium text-green-900">Campaign Template Ready!</h3>
                        <p className="text-green-700">
                          Your AI-powered campaign template has been generated successfully.
                          You can now export it or save it for future use.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
                  <p className="text-gray-600">Creating comprehensive campaign template...</p>
                </div>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium ${
                currentStep === 1
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </button>
            
            <button
              onClick={handleNext}
              disabled={loading || currentStep === 4}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium ${
                loading || currentStep === 4
                  ? 'text-gray-400 cursor-not-allowed bg-gray-200'
                  : 'text-white bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? (
                <>
                  <Loader className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : currentStep === 4 ? (
                'Complete'
              ) : (
                <>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CampaignBuilder;
