import React, { useState, useEffect } from 'react';
import {
  X,
  User,
  Calendar,
  DollarSign,
  Phone,
  Mail,
  Building,
  Clock,
  MessageSquare,
  Target,
  Settings,
  FileText,
  Brain,
  Activity,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  Circle,
  TrendingUp,
  BarChart3,
  Users,
  Percent,
  Euro,
  ArrowRight,
  Send,
  Trash2
} from 'lucide-react';
import { sprintAPI } from '../services/api';
import toast from 'react-hot-toast';

const DealDetailModal = ({ dealId, isOpen, onClose }) => {
  const [dealData, setDealData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [isPostingComment, setIsPostingComment] = useState(false);

  useEffect(() => {
    if (isOpen && dealId) {
      fetchDealDetails();
    }
  }, [isOpen, dealId]);

  const fetchDealDetails = async () => {
    try {
      setLoading(true);
      const response = await sprintAPI.getDealDetailed(dealId);
      setDealData(response.data);
      setComments(response.data.comments || []);
    } catch (error) {
      console.error('Error fetching deal details:', error);
      toast.error('Failed to load deal details');
    } finally {
      setLoading(false);
    }
  };

  const triggerAIInsight = async () => {
    if (!dealData?.deal) return;
    
    try {
      setLoading(true);
      const analysisMessage = getAnalysisMessage(dealData.deal.status);
      toast.loading(analysisMessage, { id: 'ai-analysis' });
      
      await sprintAPI.triggerAIInsight(dealData.deal.id, dealData.deal.status);
      
      // Refresh deal details to get the latest AI insights
      await fetchDealDetails();
      
      toast.success('AI analysis completed', { id: 'ai-analysis' });
      
      // Switch to AI insights tab to show results
      setActiveTab('ai-insights');
    } catch (error) {
      console.error('Error triggering AI insight:', error);
      toast.error('Failed to generate AI insights', { id: 'ai-analysis' });
    } finally {
      setLoading(false);
    }
  };

  const getAnalysisMessage = (status) => {
    switch (status) {
      case 'lead': return 'Analyzing lead qualification...';
      case 'qualified_solution': return 'Designing technical solution...';
      case 'qualified_delivery': return 'Planning delivery strategy...';
      case 'qualified_cso': return 'Generating commercial proposal...';
      default: return 'Running AI analysis...';
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'Not specified';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      lead: 'bg-gray-100 text-gray-800',
      qualified_solution: 'bg-blue-100 text-blue-800',
      qualified_delivery: 'bg-yellow-100 text-yellow-800',
      qualified_cso: 'bg-purple-100 text-purple-800',
      deal: 'bg-green-100 text-green-800',
      project: 'bg-indigo-100 text-indigo-800'
    };
    return colors[status] || colors.lead;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      urgent: 'bg-red-100 text-red-800'
    };
    return colors[priority] || colors.medium;
  };

  const handlePostComment = async () => {
    if (!newComment.trim() || !dealData?.deal?.id) return;

    try {
      setIsPostingComment(true);

      // For now, we'll use a default commenter name and role
      // In a real app, this would come from the authenticated user
      const commentData = {
        deal_id: dealData.deal.id,
        commenter_name: 'Current User', // This should come from auth context
        commenter_role: 'Sales', // This should come from auth context
        comment_text: newComment.trim()
      };

      const response = await sprintAPI.createComment(dealData.deal.id, commentData);

      // Add the new comment to the local state
      setComments(prevComments => [response.data, ...prevComments]);
      setNewComment('');

      toast.success('Comment posted successfully');
    } catch (error) {
      console.error('Error posting comment:', error);
      toast.error('Failed to post comment');
    } finally {
      setIsPostingComment(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    try {
      await sprintAPI.deleteComment(commentId);

      // Remove the comment from local state
      setComments(prevComments => prevComments.filter(comment => comment.id !== commentId));

      toast.success('Comment deleted successfully');
    } catch (error) {
      console.error('Error deleting comment:', error);
      toast.error('Failed to delete comment');
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Circle },
    { id: 'conversation', label: 'Conversation', icon: MessageSquare },
    { id: 'technical', label: 'Technical', icon: Settings },
    { id: 'ai-insights', label: 'AI Insights', icon: Brain },
    { id: 'timeline', label: 'Timeline', icon: Activity },
    { id: 'resources', label: 'Resources', icon: User },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full h-full flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {dealData?.deal?.title || 'Deal Details'}
              </h2>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  dealData?.deal ? getStatusColor(dealData.deal.status) : ''
                }`}>
                  {dealData?.deal?.status?.replace('_', ' ')?.toUpperCase()}
                </span>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  dealData?.deal ? getPriorityColor(dealData.deal.priority) : ''
                }`}>
                  {dealData?.deal?.priority?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : dealData ? (
          <>
            {/* Tabs */}
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8 px-6">
                {tabs.map((tab) => {
                  const IconComponent = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <IconComponent className="h-4 w-4" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Content */}
            <div className="p-6 flex-1 pb-8 overflow-y-auto">
              {activeTab === 'overview' && <OverviewTab
                dealData={dealData}
                formatCurrency={formatCurrency}
                formatDate={formatDate}
                comments={comments}
                newComment={newComment}
                setNewComment={setNewComment}
                handlePostComment={handlePostComment}
                handleDeleteComment={handleDeleteComment}
                isPostingComment={isPostingComment}
              />}
              {activeTab === 'conversation' && <ConversationTab dealData={dealData} />}
              {activeTab === 'technical' && <TechnicalTab dealData={dealData} />}
              {activeTab === 'ai-insights' && <AIInsightsTab dealData={dealData} triggerAIInsight={triggerAIInsight} loading={loading} />}
              {activeTab === 'timeline' && <TimelineTab dealData={dealData} />}
              {activeTab === 'resources' && <ResourcesTab dealData={dealData} />}
            </div>
          </>
        ) : (
          <div className="p-6 text-center text-gray-500">
            Failed to load deal details
          </div>
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ dealData, formatCurrency, formatDate, comments, newComment, setNewComment, handlePostComment, handleDeleteComment, isPostingComment }) => {
  const { deal, conversation_data, activity_summary } = dealData;

  return (
    <div className="grid grid-cols-1 gap-6">
      {/* Basic Information */}
      <div className="space-y-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Building className="h-4 w-4 mr-2" />
            Customer Information
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Company:</span>
              <span className="font-medium">{deal.customer_name || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email:</span>
              <span className="font-medium">{deal.customer_email || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Contact Person:</span>
              <span className="font-medium">{deal.contact_person || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Decision Makers:</span>
              <span className="font-medium">{deal.decision_makers || 'Not specified'}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <DollarSign className="h-4 w-4 mr-2" />
            Financial Information
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Estimated Value:</span>
              <span className="font-medium">{formatCurrency(deal.estimated_value)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Budget Range:</span>
              <span className="font-medium">
                {deal.budget_range_min && deal.budget_range_max 
                  ? `${formatCurrency(deal.budget_range_min)} - ${formatCurrency(deal.budget_range_max)}`
                  : 'Not specified'
                }
              </span>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <User className="h-4 w-4 mr-2" />
            Assignment & Timeline
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Contact owner:</span>
              <span className="font-medium">{deal.assigned_person?.name || 'Unassigned'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Region:</span>
              <span className="font-medium">{deal.region || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Country:</span>
              <span className="font-medium">{deal.country || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Expected Close:</span>
              <span className="font-medium">{formatDate(deal.expected_close_date)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Days Active:</span>
              <span className="font-medium">{activity_summary?.days_since_creation || 0} days</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Deal Overview
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Solution Owner:</span>
              <span className="font-medium">{deal.solution_owner?.name || 'Not assigned'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Velocity:</span>
              <span className="font-medium">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  deal.velocity === 'Fast' ? 'bg-green-100 text-green-800' :
                  deal.velocity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                  deal.velocity === 'Slow' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {deal.velocity || 'Not specified'}
                </span>
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Deal Stage:</span>
              <span className="font-medium">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  deal.deal_stage === 'Closed Won' ? 'bg-green-100 text-green-800' :
                  deal.deal_stage === 'Closed Lost' ? 'bg-red-100 text-red-800' :
                  deal.deal_stage === 'Negotiation' ? 'bg-blue-100 text-blue-800' :
                  deal.deal_stage === 'Proposal' ? 'bg-purple-100 text-purple-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {deal.deal_stage || 'Not specified'}
                </span>
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Deal Probability:</span>
              <span className="font-medium flex items-center">
                <Percent className="h-3 w-3 mr-1" />
                {deal.deal_probability ? `${deal.deal_probability}%` : 'Not specified'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Weighted Amount:</span>
              <span className="font-medium flex items-center">
                <Euro className="h-3 w-3 mr-1" />
                {deal.weighted_amount ? `€${deal.weighted_amount.toLocaleString()}` : 'Not calculated'}
              </span>
            </div>


          </div>
        </div>
      </div>

      {/* Description & Requirements */}
      <div className="space-y-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3">Deal Description</h3>
          <p className="text-sm text-gray-700">
            {deal.deal_description || deal.description || 'No description provided'}
          </p>
        </div>

        {conversation_data && (
          <>
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                <Target className="h-4 w-4 mr-2" />
                Business Goals
              </h3>
              <p className="text-sm text-gray-700">
                {conversation_data.business_goals || 'Not specified'}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                <AlertCircle className="h-4 w-4 mr-2" />
                Pain Points
              </h3>
              <p className="text-sm text-gray-700">
                {conversation_data.pain_points || 'Not specified'}
              </p>
            </div>
          </>
        )}

          {/* Comments Section */}
          <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Comments
              </h3>

              {/* Add Comment Form */}
              <div className="space-y-3">
            <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add your comment..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="3"
            />
                  <button
                      onClick={handlePostComment}
                      disabled={!newComment.trim() || isPostingComment}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                      <Send className="h-4 w-4 mr-2" />
                      {isPostingComment ? 'Posting...' : 'Post Comment'}
                  </button>
              </div>

              {/* Comments List */}
              <div className="space-y-3 mt-4">
                  {comments && comments.length > 0 ? (
                      comments.map((comment, index) => (
                          <div key={comment.id || index} className="bg-white rounded-lg p-3 border border-gray-200 group">
                              <div className="flex justify-between items-start mb-2">
                                  <div className="flex items-center space-x-2">
                                      <span className="font-medium text-sm text-gray-900">{comment.commenter_name}</span>
                                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {comment.commenter_role}
                      </span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                      <span className="text-xs text-gray-500">
                        {new Date(comment.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                      </span>
                                      <button
                                          onClick={() => handleDeleteComment(comment.id)}
                                          className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                                          title="Delete comment"
                                      >
                                          <Trash2 className="h-3 w-3" />
                                      </button>
                                  </div>
                              </div>
                              <p className="text-sm text-gray-700">{comment.comment_text}</p>
                          </div>
                      ))
                  ) : (
                      <p className="text-sm text-gray-500 italic">No comments yet</p>
                  )}
              </div>


          </div>
      </div>
    </div>
  );
};

// Conversation Tab Component
const ConversationTab = ({ dealData }) => {
  const { conversation_data } = dealData;

  if (!conversation_data) {
    return (
      <div className="text-center py-8">
        <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No conversation data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Customer Requirements</h3>
            <p className="text-sm text-blue-800">{conversation_data.customer_requirements || 'Not specified'}</p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-medium text-green-900 mb-2">Current Solutions</h3>
            <p className="text-sm text-green-800">{conversation_data.current_solutions || 'Not specified'}</p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="font-medium text-purple-900 mb-2">Technical Preferences</h3>
            <p className="text-sm text-purple-800">{conversation_data.tech_preferences || 'Not specified'}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-yellow-50 rounded-lg p-4">
            <h3 className="font-medium text-yellow-900 mb-2">Project Timeline</h3>
            <p className="text-sm text-yellow-800">{conversation_data.project_timeline || 'Not specified'}</p>
          </div>

          <div className="bg-red-50 rounded-lg p-4">
            <h3 className="font-medium text-red-900 mb-2">Urgency Level</h3>
            <p className="text-sm text-red-800">{conversation_data.urgency_level || 'Not specified'}</p>
          </div>

          <div className="bg-indigo-50 rounded-lg p-4">
            <h3 className="font-medium text-indigo-900 mb-2">Communication Style</h3>
            <p className="text-sm text-indigo-800">{conversation_data.communication_style || 'Not specified'}</p>
          </div>
        </div>
      </div>

      {conversation_data.sales_notes && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2 flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Sales Notes
          </h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{conversation_data.sales_notes}</p>
        </div>
      )}
    </div>
  );
};

// Technical Tab Component
const TechnicalTab = ({ dealData }) => {
  const { technical_solution, conversation_data } = dealData;

  return (
    <div className="space-y-6">
      {technical_solution ? (
        <div className="grid grid-cols-1 gap-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Solution Summary</h3>
            <p className="text-sm text-blue-800">{technical_solution.solution_summary}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-medium text-green-900 mb-2">Recommended Tech Stack</h3>
              <p className="text-sm text-green-800">{technical_solution.recommended_tech_stack}</p>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="font-medium text-purple-900 mb-2">Architecture Overview</h3>
              <p className="text-sm text-purple-800">{technical_solution.architecture_overview}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-center py-8">
            <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No technical solution generated yet</p>
          </div>

          {conversation_data && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Integration Needs</h3>
                <p className="text-sm text-gray-700">{conversation_data.integration_needs || 'Not specified'}</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Compliance Requirements</h3>
                <p className="text-sm text-gray-700">{conversation_data.compliance_requirements || 'Not specified'}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Timeline Tab Component
const TimelineTab = ({ dealData }) => {
  const { timeline } = dealData;

  const getTimelineIcon = (type) => {
    switch (type) {
      case 'creation': return Circle;
      case 'status_change': return ArrowRight;
      case 'ai_insight': return Brain;
      default: return CheckCircle;
    }
  };

  const getTimelineColor = (type) => {
    switch (type) {
      case 'creation': return 'text-green-600';
      case 'status_change': return 'text-blue-600';
      case 'ai_insight': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-4">
      {timeline && timeline.length > 0 ? (
        <div className="flow-root">
          <ul className="-mb-8">
            {timeline.map((event, index) => {
              const IconComponent = getTimelineIcon(event.type);
              return (
                <li key={index}>
                  <div className="relative pb-8">
                    {index !== timeline.length - 1 && (
                      <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white bg-gray-100 ${getTimelineColor(event.type)}`}>
                          <IconComponent className="h-4 w-4" />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{event.title}</p>
                          <p className="text-sm text-gray-500">{event.description}</p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time>{new Date(event.date).toLocaleDateString()}</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      ) : (
        <div className="text-center py-8">
          <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No timeline data available</p>
        </div>
      )}
    </div>
  );
};

// Resources Tab Component
const ResourcesTab = ({ dealData }) => {
  const { resource_allocation, proposal } = dealData;

  return (
    <div className="space-y-6">
      {resource_allocation ? (
        <div className="space-y-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Resource Summary</h3>
            <p className="text-sm text-blue-800">{resource_allocation.allocation_summary}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-medium text-green-900 mb-2">Team Structure</h3>
              <p className="text-sm text-green-800">{resource_allocation.team_structure}</p>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="font-medium text-purple-900 mb-2">Estimated Hours</h3>
              <p className="text-sm text-purple-800">{resource_allocation.estimated_hours} hours</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No resource allocation data available</p>
        </div>
      )}

      {proposal && (
        <div className="bg-yellow-50 rounded-lg p-4">
          <h3 className="font-medium text-yellow-900 mb-2">Proposal</h3>
          <p className="text-sm text-yellow-800">{proposal.proposal_summary}</p>
        </div>
      )}
    </div>
  );
};

// AI Insights Tab Component
const AIInsightsTab = ({ dealData, triggerAIInsight, loading }) => {
  const { ai_insights, deal } = dealData;

  const getInsightTypeColor = (type) => {
    const colors = {
      lead_qualification: 'bg-blue-100 text-blue-800',
      solution_design: 'bg-green-100 text-green-800',
      delivery_planning: 'bg-purple-100 text-purple-800',
      proposal_generation: 'bg-orange-100 text-orange-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const formatInsightData = (insight) => {
    try {
      return {
        recommendations: insight.recommendations ? JSON.parse(insight.recommendations) : [],
        relevant_data_points: insight.relevant_data_points ? JSON.parse(insight.relevant_data_points) : [],
        suggested_actions: insight.suggested_actions ? JSON.parse(insight.suggested_actions) : []
      };
    } catch (e) {
      return { recommendations: [], relevant_data_points: [], suggested_actions: [] };
    }
  };

  return (
    <div className="space-y-6">
      {/* Trigger AI Analysis Button */}
      <div className="border-b pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">AI Insights</h3>
            <p className="text-sm text-gray-500">AI-powered analysis for deal progression</p>
          </div>
          <button
            onClick={triggerAIInsight}
            disabled={loading}
            className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Brain className="h-4 w-4" />
            {loading ? 'Analyzing...' : 'Generate AI Analysis'}
          </button>
        </div>
      </div>

      {/* AI Insights List */}
      {ai_insights && ai_insights.length > 0 ? (
        <div className="space-y-4">
          {ai_insights.map((insight, index) => {
            const formattedData = formatInsightData(insight);
            return (
              <div key={index} className="border rounded-lg p-4 bg-white">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getInsightTypeColor(insight.insight_type)}`}>
                        {insight.insight_type.replace('_', ' ').toUpperCase()}
                      </span>
                      {insight.confidence_score && (
                        <span className="text-xs text-gray-500">
                          Confidence: {insight.confidence_score}%
                        </span>
                      )}
                    </div>
                    <h4 className="font-medium text-gray-900">{insight.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(insight.generated_at).toLocaleDateString()}
                  </span>
                </div>

                {formattedData.recommendations.length > 0 && (
                  <div className="mb-3">
                    <h5 className="font-medium text-gray-800 mb-2">Recommendations:</h5>
                    <ul className="space-y-1">
                      {formattedData.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {formattedData.suggested_actions.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-800 mb-2">Suggested Actions:</h5>
                    <ul className="space-y-1">
                      {formattedData.suggested_actions.map((action, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                          <ArrowRight className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8">
          <Brain className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No AI Insights Yet</h3>
          <p className="text-gray-500 mb-4">Generate AI analysis to get intelligent insights for this deal</p>
          <button
            onClick={triggerAIInsight}
            disabled={loading}
            className={`px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Brain className="h-5 w-5" />
            {loading ? 'Analyzing...' : 'Generate AI Analysis'}
          </button>
        </div>
      )}
    </div>
  );
};

export default DealDetailModal;