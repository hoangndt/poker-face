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
  Code,
  TrendingUp,
  BarChart3,
  Users,
  Percent,
  Euro,
  ArrowRight,
  Send,
  Trash2,
  FileCheck,
  AlertTriangle,
  Star,
  MessageCircle,
  Search,
  Filter,
  ExternalLink,
  Video,
  Linkedin
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

      // Switch to appropriate tab based on deal status
      if (dealData.deal.status === 'qualified_delivery') {
        setActiveTab('resources');
      } else if (dealData.deal.status === 'qualified_cso') {
        setActiveTab('proposal');
      } else {
        setActiveTab('ai-insights');
      }
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
      case 'qualified_delivery': return 'Planning delivery strategy and resource allocation...';
      case 'qualified_cso': return 'Generating commercial proposal and pricing model...';
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
    { id: 'activities', label: 'Activities', icon: Activity },
    { id: 'technical', label: 'Technical', icon: Settings },
    { id: 'ai-insights', label: 'AI Insights', icon: Brain },
    { id: 'timeline', label: 'Timeline', icon: Clock },
    { id: 'resources', label: 'Resources', icon: User },
    { id: 'proposal', label: 'Proposal', icon: FileText },
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
              {activeTab === 'activities' && <ActivitiesTab dealData={dealData} />}
              {activeTab === 'technical' && <TechnicalTab dealData={dealData} />}
              {activeTab === 'ai-insights' && <AIInsightsTab dealData={dealData} triggerAIInsight={triggerAIInsight} loading={loading} />}
              {activeTab === 'timeline' && <TimelineTab dealData={dealData} />}
              {activeTab === 'resources' && <ResourcesTab dealData={dealData} triggerAIInsight={triggerAIInsight} loading={loading} />}
              {activeTab === 'proposal' && <ProposalTab dealData={dealData} triggerAIInsight={triggerAIInsight} loading={loading} />}
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
      <div className="grid grid-cols-2 gap-6">
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
            Assignment
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Contact owner:</span>
              <div className="text-right">
                <div className="font-medium">{deal.assigned_person?.name || 'Unassigned'}</div>
                {deal.assigned_person?.department && (
                  <div className="text-xs text-gray-500">{deal.assigned_person.department}</div>
                )}
              </div>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Region:</span>
              <span className="font-medium">{deal.region || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Country:</span>
              <span className="font-medium">{deal.country || 'Not specified'}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Clock className="h-4 w-4 mr-2" />
            Timeline
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Expected Close:</span>
              <span className="font-medium">{formatDate(deal.expected_close_date)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Implementation Time:</span>
              <span className="font-medium">{deal.implementation_time || 'Not specified'}</span>
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
                {deal.deal_probability ? `${deal.deal_probability}%` : 'Not specified'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Weighted Amount:</span>
              <span className="font-medium flex items-center">
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
      {/* Business Context */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Customer Requirements</h3>
            <p className="text-sm text-blue-800">{conversation_data.customer_requirements || 'Not specified'}</p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-medium text-green-900 mb-2">Business Goals</h3>
            <p className="text-sm text-green-800">{conversation_data.business_goals || 'Not specified'}</p>
          </div>

          <div className="bg-red-50 rounded-lg p-4">
            <h3 className="font-medium text-red-900 mb-2">Pain Points</h3>
            <p className="text-sm text-red-800">{conversation_data.pain_points || 'Not specified'}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Current Solutions</h3>
            <p className="text-sm text-gray-700">{conversation_data.current_solutions || 'Not specified'}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="font-medium text-purple-900 mb-2">Technical Preferences</h3>
            <p className="text-sm text-purple-800">{conversation_data.tech_preferences || 'Not specified'}</p>
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <h3 className="font-medium text-orange-900 mb-2">Integration Needs</h3>
            <p className="text-sm text-orange-800">{conversation_data.integration_needs || 'Not specified'}</p>
          </div>

          <div className="bg-pink-50 rounded-lg p-4">
            <h3 className="font-medium text-pink-900 mb-2">Compliance Requirements</h3>
            <p className="text-sm text-pink-800">{conversation_data.compliance_requirements || 'Not specified'}</p>
          </div>

          <div className="bg-yellow-50 rounded-lg p-4">
            <h3 className="font-medium text-yellow-900 mb-2">Project Timeline</h3>
            <p className="text-sm text-yellow-800">{conversation_data.project_timeline || 'Not specified'}</p>
          </div>
        </div>
      </div>

      {/* Project Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-indigo-50 rounded-lg p-4">
          <h3 className="font-medium text-indigo-900 mb-2">Urgency Level</h3>
          <p className="text-sm text-indigo-800">{conversation_data.urgency_level || 'Not specified'}</p>
        </div>

        <div className="bg-teal-50 rounded-lg p-4">
          <h3 className="font-medium text-teal-900 mb-2">Team Size</h3>
          <p className="text-sm text-teal-800">{conversation_data.team_size || 'Not specified'}</p>
        </div>

        <div className="bg-cyan-50 rounded-lg p-4">
          <h3 className="font-medium text-cyan-900 mb-2">Communication Style</h3>
          <p className="text-sm text-cyan-800">{conversation_data.communication_style || 'Not specified'}</p>
        </div>
      </div>

      {/* Sales Notes */}
      {conversation_data.sales_notes && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2 flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Sales Notes
          </h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{conversation_data.sales_notes}</p>
        </div>
      )}

      {/* Follow-up Information */}
      {conversation_data.follow_up_needed && (
        <div className="bg-amber-50 rounded-lg p-4">
          <h3 className="font-medium text-amber-900 mb-2 flex items-center">
            <Clock className="h-4 w-4 mr-2" />
            Follow-up Needed
          </h3>
          <p className="text-sm text-amber-800">{conversation_data.follow_up_needed}</p>
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
              <h3 className="font-medium text-green-900 mb-3 flex items-center">
                <Code className="h-4 w-4 mr-2" />
                Recommended Tech Stack
              </h3>
              {(() => {
                try {
                  const techStack = JSON.parse(technical_solution.recommended_tech_stack || '{}');
                  return (
                    <div className="space-y-3">
                      {Object.entries(techStack).map(([category, technologies]) => (
                        <div key={category} className="space-y-1">
                          <h4 className="text-xs font-medium text-green-700 uppercase tracking-wide">
                            {category.replace('_', ' ')}
                          </h4>
                          <div className="flex flex-wrap gap-1">
                            {Array.isArray(technologies) ? technologies.map((tech, index) => (
                              <span
                                key={index}
                                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-white text-gray-700 border border-gray-300 shadow-sm"
                              >
                                {tech}
                              </span>
                            )) : (
                              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-white text-gray-700 border border-gray-300 shadow-sm">
                                {technologies}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                      {Object.keys(techStack).length === 0 && (
                        <p className="text-sm text-green-700 italic">No tech stack specified</p>
                      )}
                    </div>
                  );
                } catch (error) {
                  // Fallback for non-JSON data
                  return (
                    <p className="text-sm text-green-800">{technical_solution.recommended_tech_stack}</p>
                  );
                }
              })()}
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="font-medium text-purple-900 mb-2 flex items-center">
                <Settings className="h-4 w-4 mr-2" />
                Architecture Overview
              </h3>
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

// Activities Tab Component
const ActivitiesTab = ({ dealData }) => {
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewActivityModal, setShowNewActivityModal] = useState(false);
  const [selectedActivityType, setSelectedActivityType] = useState('email');

  // Extract existing conversation data
  const { conversation_data, comments, status_history } = dealData;

  // Convert existing data to activity format and combine with mock data
  const existingActivities = [];

  // Add conversation data as activity
  if (conversation_data?.sales_notes) {
    existingActivities.push({
      id: 'conv-1',
      type: conversation_data.communication_channel || 'email',
      direction: 'inbound',
      subject: 'Initial Conversation Notes',
      content: conversation_data.sales_notes,
      participant: 'Customer',
      timestamp: conversation_data.last_conversation_date ? new Date(conversation_data.last_conversation_date) : new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      status: 'completed'
    });
  }

  // Add comments as activities
  if (comments && comments.length > 0) {
    comments.forEach((comment, index) => {
      existingActivities.push({
        id: `comment-${comment.id}`,
        type: 'other',
        direction: 'internal',
        subject: 'Internal Note',
        content: comment.content,
        participant: comment.author_name || 'Team Member',
        timestamp: new Date(comment.created_at),
        status: 'completed'
      });
    });
  }

  // Mock activities data for demonstration
  const mockActivities = [
    {
      id: 1,
      type: 'email',
      direction: 'outbound',
      subject: 'Follow-up on Technical Requirements',
      content: 'Hi John, Following up on our discussion about the technical requirements...',
      participant: 'john.doe@client.com',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      status: 'delivered',
      important: true
    },
    {
      id: 2,
      type: 'linkedin',
      direction: 'inbound',
      subject: 'Connection Request Accepted',
      content: 'Thanks for connecting! Looking forward to our collaboration.',
      participant: 'Sarah Johnson',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
      status: 'read'
    },
    {
      id: 3,
      type: 'phone',
      direction: 'outbound',
      subject: 'Discovery Call',
      content: 'Discussed project scope, timeline, and budget requirements. Client interested in Q2 implementation.',
      participant: '+1 (555) 123-4567',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
      status: 'completed',
      duration: '45 minutes'
    },
    {
      id: 4,
      type: 'whatsapp',
      direction: 'inbound',
      subject: 'Quick Question',
      content: 'Can we schedule a call for tomorrow?',
      participant: 'John Doe',
      timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
      status: 'replied'
    },
    {
      id: 5,
      type: 'meeting',
      direction: 'scheduled',
      subject: 'Technical Architecture Review',
      content: 'Review proposed technical architecture and discuss implementation approach.',
      participant: 'Technical Team',
      timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
      status: 'completed',
      duration: '90 minutes'
    },
    {
      id: 6,
      type: 'email',
      direction: 'inbound',
      subject: 'Proposal Feedback',
      content: 'We have reviewed your proposal and have some questions about the timeline...',
      participant: 'procurement@client.com',
      timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000), // 5 days ago
      status: 'replied'
    }
  ];

  // Combine existing and mock activities, sort by timestamp
  const allActivities = [...existingActivities, ...mockActivities].sort((a, b) => b.timestamp - a.timestamp);

  // Activity type configuration
  const activityTypes = {
    email: {
      icon: Mail,
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-600',
      label: 'Email'
    },
    linkedin: {
      icon: Linkedin,
      bgColor: 'bg-indigo-100',
      textColor: 'text-indigo-600',
      label: 'LinkedIn'
    },
    whatsapp: {
      icon: MessageCircle,
      bgColor: 'bg-green-100',
      textColor: 'text-green-600',
      label: 'WhatsApp'
    },
    phone: {
      icon: Phone,
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-600',
      label: 'Phone'
    },
    meeting: {
      icon: Video,
      bgColor: 'bg-orange-100',
      textColor: 'text-orange-600',
      label: 'Meeting'
    },
    other: {
      icon: MessageSquare,
      bgColor: 'bg-gray-100',
      textColor: 'text-gray-600',
      label: 'Other'
    }
  };

  // Filter activities
  const filteredActivities = allActivities.filter(activity => {
    const matchesType = filterType === 'all' || activity.type === filterType;
    const matchesSearch = searchTerm === '' ||
      activity.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      activity.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      activity.participant.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesType && matchesSearch;
  });

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return timestamp.toLocaleDateString();
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'text-blue-600';
      case 'read': return 'text-green-600';
      case 'replied': return 'text-purple-600';
      case 'completed': return 'text-green-600';
      case 'pending': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  // Get direction indicator
  const getDirectionIcon = (direction) => {
    switch (direction) {
      case 'inbound': return '↓';
      case 'outbound': return '↑';
      case 'scheduled': return '📅';
      case 'internal': return '🏢';
      default: return '•';
    }
  };

  // Check if activity is internal
  const isInternalActivity = (activity) => {
    return activity.direction === 'internal' || activity.type === 'other';
  };

  return (
    <div className="space-y-6">
      {/* Header with Quick Actions */}
      <div className="border-b pb-4">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Communication Activities</h3>
            <p className="text-sm text-gray-500">Multi-channel communication timeline and management</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {setSelectedActivityType('email'); setShowNewActivityModal(true);}}
              className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm"
            >
              <Mail className="h-4 w-4" />
              Email
            </button>
            <button
              onClick={() => {setSelectedActivityType('linkedin'); setShowNewActivityModal(true);}}
              className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 text-sm"
            >
              <Linkedin className="h-4 w-4" />
              LinkedIn
            </button>
            <button
              onClick={() => {setSelectedActivityType('whatsapp'); setShowNewActivityModal(true);}}
              className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 text-sm"
            >
              <MessageCircle className="h-4 w-4" />
              WhatsApp
            </button>
            <button
              onClick={() => {setSelectedActivityType('phone'); setShowNewActivityModal(true);}}
              className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 text-sm"
            >
              <Phone className="h-4 w-4" />
              Call
            </button>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Activities</option>
              <option value="email">Email</option>
              <option value="linkedin">LinkedIn</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="phone">Phone</option>
              <option value="meeting">Meetings</option>
            </select>
          </div>
          <div className="flex-1 relative">
            <Search className="h-4 w-4 text-gray-500 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search activities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="space-y-4">
        {filteredActivities.length > 0 ? (
          filteredActivities.map((activity) => {
            const activityConfig = activityTypes[activity.type] || activityTypes.other;
            const ActivityIcon = activityConfig.icon;

            const isInternal = isInternalActivity(activity);

            return (
              <div key={activity.id} className={`${isInternal ? 'bg-gray-50 border-gray-100' : 'bg-white border-gray-200'} border rounded-lg p-4 hover:shadow-md transition-shadow`}>
                <div className="flex items-start gap-4">
                  {/* Activity Icon */}
                  <div className={`flex-shrink-0 w-10 h-10 ${activityConfig.bgColor} rounded-full flex items-center justify-center`}>
                    <ActivityIcon className={`h-5 w-5 ${activityConfig.textColor}`} />
                  </div>

                  {/* Activity Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900 truncate">{activity.subject}</h4>
                          <span className="text-sm text-gray-500">{getDirectionIcon(activity.direction)}</span>
                          {activity.important && (
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">{activity.content}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>{activity.participant}</span>
                          <span>•</span>
                          <span>{formatTimestamp(activity.timestamp)}</span>
                          {activity.duration && (
                            <>
                              <span>•</span>
                              <span>{activity.duration}</span>
                            </>
                          )}
                          <span className={`font-medium ${getStatusColor(activity.status)}`}>
                            {activity.status}
                          </span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center gap-2 ml-4">
                        <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                          <Star className="h-4 w-4" />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                          <ExternalLink className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-center py-8">
            <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Activities Found</h3>
            <p className="text-gray-500 mb-4">
              {searchTerm || filterType !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Start communicating with your contacts to see activities here'
              }
            </p>
          </div>
        )}
      </div>

      {/* Activity Summary Stats */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Activity Summary</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(activityTypes).map(([type, config]) => {
            const count = allActivities.filter(a => a.type === type).length;
            if (count === 0) return null;

            return (
              <div key={type} className="text-center">
                <div className={`w-8 h-8 ${config.bgColor} rounded-full flex items-center justify-center mx-auto mb-1`}>
                  <config.icon className={`h-4 w-4 ${config.textColor}`} />
                </div>
                <div className="text-lg font-semibold text-gray-900">{count}</div>
                <div className="text-xs text-gray-500">{config.label}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* New Activity Modal Placeholder */}
      {showNewActivityModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium mb-4">
              New {activityTypes[selectedActivityType]?.label} Activity
            </h3>
            <p className="text-gray-600 mb-4">
              This would open a form to create a new {selectedActivityType} activity.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowNewActivityModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowNewActivityModal(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Resources Tab Component
const ResourcesTab = ({ dealData, triggerAIInsight, loading }) => {
  const { resource_allocation, proposal, deal } = dealData;

  // Parse JSON data safely
  const parseJSONSafely = (jsonString, fallback = []) => {
    try {
      return jsonString ? JSON.parse(jsonString) : fallback;
    } catch (error) {
      console.error('Error parsing JSON:', error);
      return fallback;
    }
  };

  const teamComposition = parseJSONSafely(resource_allocation?.team_composition);
  const milestoneBreakdown = parseJSONSafely(resource_allocation?.milestone_breakdown);
  const resourceTimeline = parseJSONSafely(resource_allocation?.resource_timeline, '');

  // Calculate total estimated hours from team composition and timeline
  const calculateTotalHours = (team) => {
    if (!Array.isArray(team)) return 0;

    // If team members have explicit hours, use those
    const explicitHours = team.reduce((total, member) => {
      const hours = member.estimated_hours || member.hours || 0;
      return total + (typeof hours === 'number' ? hours : 0);
    }, 0);

    if (explicitHours > 0) return explicitHours;

    // Otherwise, calculate based on allocation and estimated timeline
    // Assume 4 months average project duration and 160 hours per month per full-time person
    const averageProjectMonths = 4;
    const hoursPerMonth = 160;

    return team.reduce((total, member) => {
      const allocation = member.allocation || 1.0;
      const estimatedHours = allocation * hoursPerMonth * averageProjectMonths;
      return total + estimatedHours;
    }, 0);
  };

  const totalHours = calculateTotalHours(teamComposition);

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return 'TBD';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* AI Trigger Section */}
      <div className="border-b pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Resource Planning</h3>
            <p className="text-sm text-gray-500">AI-powered resource allocation and team planning</p>
          </div>
          {(!resource_allocation || deal?.status === 'qualified_delivery') && (
            <button
              onClick={triggerAIInsight}
              disabled={loading}
              className={`px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <Brain className="h-4 w-4" />
              {loading ? 'Generating...' : 'Generate Resource Plan'}
            </button>
          )}
        </div>
      </div>

      {resource_allocation ? (
        <div className="space-y-6">
          {/* Resource Summary */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-3 flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Resource Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">{totalHours}</div>
                <div className="text-sm text-blue-600">Total Hours</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">{formatCurrency(resource_allocation.development_cost)}</div>
                <div className="text-sm text-blue-600">Development Cost</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">{formatCurrency(resource_allocation.total_estimated_cost)}</div>
                <div className="text-sm text-blue-600">Total Cost</div>
              </div>
            </div>
          </div>

          {/* Team Structure */}
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-medium text-green-900 mb-3 flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Team Structure
            </h3>
            {Array.isArray(teamComposition) && teamComposition.length > 0 ? (
              <div className="space-y-3">
                {teamComposition.map((member, index) => {
                  const allocation = member.allocation || 1.0;
                  const estimatedHours = member.estimated_hours || member.hours || (allocation * 160 * 4); // 4 months average
                  const allocationPercent = Math.round(allocation * 100);

                  return (
                    <div key={index} className="flex justify-between items-center bg-white rounded p-3">
                      <div className="flex-1">
                        <div className="font-medium text-green-900">{member.role || member.name || 'Team Member'}</div>
                        <div className="text-sm text-green-700">
                          {Array.isArray(member.skills_required)
                            ? member.skills_required.join(', ')
                            : (member.skills || member.description || 'Various skills')
                          }
                        </div>
                        {Array.isArray(member.responsibilities) && member.responsibilities.length > 0 && (
                          <div className="text-xs text-green-600 mt-1">
                            {member.responsibilities.join(', ')}
                          </div>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <div className="font-medium text-green-900">{Math.round(estimatedHours)}h</div>
                        <div className="text-sm text-green-700">{allocationPercent}% allocation</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-green-800">Team composition will be determined during planning phase</p>
            )}
          </div>

          {/* Project Timeline & Milestones */}
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="font-medium text-purple-900 mb-3 flex items-center">
              <Calendar className="h-4 w-4 mr-2" />
              Project Timeline & Milestones
            </h3>
            {Array.isArray(milestoneBreakdown) && milestoneBreakdown.length > 0 ? (
              <div className="space-y-3">
                {milestoneBreakdown.map((milestone, index) => (
                  <div key={index} className="bg-white rounded p-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="font-medium text-purple-900">{milestone.phase || milestone.name || `Phase ${index + 1}`}</div>
                        <div className="text-sm text-purple-700 mt-1">{milestone.description || milestone.deliverables || 'Key deliverables and activities'}</div>
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-sm font-medium text-purple-900">{milestone.duration || milestone.timeline || 'TBD'}</div>
                        <div className="text-xs text-purple-700">{milestone.effort || milestone.hours || ''}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-purple-700 mb-1">Estimated Start Date</div>
                  <div className="font-medium text-purple-900">
                    {resource_allocation.estimated_start_date
                      ? new Date(resource_allocation.estimated_start_date).toLocaleDateString()
                      : 'TBD'
                    }
                  </div>
                </div>
                <div>
                  <div className="text-sm text-purple-700 mb-1">Estimated Delivery Date</div>
                  <div className="font-medium text-purple-900">
                    {resource_allocation.estimated_delivery_date
                      ? new Date(resource_allocation.estimated_delivery_date).toLocaleDateString()
                      : 'TBD'
                    }
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* AI Confidence & Metadata */}
          {resource_allocation.ai_confidence_score && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                <Brain className="h-4 w-4 mr-2" />
                AI Analysis Confidence
              </h3>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Confidence Score</span>
                    <span>{Math.round(resource_allocation.ai_confidence_score)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${resource_allocation.ai_confidence_score}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">Generated by</div>
                  <div className="text-sm font-medium">{resource_allocation.generated_by || 'AI Agent'}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Resource Plan Yet</h3>
          <p className="text-gray-500 mb-4">Generate an AI-powered resource allocation plan for this deal</p>
          <button
            onClick={triggerAIInsight}
            disabled={loading}
            className={`px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 mx-auto ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Brain className="h-5 w-5" />
            {loading ? 'Generating Resource Plan...' : 'Generate Resource Plan'}
          </button>
        </div>
      )}

      {proposal && (
        <div className="bg-yellow-50 rounded-lg p-4">
          <h3 className="font-medium text-yellow-900 mb-2 flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Proposal Summary
          </h3>
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

// Proposal Tab Component
const ProposalTab = ({ dealData, triggerAIInsight, loading }) => {
  const { proposal, deal } = dealData;

  // Parse JSON data safely
  const parseJSONSafely = (jsonString, fallback = []) => {
    try {
      return jsonString ? JSON.parse(jsonString) : fallback;
    } catch (error) {
      console.error('Error parsing JSON:', error);
      return fallback;
    }
  };

  // Parse proposal data if it exists
  const valueProposition = parseJSONSafely(proposal?.solution_overview);
  const competitiveAdvantages = parseJSONSafely(proposal?.business_value);
  const costBreakdown = parseJSONSafely(proposal?.cost_breakdown);
  const riskMitigation = parseJSONSafely(proposal?.risk_mitigation);
  const projectPhases = parseJSONSafely(proposal?.project_phases);
  const keyMilestones = parseJSONSafely(proposal?.key_milestones);

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return 'TBD';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* AI Trigger Section */}
      <div className="border-b pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Commercial Proposal</h3>
            <p className="text-sm text-gray-500">AI-generated proposal with pricing and commercial terms</p>
          </div>
          {(!proposal || deal?.status === 'qualified_cso') && (
            <button
              onClick={triggerAIInsight}
              disabled={loading}
              className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <FileText className="h-4 w-4" />
              {loading ? 'Generating...' : 'Generate Proposal'}
            </button>
          )}
        </div>
      </div>

      {proposal ? (
        <div className="space-y-6">
          {/* Executive Summary */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-3 flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              Executive Summary
            </h3>
            <p className="text-sm text-blue-800 leading-relaxed">
              {proposal.executive_summary || 'Comprehensive solution proposal tailored to client requirements and business objectives.'}
            </p>
            {proposal.proposal_status && (
              <div className="mt-3 flex items-center gap-2">
                <span className="text-xs text-blue-600">Status:</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  proposal.proposal_status === 'approved' ? 'bg-green-100 text-green-800' :
                  proposal.proposal_status === 'review' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {proposal.proposal_status.charAt(0).toUpperCase() + proposal.proposal_status.slice(1)}
                </span>
              </div>
            )}
          </div>

          {/* Pricing Model & Cost Breakdown */}
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-medium text-green-900 mb-3 flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Pricing Model & Cost Breakdown
            </h3>
            {costBreakdown && Object.keys(costBreakdown).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(costBreakdown).map(([key, value], index) => (
                  <div key={index} className="flex justify-between items-center bg-white rounded p-3">
                    <div>
                      <div className="font-medium text-green-900">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                      <div className="text-sm text-green-700">Commercial term details</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-green-900">{value}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded p-4">
                <p className="text-sm text-green-800">Cost breakdown and pricing model will be determined during proposal generation.</p>
              </div>
            )}
          </div>

          {/* Value Proposition */}
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="font-medium text-purple-900 mb-3 flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Value Proposition
            </h3>
            {Array.isArray(valueProposition) && valueProposition.length > 0 ? (
              <div className="space-y-2">
                {valueProposition.map((value, index) => (
                  <div key={index} className="flex items-start bg-white rounded p-3">
                    <CheckCircle className="h-4 w-4 text-purple-600 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-purple-800">{value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded p-4">
                <p className="text-sm text-purple-800">Value proposition will be defined during proposal generation.</p>
              </div>
            )}
          </div>

          {/* Competitive Advantages */}
          <div className="bg-indigo-50 rounded-lg p-4">
            <h3 className="font-medium text-indigo-900 mb-3 flex items-center">
              <Star className="h-4 w-4 mr-2" />
              Competitive Advantages
            </h3>
            {Array.isArray(competitiveAdvantages) && competitiveAdvantages.length > 0 ? (
              <div className="space-y-2">
                {competitiveAdvantages.map((advantage, index) => (
                  <div key={index} className="flex items-start bg-white rounded p-3">
                    <Star className="h-4 w-4 text-indigo-600 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-indigo-800">{advantage}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded p-4">
                <p className="text-sm text-indigo-800">Competitive advantages will be identified during proposal generation.</p>
              </div>
            )}
          </div>

          {/* Technical Approach */}
          <div className="bg-cyan-50 rounded-lg p-4">
            <h3 className="font-medium text-cyan-900 mb-3 flex items-center">
              <Settings className="h-4 w-4 mr-2" />
              Technical Approach
            </h3>
            <div className="bg-white rounded p-4">
              <p className="text-sm text-cyan-800 leading-relaxed">
                {proposal.technical_approach || 'Technical approach and implementation methodology will be detailed during proposal generation.'}
              </p>
            </div>
          </div>

          {/* Terms & Conditions */}
          <div className="bg-yellow-50 rounded-lg p-4">
            <h3 className="font-medium text-yellow-900 mb-3 flex items-center">
              <FileCheck className="h-4 w-4 mr-2" />
              Terms & Conditions
            </h3>
            <div className="space-y-3">
              {proposal.assumptions && (
                <div className="bg-white rounded p-3">
                  <div className="font-medium text-yellow-900 mb-1">Assumptions</div>
                  <div className="text-sm text-yellow-700">{proposal.assumptions}</div>
                </div>
              )}
              {proposal.scope_limitations && (
                <div className="bg-white rounded p-3">
                  <div className="font-medium text-yellow-900 mb-1">Scope Limitations</div>
                  <div className="text-sm text-yellow-700">{proposal.scope_limitations}</div>
                </div>
              )}
              {proposal.terms_and_conditions && (
                <div className="bg-white rounded p-3">
                  <div className="font-medium text-yellow-900 mb-1">General Terms</div>
                  <div className="text-sm text-yellow-700">{proposal.terms_and_conditions}</div>
                </div>
              )}
              {!proposal.assumptions && !proposal.scope_limitations && !proposal.terms_and_conditions && (
                <div className="bg-white rounded p-4">
                  <p className="text-sm text-yellow-800">Terms and conditions will be defined during proposal generation.</p>
                </div>
              )}
            </div>
          </div>

          {/* Implementation Timeline */}
          <div className="bg-orange-50 rounded-lg p-4">
            <h3 className="font-medium text-orange-900 mb-3 flex items-center">
              <Calendar className="h-4 w-4 mr-2" />
              Implementation Timeline & Deliverables
            </h3>
            <div className="space-y-3">
              {/* Project Phases */}
              {Array.isArray(projectPhases) && projectPhases.length > 0 ? (
                <div>
                  <h4 className="font-medium text-orange-900 mb-2">Project Phases</h4>
                  {projectPhases.map((phase, index) => (
                    <div key={index} className="bg-white rounded p-3 mb-2">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="font-medium text-orange-900">{phase.phase || phase.name || `Phase ${index + 1}`}</div>
                          <div className="text-sm text-orange-700 mt-1">{phase.description || phase.deliverables || 'Phase deliverables and activities'}</div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-sm font-medium text-orange-900">{phase.duration || phase.timeline || 'TBD'}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : proposal.implementation_plan ? (
                <div className="bg-white rounded p-4">
                  <h4 className="font-medium text-orange-900 mb-2">Implementation Plan</h4>
                  <p className="text-sm text-orange-800">{proposal.implementation_plan}</p>
                </div>
              ) : null}

              {/* Key Milestones */}
              {Array.isArray(keyMilestones) && keyMilestones.length > 0 ? (
                <div>
                  <h4 className="font-medium text-orange-900 mb-2">Key Milestones</h4>
                  {keyMilestones.map((milestone, index) => (
                    <div key={index} className="bg-white rounded p-3 mb-2">
                      <div className="flex justify-between items-center">
                        <div className="font-medium text-orange-900">{milestone.name || milestone.title || `Milestone ${index + 1}`}</div>
                        <div className="text-sm text-orange-700">{milestone.date || milestone.timeline || 'TBD'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}

              {/* Delivery Timeline */}
              {proposal.delivery_timeline && (
                <div className="bg-white rounded p-4">
                  <h4 className="font-medium text-orange-900 mb-2">Delivery Timeline</h4>
                  <p className="text-sm text-orange-800">{proposal.delivery_timeline}</p>
                </div>
              )}

              {!projectPhases?.length && !keyMilestones?.length && !proposal.implementation_plan && !proposal.delivery_timeline && (
                <div className="bg-white rounded p-4">
                  <p className="text-sm text-orange-800">Implementation timeline and deliverables will be defined during proposal generation.</p>
                </div>
              )}
            </div>
          </div>

          {/* Risk Assessment & Mitigation */}
          <div className="bg-red-50 rounded-lg p-4">
            <h3 className="font-medium text-red-900 mb-3 flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Risk Assessment & Mitigation
            </h3>
            {riskMitigation && Object.keys(riskMitigation).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(riskMitigation).map(([riskType, mitigation], index) => (
                  <div key={index} className="bg-white rounded p-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="font-medium text-red-900">{riskType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                        <div className="text-sm text-red-700 mt-1">{mitigation}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : proposal.risk_mitigation ? (
              <div className="bg-white rounded p-4">
                <p className="text-sm text-red-800">{proposal.risk_mitigation}</p>
              </div>
            ) : (
              <div className="bg-white rounded p-4">
                <p className="text-sm text-red-800">Risk assessment and mitigation strategies will be defined during proposal generation.</p>
              </div>
            )}
          </div>

          {/* Proposal Metadata */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Brain className="h-4 w-4 mr-2" />
              Proposal Metadata
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Generated</div>
                <div className="font-medium text-gray-900">
                  {proposal.generated_at
                    ? new Date(proposal.generated_at).toLocaleDateString()
                    : 'TBD'
                  }
                </div>
              </div>
              {proposal.approved_at && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Approved</div>
                  <div className="font-medium text-gray-900">
                    {new Date(proposal.approved_at).toLocaleDateString()}
                  </div>
                </div>
              )}
              {proposal.sent_at && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Sent to Client</div>
                  <div className="font-medium text-gray-900">
                    {new Date(proposal.sent_at).toLocaleDateString()}
                  </div>
                </div>
              )}
              {proposal.cso_approval !== null && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">CSO Approval</div>
                  <div className={`font-medium ${proposal.cso_approval ? 'text-green-700' : 'text-red-700'}`}>
                    {proposal.cso_approval ? 'Approved' : 'Pending'}
                  </div>
                </div>
              )}
            </div>
            {proposal.cso_review_notes && (
              <div className="mt-4 bg-white rounded p-3">
                <div className="text-sm text-gray-600 mb-1">CSO Review Notes</div>
                <div className="text-sm text-gray-800">{proposal.cso_review_notes}</div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Proposal Generated Yet</h3>
          <p className="text-gray-500 mb-4">Generate an AI-powered commercial proposal for this deal</p>
          <button
            onClick={triggerAIInsight}
            disabled={loading}
            className={`px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <FileText className="h-5 w-5" />
            {loading ? 'Generating Proposal...' : 'Generate Commercial Proposal'}
          </button>
        </div>
      )}
    </div>
  );
};

export default DealDetailModal;