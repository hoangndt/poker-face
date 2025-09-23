import React, { useState, useEffect, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import {
  Users,
  Clock,
  DollarSign,
  AlertCircle,
  Plus,
  MoreHorizontal,
  User,
  Calendar,
  TrendingUp,
  Brain,
  CheckCircle,
  Circle,
  Target
} from 'lucide-react';
import { sprintAPI } from '../services/api';
import toast from 'react-hot-toast';
import DealDetailModal from './DealDetailModal';
import AIInsightPanel from './AIInsightPanel';
import AssigneeFilter from './AssigneeFilter';

const SPRINT_COLUMNS = [
  {
    id: 'lead',
    title: 'Lead',
    color: 'bg-gray-100',
    borderColor: 'border-gray-300',
    icon: Circle,
    description: 'Initial contact and qualification'
  },
  {
    id: 'qualified_solution',
    title: 'Solution',
    color: 'bg-blue-100',
    borderColor: 'border-blue-300',
    icon: Brain,
    description: 'Technical solution design'
  },
  {
    id: 'qualified_delivery',
    title: 'Delivery',
    color: 'bg-yellow-100',
    borderColor: 'border-yellow-300',
    icon: Users,
    description: 'Resource allocation and pricing'
  },
  {
    id: 'qualified_cso',
    title: 'CSO Review',
    color: 'bg-purple-100',
    borderColor: 'border-purple-300',
    icon: CheckCircle,
    description: 'Final proposal review'
  },
  {
    id: 'deal',
    title: 'Deal',
    color: 'bg-green-100',
    borderColor: 'border-green-300',
    icon: Target,
    description: 'Closed deals'
  },
  {
    id: 'project',
    title: 'Project',
    color: 'bg-emerald-100',
    borderColor: 'border-emerald-300',
    icon: TrendingUp,
    description: 'Active projects'
  }
];

const COLUMN_GROUPS = [
  {
    id: 'individual_lead',
    title: null,
    columns: ['lead']
  },
  {
    id: 'qualified_lead',
    title: 'Qualified Lead',
    description: 'Technical solution, delivery planning, and final review',
    columns: ['qualified_solution', 'qualified_delivery', 'qualified_cso']
  },
  {
    id: 'individual_deal_project',
    title: null,
    columns: ['deal', 'project']
  }
];

const PRIORITY_COLORS = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800'
};

const DealCard = ({ deal, index, onDealClick, onStatusChange }) => {
  const [showAIInsights, setShowAIInsights] = useState(false);
  const [aiInsightData, setAiInsightData] = useState(null);
  const [isLoadingInsight, setIsLoadingInsight] = useState(false);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  
  const getPriorityColor = (priority) => PRIORITY_COLORS[priority] || PRIORITY_COLORS.medium;
  
  const formatCurrency = (amount) => {
    if (!amount) return 'No budget';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const triggerAIInsight = async () => {
    try {
      setIsLoadingInsight(true);
      
      // Get the appropriate AI analysis message based on status
      const getAnalysisMessage = (status) => {
        switch (status) {
          case 'lead': return 'Analyzing lead qualification...';
          case 'qualified_solution': return 'Designing technical solution...';
          case 'qualified_delivery': return 'Planning delivery strategy...';
          case 'qualified_cso': return 'Generating commercial proposal...';
          default: return 'Running AI analysis...';
        }
      };
      
      const analysisMessage = getAnalysisMessage(deal.status);
      toast.loading(analysisMessage, { id: 'ai-analysis' });
      
      const response = await sprintAPI.triggerAIInsight(deal.id, deal.status);
      console.log('AI Insight Response:', response);
      console.log('Response data:', response.data);
      
      setAiInsightData(response.data);
      setShowAIInsights(true);
      
      // Success message based on analysis type
      const getSuccessMessage = (status) => {
        switch (status) {
          case 'lead': return 'Lead qualification complete';
          case 'qualified_solution': return 'Solution design complete';
          case 'qualified_delivery': return 'Delivery plan complete';
          case 'qualified_cso': return 'Proposal analysis complete';
          default: return 'AI analysis complete';
        }
      };
      
      toast.success(getSuccessMessage(deal.status), { id: 'ai-analysis' });
    } catch (error) {
      console.error('AI insight error:', error);
      toast.error('Failed to trigger AI analysis', { id: 'ai-analysis' });
      setShowAIInsights(false);
    } finally {
      setIsLoadingInsight(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      setShowStatusMenu(false);
      await onStatusChange(deal.id, newStatus);
      toast.success(`Status changed to ${SPRINT_COLUMNS.find(col => col.id === newStatus)?.title}`);
    } catch (error) {
      console.error('Status change error:', error);
      toast.error('Failed to change status');
    }
  };

  return (
    <Draggable draggableId={deal.id.toString()} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={() => onDealClick && onDealClick(deal.id)}
          className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-3 cursor-pointer hover:shadow-md transition-shadow ${
            snapshot.isDragging ? 'shadow-lg transform rotate-1' : ''
          }`}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900 text-sm leading-tight">
                {deal.title}
              </h4>
              <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                {deal.customer_name || 'No customer assigned'}
              </p>
            </div>
            <div className="flex items-center space-x-1 ml-2">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(deal.priority)}`}>
                {deal.priority}
              </span>

              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowStatusMenu(!showStatusMenu);
                  }}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title="Change Status"
                >
                  <MoreHorizontal className="h-4 w-4 text-gray-400" />
                </button>

                {showStatusMenu && (
                  <div className="absolute right-0 top-8 z-50 bg-white border border-gray-200 rounded-lg shadow-lg min-w-40">
                    <div className="py-1">
                      <div className="px-3 py-2 text-xs font-medium text-gray-500 border-b border-gray-100">
                        Change Status
                      </div>
                      {SPRINT_COLUMNS.map(column => {
                        const Icon = column.icon;
                        return (
                          <button
                            key={column.id}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusChange(column.id);
                            }}
                            disabled={column.id === deal.status}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                              column.id === deal.status ? 'bg-gray-50 text-gray-500' : 'text-gray-700'
                            }`}
                          >
                            <Icon className="h-4 w-4" />
                            <span>{column.title}</span>
                            {column.id === deal.status && (
                              <span className="ml-auto text-xs text-gray-400">(current)</span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Click outside to close menu */}
          {showStatusMenu && (
            <div
              className="fixed inset-0 z-40"
              onClick={() => setShowStatusMenu(false)}
            />
          )}

          {/* Click outside to close menu */}
          {showStatusMenu && (
            <div 
              className="fixed inset-0 z-40" 
              onClick={() => setShowStatusMenu(false)}
            />
          )}

          {/* Budget */}
          {(deal.budget_range_min || deal.estimated_value) && (
            <div className="flex items-center mb-2">
              <DollarSign className="h-4 w-4 text-green-600 mr-1" />
              <span className="text-sm text-gray-700">
                {deal.budget_range_min && deal.budget_range_max 
                  ? `${formatCurrency(deal.budget_range_min)} - ${formatCurrency(deal.budget_range_max)}`
                  : formatCurrency(deal.estimated_value)
                }
              </span>
            </div>
          )}

          {/* Timeline */}
          {deal.expected_close_date && (
            <div className="flex items-center mb-2">
              <Calendar className="h-4 w-4 text-blue-600 mr-1" />
              <span className="text-sm text-gray-700">
                {formatDate(deal.expected_close_date)}
              </span>
            </div>
          )}

          {/* Assigned Person */}
          {deal.assigned_person && (
            <div className="flex items-center mb-2">
              <User className="h-4 w-4 text-purple-600 mr-1" />
              <span className="text-sm text-gray-700">
                {deal.assigned_person.name}
              </span>
            </div>
          )}

          {/* AI Insights Panel */}
          {showAIInsights && aiInsightData && (
            <AIInsightPanel 
              aiInsightData={aiInsightData}
              insightType={deal.status}
              onClose={() => setShowAIInsights(false)}
            />
          )}

          {/* Loading State */}
          {isLoadingInsight && (
            <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-center text-xs text-gray-600">
                <Brain className="h-4 w-4 mr-2 animate-pulse" />
                Analyzing lead data...
              </div>
            </div>
          )}

          {/* Contract Completion Tracking for Closed Deals */}
          {deal.status === 'deal' && deal.contract_completion_status && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              {deal.contract_completion_status.is_applicable && (
                <div className="space-y-2">
                  {/* Warning for overdue tasks */}
                  {deal.contract_completion_status.is_overdue && deal.contract_completion_status.missing_tasks.length > 0 && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-xs font-medium text-red-800">
                            Contract completion overdue
                          </p>
                          <p className="text-xs text-red-700 mt-1">
                            Missing: {deal.contract_completion_status.missing_tasks.join(', ')}
                          </p>
                          {deal.contract_completion_status.needs_reminder && (
                            <p className="text-xs text-red-600 mt-1 font-medium">
                              📧 Reminder email sent
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Status for completed tasks */}
                  {deal.contract_completion_status.all_tasks_completed && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <p className="text-xs font-medium text-green-800">
                          All contract tasks completed ✓
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Status for approaching deadline */}
                  {!deal.contract_completion_status.is_overdue &&
                   !deal.contract_completion_status.all_tasks_completed &&
                   deal.contract_completion_status.missing_tasks.length > 0 && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <Clock className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-xs font-medium text-yellow-800">
                            Pending: {deal.contract_completion_status.missing_tasks.join(', ')}
                          </p>
                          <p className="text-xs text-yellow-700 mt-1">
                            {30 - deal.contract_completion_status.days_since_close} days remaining
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* AI Analysis Button */}
          {deal.status !== 'deal' && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  triggerAIInsight();
                }}
                disabled={isLoadingInsight}
                className="w-full flex items-center justify-center px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title={isLoadingInsight ? "Analyzing..." : "Trigger AI Analysis"}
              >
                <Brain className={`h-4 w-4 mr-2 ${
                  isLoadingInsight ? 'animate-pulse' : ''
                }`} />
                <span className="text-sm font-medium">
                  {isLoadingInsight ? 'Analyzing...' : 'AI Analysis'}
                </span>
              </button>

              {/* Status Indicators */}
              <div className="flex items-center justify-center space-x-2 pt-2">
                {deal.status === 'lead' && (
                  <AlertCircle className="h-4 w-4 text-orange-500" title="Needs qualification" />
                )}
                {isLoadingInsight && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" title="AI analysis in progress" />
                )}
                {showAIInsights && aiInsightData && (
                  <CheckCircle className="h-4 w-4 text-green-500" title="AI analysis complete" />
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </Draggable>
  );
};

const SprintColumn = ({ column, deals, onAddDeal, onDealClick, onStatusChange }) => {
  const IconComponent = column.icon;

  // Calculate total budget for this column
  const calculateColumnBudget = () => {
    return deals.reduce((total, deal) => {
      // Use estimated_value if available, otherwise use the average of budget range
      const dealValue = deal.estimated_value ||
        (deal.budget_range_min && deal.budget_range_max
          ? (deal.budget_range_min + deal.budget_range_max) / 2
          : deal.budget_range_min || 0);
      return total + (dealValue || 0);
    }, 0);
  };

  const formatBudget = (amount) => {
    if (amount === 0) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const totalBudget = calculateColumnBudget();

  return (
    <div className={`${column.color} rounded-lg p-4 min-h-screen w-80 flex-shrink-0`}>
      {/* Column Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <IconComponent className="h-5 w-5 text-gray-700 mr-2" />
          <h3 className="font-semibold text-gray-900">{column.title}</h3>
          <span className="ml-2 bg-white px-2 py-1 rounded-full text-xs font-medium text-gray-600">
            {deals.length}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {/* Show total budget only for Deal column (closed deals) */}
          {column.id === 'deal' && (
              <span className="ml-2 bg-blue-100 px-2 py-1 rounded-full text-xs font-medium text-blue-800">
              {formatBudget(totalBudget)}
            </span>
          )}
          {column.id === 'lead' && (
            <button
              onClick={() => onAddDeal(column.id)}
              className="p-1 hover:bg-white/50 rounded transition-colors"
              title="Add new lead"
            >
              <Plus className="h-4 w-4 text-gray-700" />
            </button>
          )}
        </div>
      </div>

      {/* Column Description */}
      <p className="text-sm text-gray-600 mb-4">{column.description}</p>

      {/* Drop Zone */}
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`min-h-96 transition-colors ${
              snapshot.isDraggingOver ? 'bg-white/30 border-2 border-dashed border-gray-400 rounded-lg' : ''
            }`}
          >
            {deals.map((deal, index) => (
              <DealCard
                key={deal.id}
                deal={deal}
                index={index}
                onDealClick={onDealClick}
                onStatusChange={onStatusChange}
              />
            ))}
            {provided.placeholder}

            {/* Empty State */}
            {deals.length === 0 && !snapshot.isDraggingOver && (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📋</div>
                <p className="text-sm">No deals in this stage</p>
              </div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );
};

const ColumnGroup = ({ group, boardData, onAddDeal, onDealClick, onStatusChange }) => {
  const groupColumns = group.columns.map(columnId =>
    SPRINT_COLUMNS.find(col => col.id === columnId)
  ).filter(Boolean);

  const getTotalDealsInGroup = () => {
    return group.columns.reduce((total, columnId) => {
      const columnData = boardData.columns.find(col => col.status === columnId);
      return total + (columnData?.deals.length || 0);
    }, 0);
  };

  if (!group.title) {
    // Render individual columns without grouping
    return (
      <>
        {groupColumns.map(column => {
          const columnData = boardData.columns.find(col => col.status === column.id) || { deals: [] };
          return (
            <SprintColumn
              key={column.id}
              column={column}
              deals={columnData.deals}
              onAddDeal={onAddDeal}
              onDealClick={onDealClick}
              onStatusChange={onStatusChange}
            />
          );
        })}
      </>
    );
  }

  return (
    <div className="relative">
      {/* Group Header - positioned above but not affecting column alignment */}
      <div className="absolute -top-10 left-0 right-0 z-10 ">
        <div className="bg-white/90 backdrop-blur-sm bg-blue-300 rounded-t-lg border border-b-0 border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-white">{group.title}</h2>
            </div>
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
              {getTotalDealsInGroup()} deals
            </span>
          </div>
        </div>
      </div>

      {/* Grouped Columns Container - subtle background */}
      <div className="bg-blue-300 backdrop-blur-sm rounded-b-xl border border-gray-200/50 p-4 pt-0">
        <div className="flex space-x-6">
          {groupColumns.map(column => {
            const columnData = boardData.columns.find(col => col.status === column.id) || { deals: [] };
            return (
              <SprintColumn
                key={column.id}
                column={column}
                deals={columnData.deals}
                onAddDeal={onAddDeal}
                onDealClick={onDealClick}
                onStatusChange={onStatusChange}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

const SprintBoard = () => {
  const [boardData, setBoardData] = useState({ columns: [] });
  const [loading, setLoading] = useState(true);
  const [showNewDealModal, setShowNewDealModal] = useState(false);
  const [selectedDealId, setSelectedDealId] = useState(null);
  const [showDealDetail, setShowDealDetail] = useState(false);
  const [allAssignees, setAllAssignees] = useState([]);
  const [selectedAssignees, setSelectedAssignees] = useState([]);

  useEffect(() => {
    fetchBoardData();
  }, []);

  // Extract unique assignees from all deals
  useEffect(() => {
    if (boardData.columns) {
      const assigneesSet = new Set();
      const assigneesList = [];

      boardData.columns.forEach(column => {
        column.deals?.forEach(deal => {
          if (deal.assigned_person && !assigneesSet.has(deal.assigned_person.id)) {
            assigneesSet.add(deal.assigned_person.id);
            assigneesList.push({
              id: deal.assigned_person.id,
              name: deal.assigned_person.name,
              email: deal.assigned_person.email,
              role: deal.assigned_person.role
            });
          }
        });
      });

      setAllAssignees(assigneesList);
    }
  }, [boardData]);

  // Filter deals based on selected assignees
  const getFilteredBoardData = () => {
    if (selectedAssignees.length === 0) {
      return boardData;
    }

    const selectedAssigneeIds = selectedAssignees.map(assignee => assignee.id);
    const filteredBoardData = {
      ...boardData,
      columns: boardData.columns.map(column => ({
        ...column,
        deals: column.deals.filter(deal =>
          deal.assigned_person && selectedAssigneeIds.includes(deal.assigned_person.id)
        )
      }))
    };

    return filteredBoardData;
  };

  const fetchBoardData = async () => {
    try {
      const response = await sprintAPI.getSprintBoard();
      setBoardData(response.data);
    } catch (error) {
      toast.error('Failed to load sprint board');
      console.error('Sprint board error:', error);
    } finally {
      setLoading(false);
    }
  };

  const onDragEnd = useCallback(async (result) => {
    const { destination, source, draggableId } = result;
    
    if (!destination) return;
    
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    try {
      // Optimistic update
      const newBoardData = { ...boardData };
      const sourceColumn = newBoardData.columns.find(col => col.status === source.droppableId);
      const destColumn = newBoardData.columns.find(col => col.status === destination.droppableId);
      
      const [movedDeal] = sourceColumn.deals.splice(source.index, 1);
      destColumn.deals.splice(destination.index, 0, movedDeal);
      
      setBoardData(newBoardData);

      // Update backend
      await sprintAPI.updateDealStatus(parseInt(draggableId), {
        new_status: destination.droppableId,
        board_position: destination.index,
        change_reason: `Moved from ${source.droppableId} to ${destination.droppableId}`
      });

      toast.success('Deal status updated');
    } catch (error) {
      toast.error('Failed to update deal status');
      fetchBoardData(); // Refresh on error
    }
  }, [boardData]);

  const handleManualStatusChange = async (dealId, newStatus) => {
    try {
      // Find the current deal
      const currentColumn = boardData.columns.find(col => 
        col.deals.some(deal => deal.id === dealId)
      );
      const deal = currentColumn?.deals.find(d => d.id === dealId);
      
      if (!deal) {
        throw new Error('Deal not found');
      }

      // Optimistic update
      const newBoardData = { ...boardData };
      const sourceColumn = newBoardData.columns.find(col => col.status === deal.status);
      const destColumn = newBoardData.columns.find(col => col.status === newStatus);
      
      // Remove from source
      const dealIndex = sourceColumn.deals.findIndex(d => d.id === dealId);
      const [movedDeal] = sourceColumn.deals.splice(dealIndex, 1);
      
      // Add to destination
      destColumn.deals.push(movedDeal);
      
      setBoardData(newBoardData);

      // Update backend
      await sprintAPI.updateDealStatus(dealId, {
        new_status: newStatus,
        board_position: destColumn.deals.length - 1,
        change_reason: `Manual status change to ${newStatus}`
      });

    } catch (error) {
      console.error('Manual status change error:', error);
      fetchBoardData(); // Refresh on error
      throw error; // Re-throw so the card can show error
    }
  };

  const handleAddDeal = (columnId) => {
    setShowNewDealModal(true);
  };

  const handleDealClick = (dealId) => {
    setSelectedDealId(dealId);
    setShowDealDetail(true);
  };

  const handleCloseDealDetail = () => {
    setShowDealDetail(false);
    setSelectedDealId(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50">
      {/* Header */}
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Sale pipeline</h1>
            <p className="text-gray-600 mt-1">
              Manage deals through the sales pipeline with AI assistance
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Total Pipeline: <span className="font-semibold">${(boardData.total_value || 0).toLocaleString()}</span>
            </div>
            <div className="text-sm text-gray-600">
              Active Deals: <span className="font-semibold">{boardData.total_deals || 0}</span>
            </div>
            
            <button
              onClick={() => setShowNewDealModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Deal
            </button>
          </div>
        </div>
      </div>

        <div className="p-6">
            <AssigneeFilter
                assignees={allAssignees}
                selectedAssignees={selectedAssignees}
                onSelectionChange={setSelectedAssignees}
            />
        </div>

      {/* Sprint Board */}
      <div className="overflow-x-auto h-full">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex space-x-8 p-6 pt-20 min-w-max">
            {COLUMN_GROUPS.map(group => (
              <ColumnGroup
                key={group.id}
                group={group}
                boardData={getFilteredBoardData()}
                onAddDeal={handleAddDeal}
                onDealClick={handleDealClick}
                onStatusChange={handleManualStatusChange}
              />
            ))}
          </div>
        </DragDropContext>
      </div>

      {/* New Deal Modal would go here */}
      {showNewDealModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New Deal</h3>
            <p className="text-gray-600 mb-4">New deal creation form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowNewDealModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowNewDealModal(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Create Deal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Deal Detail Modal */}
      <DealDetailModal
        dealId={selectedDealId}
        isOpen={showDealDetail}
        onClose={handleCloseDealDetail}
      />
    </div>
  );
};

export default SprintBoard;