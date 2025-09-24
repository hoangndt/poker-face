import React, { useState, useEffect } from 'react';
import {
  X,
  Building,
  User,
  Calendar,
  DollarSign,
  MapPin,
  Clock,
  Star,
  TrendingUp,
  MessageSquare,
  CheckCircle,
  AlertTriangle,
  XCircle,
  BarChart3,
  Phone,
  Mail,
  Target,
  Activity,
  Users,
  Percent
} from 'lucide-react';
import toast from 'react-hot-toast';

const CustomerDetailModal = ({ customerId, isOpen, onClose }) => {
  const [customerData, setCustomerData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && customerId) {
      fetchCustomerDetail();
    }
  }, [isOpen, customerId]);

  const fetchCustomerDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/sprint/customer-success/customers/${customerId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch customer details');
      }

      const data = await response.json();
      setCustomerData(data);
    } catch (error) {
      console.error('Error fetching customer details:', error);
      toast.error('Failed to load customer details');
    } finally {
      setLoading(false);
    }
  };

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

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Get health status display
  const getHealthStatusDisplay = (status) => {
    switch (status) {
      case 'Green':
        return { color: 'text-green-600 bg-green-100', icon: CheckCircle, label: 'Healthy' };
      case 'Yellow':
        return { color: 'text-yellow-600 bg-yellow-100', icon: AlertTriangle, label: 'At Risk' };
      case 'Red':
        return { color: 'text-red-600 bg-red-100', icon: XCircle, label: 'Critical' };
      default:
        return { color: 'text-gray-600 bg-gray-100', icon: AlertTriangle, label: 'Unknown' };
    }
  };

  // Get NPS category
  const getNPSCategory = (score) => {
    if (score >= 50) return { label: 'Excellent', color: 'text-green-600' };
    if (score >= 0) return { label: 'Good', color: 'text-yellow-600' };
    return { label: 'Needs Improvement', color: 'text-red-600' };
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Customer Success Details</h2>
            <p className="text-sm text-gray-600 mt-1">
              Comprehensive customer implementation overview
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : customerData ? (
          <div className="p-6 space-y-6">
            {/* Customer Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Basic Information */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Building className="h-4 w-4 mr-2" />
                  Customer Information
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Company:</span>
                    <span className="font-medium">{customerData.deal.customer_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Contact Person:</span>
                    <span className="font-medium">{customerData.deal.contact_person || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Email:</span>
                    <span className="font-medium">{customerData.deal.customer_email || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Location:</span>
                    <span className="font-medium">{customerData.deal.country}, {customerData.deal.region}</span>
                  </div>
                </div>
              </div>

              {/* Deal Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Deal Summary
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Deal Value:</span>
                    <span className="font-medium">{formatCurrency(customerData.deal.estimated_value)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Close Date:</span>
                    <span className="font-medium">{formatDate(customerData.deal.actual_close_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Implementation Time:</span>
                    <span className="font-medium">{customerData.deal.implementation_time || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Assigned Owner:</span>
                    <span className="font-medium">{customerData.deal.assigned_person?.name || 'Unassigned'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Satisfaction Metrics */}
            {customerData.satisfaction && (
              <div className="bg-white border rounded-lg p-6">
                <h3 className="font-medium text-gray-900 mb-4 flex items-center">
                  <Star className="h-4 w-4 mr-2" />
                  Customer Satisfaction Metrics
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  {/* Overall Satisfaction */}
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-1">
                      {customerData.satisfaction.overall_satisfaction_score}/10
                    </div>
                    <div className="text-sm text-gray-600">Overall Satisfaction</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(customerData.satisfaction.overall_satisfaction_score / 10) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* NPS Score */}
                  <div className="text-center">
                    <div className={`text-3xl font-bold mb-1 ${getNPSCategory(customerData.satisfaction.nps_score).color}`}>
                      {customerData.satisfaction.nps_score}
                    </div>
                    <div className="text-sm text-gray-600">Net Promoter Score</div>
                    <div className={`text-xs mt-1 ${getNPSCategory(customerData.satisfaction.nps_score).color}`}>
                      {getNPSCategory(customerData.satisfaction.nps_score).label}
                    </div>
                  </div>

                  {/* Health Status */}
                  <div className="text-center">
                    {(() => {
                      const healthDisplay = getHealthStatusDisplay(customerData.satisfaction.customer_health_status);
                      const HealthIcon = healthDisplay.icon;
                      return (
                        <>
                          <div className="flex justify-center mb-2">
                            <HealthIcon className="h-8 w-8 text-current" />
                          </div>
                          <div className={`font-medium ${healthDisplay.color.split(' ')[0]}`}>
                            {healthDisplay.label}
                          </div>
                          <div className="text-sm text-gray-600">Customer Health</div>
                        </>
                      );
                    })()}
                  </div>
                </div>

                {/* Usage and Support Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Usage & Engagement</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Usage Score:</span>
                        <span className="font-medium">{Math.round(customerData.satisfaction.usage_score || 0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${customerData.satisfaction.usage_score || 0}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Support Metrics</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Tickets:</span>
                        <span className="font-medium">{customerData.satisfaction.support_tickets_count || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resolved:</span>
                        <span className="font-medium">{customerData.satisfaction.support_tickets_resolved || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resolution Rate:</span>
                        <span className="font-medium">
                          {customerData.satisfaction.support_tickets_count > 0 
                            ? Math.round((customerData.satisfaction.support_tickets_resolved / customerData.satisfaction.support_tickets_count) * 100)
                            : 100}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Implementation Progress */}
            {customerData.satisfaction && (
              <div className="bg-white border rounded-lg p-6">
                <h3 className="font-medium text-gray-900 mb-4 flex items-center">
                  <Activity className="h-4 w-4 mr-2" />
                  Implementation Progress
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-600">Current Status</span>
                      <span className="text-sm font-medium text-blue-600">
                        {customerData.satisfaction.implementation_status}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                      <div 
                        className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
                        style={{ width: `${customerData.satisfaction.completion_percentage || 0}%` }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-600">
                      {Math.round(customerData.satisfaction.completion_percentage || 0)}% Complete
                    </div>
                  </div>

                  <div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current Phase:</span>
                        <span className="font-medium">{customerData.satisfaction.current_phase || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Last Contact:</span>
                        <span className="font-medium">{formatDate(customerData.satisfaction.last_contact_date)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Next Check-in:</span>
                        <span className="font-medium">{formatDate(customerData.satisfaction.next_check_in_date)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Feedback and Testimonials */}
            {customerData.satisfaction && (customerData.satisfaction.latest_feedback || customerData.satisfaction.testimonial) && (
              <div className="bg-white border rounded-lg p-6">
                <h3 className="font-medium text-gray-900 mb-4 flex items-center">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Customer Feedback
                </h3>
                
                {customerData.satisfaction.latest_feedback && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-700 mb-2">Latest Feedback</h4>
                    <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700">
                      "{customerData.satisfaction.latest_feedback}"
                    </div>
                  </div>
                )}

                {customerData.satisfaction.testimonial && (
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Testimonial</h4>
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-3 text-sm text-gray-700">
                      "{customerData.satisfaction.testimonial}"
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Project Requirements */}
            {customerData.conversation && (
              <div className="bg-white border rounded-lg p-6">
                <h3 className="font-medium text-gray-900 mb-4 flex items-center">
                  <Target className="h-4 w-4 mr-2" />
                  Project Context
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {customerData.conversation.business_goals && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Business Goals</h4>
                      <div className="text-sm text-gray-600 bg-gray-50 rounded p-3">
                        {customerData.conversation.business_goals}
                      </div>
                    </div>
                  )}

                  {customerData.conversation.pain_points && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Pain Points Addressed</h4>
                      <div className="text-sm text-gray-600 bg-gray-50 rounded p-3">
                        {customerData.conversation.pain_points}
                      </div>
                    </div>
                  )}
                </div>

                {customerData.conversation.customer_requirements && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-700 mb-2">Customer Requirements</h4>
                    <div className="text-sm text-gray-600 bg-gray-50 rounded p-3">
                      {customerData.conversation.customer_requirements}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="p-6 text-center">
            <p className="text-gray-500">Failed to load customer details.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerDetailModal;
