import React from 'react';
import { Brain, X, Target, Users, DollarSign, Lightbulb, AlertTriangle, CheckCircle } from 'lucide-react';

const AIInsightPanel = ({ aiInsightData, insightType, onClose }) => {
  if (!aiInsightData) return null;

  const renderLeadQualificationInsights = () => (
    <div className="space-y-3">
      {/* Qualification Score */}
      <div>
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-blue-700">Qualification Score</span>
          <span className="font-medium text-blue-900">
            {aiInsightData.qualification_score ? Math.round(aiInsightData.qualification_score) : 0}%
          </span>
        </div>
        <div className="w-full bg-blue-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ 
              width: `${Math.min(aiInsightData.qualification_score || 0, 100)}%` 
            }}
          ></div>
        </div>
        <div className="text-xs text-blue-600 mt-1">
          Confidence: {aiInsightData.confidence || 0}%
        </div>
      </div>

      {/* Missing Information */}
      {aiInsightData.missing_information && aiInsightData.missing_information.length > 0 && (
        <div>
          <h6 className="text-xs font-medium text-blue-800 mb-1 flex items-center">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Missing Info:
          </h6>
          <div className="flex flex-wrap gap-1">
            {aiInsightData.missing_information.map((item, idx) => (
              <span key={idx} className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      {aiInsightData.next_steps && aiInsightData.next_steps.length > 0 && (
        <div>
          <h6 className="text-xs font-medium text-blue-800 mb-1 flex items-center">
            <Target className="h-3 w-3 mr-1" />
            Next Steps:
          </h6>
          <ul className="text-xs text-blue-700 space-y-1">
            {aiInsightData.next_steps.slice(0, 3).map((step, idx) => (
              <li key={idx} className="flex items-start">
                <span className="w-1 h-1 bg-blue-600 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderSolutionDesignInsights = () => (
    <div className="space-y-3">
      {/* Solution Score */}
      <div>
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-green-700">Solution Score</span>
          <span className="font-medium text-green-900">
            {aiInsightData.solution_score ? Math.round(aiInsightData.solution_score) : 0}%
          </span>
        </div>
        <div className="w-full bg-green-200 rounded-full h-2">
          <div 
            className="bg-green-600 h-2 rounded-full transition-all duration-500"
            style={{ 
              width: `${Math.min(aiInsightData.solution_score || 0, 100)}%` 
            }}
          ></div>
        </div>
        <div className="text-xs text-green-600 mt-1">
          Type: {aiInsightData.solution_type || 'Custom Software'}
        </div>
      </div>

      {/* Technology Stack */}
      {aiInsightData.technology_stack && (
        <div>
          <h6 className="text-xs font-medium text-green-800 mb-1 flex items-center">
            <Brain className="h-3 w-3 mr-1" />
            Tech Stack:
          </h6>
          <div className="text-xs text-green-700">
            {Object.entries(aiInsightData.technology_stack).map(([key, value]) => (
              value && value.length > 0 && (
                <div key={key} className="mb-1">
                  <span className="font-medium capitalize">{key}:</span> {Array.isArray(value) ? value.join(', ') : value}
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      {aiInsightData.timeline && (
        <div>
          <h6 className="text-xs font-medium text-green-800 mb-1 flex items-center">
            <Target className="h-3 w-3 mr-1" />
            Timeline:
          </h6>
          <div className="text-xs text-green-700">{aiInsightData.timeline}</div>
        </div>
      )}
    </div>
  );

  const renderDeliveryPlanningInsights = () => (
    <div className="space-y-3">
      {/* Delivery Score */}
      <div>
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-yellow-700">Delivery Score</span>
          <span className="font-medium text-yellow-900">
            {aiInsightData.delivery_score ? Math.round(aiInsightData.delivery_score) : 0}%
          </span>
        </div>
        <div className="w-full bg-yellow-200 rounded-full h-2">
          <div 
            className="bg-yellow-600 h-2 rounded-full transition-all duration-500"
            style={{ 
              width: `${Math.min(aiInsightData.delivery_score || 0, 100)}%` 
            }}
          ></div>
        </div>
        <div className="text-xs text-yellow-600 mt-1">
          Approach: {aiInsightData.delivery_approach || 'Agile'}
        </div>
      </div>

      {/* Team Composition */}
      {aiInsightData.team_composition && aiInsightData.team_composition.length > 0 && (
        <div>
          <h6 className="text-xs font-medium text-yellow-800 mb-1 flex items-center">
            <Users className="h-3 w-3 mr-1" />
            Team:
          </h6>
          <div className="text-xs text-yellow-700 space-y-1">
            {aiInsightData.team_composition.slice(0, 4).map((member, idx) => (
              <div key={idx} className="flex justify-between">
                <span>{member.role || 'Unknown Role'}</span>
                <span className="font-medium">{Math.round((member.allocation || 0) * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Budget Estimate */}
      {aiInsightData.budget_estimate && (
        <div>
          <h6 className="text-xs font-medium text-yellow-800 mb-1 flex items-center">
            <DollarSign className="h-3 w-3 mr-1" />
            Budget:
          </h6>
          <div className="text-xs text-yellow-700">
            {aiInsightData.budget_estimate.total_estimate || 'To be determined'}
          </div>
        </div>
      )}
    </div>
  );

  const renderProposalInsights = () => (
    <div className="space-y-3">
      {/* Proposal Score */}
      <div>
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-purple-700">Proposal Score</span>
          <span className="font-medium text-purple-900">
            {aiInsightData.proposal_score ? Math.round(aiInsightData.proposal_score) : 0}%
          </span>
        </div>
        <div className="w-full bg-purple-200 rounded-full h-2">
          <div 
            className="bg-purple-600 h-2 rounded-full transition-all duration-500"
            style={{ 
              width: `${Math.min(aiInsightData.proposal_score || 0, 100)}%` 
            }}
          ></div>
        </div>
        <div className="text-xs text-purple-600 mt-1">
          Model: {aiInsightData.pricing_model || 'Fixed Price'}
        </div>
      </div>

      {/* Commercial Terms */}
      {aiInsightData.commercial_terms && (
        <div>
          <h6 className="text-xs font-medium text-purple-800 mb-1 flex items-center">
            <DollarSign className="h-3 w-3 mr-1" />
            Investment:
          </h6>
          <div className="text-xs text-purple-700">
            {aiInsightData.commercial_terms.total_investment || 'To be determined'}
          </div>
        </div>
      )}

      {/* Value Proposition */}
      {aiInsightData.value_proposition && aiInsightData.value_proposition.length > 0 && (
        <div>
          <h6 className="text-xs font-medium text-purple-800 mb-1 flex items-center">
            <Lightbulb className="h-3 w-3 mr-1" />
            Value Props:
          </h6>
          <ul className="text-xs text-purple-700 space-y-1">
            {aiInsightData.value_proposition.slice(0, 3).map((prop, idx) => (
              <li key={idx} className="flex items-start">
                <CheckCircle className="h-3 w-3 text-purple-600 mr-1 mt-0.5 flex-shrink-0" />
                {prop}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const getInsightConfig = () => {
    switch (insightType) {
      case 'lead':
        return {
          title: 'Lead Qualification',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          titleColor: 'text-blue-900',
          renderContent: renderLeadQualificationInsights
        };
      case 'qualified_solution':
        return {
          title: 'Solution Design',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          titleColor: 'text-green-900',
          renderContent: renderSolutionDesignInsights
        };
      case 'qualified_delivery':
        return {
          title: 'Delivery Planning',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          titleColor: 'text-yellow-900',
          renderContent: renderDeliveryPlanningInsights
        };
      case 'qualified_cso':
        return {
          title: 'Commercial Proposal',
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200',
          titleColor: 'text-purple-900',
          renderContent: renderProposalInsights
        };
      default:
        return {
          title: 'AI Analysis',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          titleColor: 'text-gray-900',
          renderContent: renderLeadQualificationInsights
        };
    }
  };

  const config = getInsightConfig();

  return (
    <div className={`mt-3 p-3 ${config.bgColor} border ${config.borderColor} rounded-lg`}>
      <div className="flex items-center justify-between mb-2">
        <h5 className={`font-medium ${config.titleColor} text-sm flex items-center`}>
          <Brain className="h-4 w-4 mr-1" />
          {config.title}
        </h5>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xs p-1"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      
      {config.renderContent()}
    </div>
  );
};

export default AIInsightPanel;