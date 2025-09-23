from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class DealStatusEnum(str, Enum):
    LEAD = "lead"
    QUALIFIED_SOLUTION = "qualified_solution"
    QUALIFIED_DELIVERY = "qualified_delivery" 
    QUALIFIED_CSO = "qualified_cso"
    DEAL = "deal"
    PROJECT = "project"

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class PersonRoleEnum(str, Enum):
    SALES = "sales"
    HEAD_OF_ENGINEERING = "head_of_engineering"
    HEAD_OF_DELIVERY = "head_of_delivery"
    CSO = "cso"
    PROJECT_MANAGER = "project_manager"

# Person Schemas
class PersonBase(BaseModel):
    name: str
    email: str
    role: PersonRoleEnum
    department: Optional[str] = None
    skills: Optional[str] = None
    availability: Optional[float] = 1.0
    hourly_rate: Optional[float] = None

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Deal Schemas
class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: DealStatusEnum = DealStatusEnum.LEAD
    priority: PriorityEnum = PriorityEnum.MEDIUM
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    contact_person: Optional[str] = None  # Primary contact at customer company
    decision_makers: Optional[str] = None  # Key decision makers at customer company

    # Geographic Information
    region: Optional[str] = None  # e.g., "North America", "Europe", "Asia-Pacific"
    country: Optional[str] = None  # e.g., "United States", "Germany", "Japan"

    # Deal Overview
    velocity: Optional[str] = None  # "Fast", "Medium", "Slow"
    deal_stage: Optional[str] = None  # "Closed Won", "Closed Lost", "Negotiation", "Proposal"
    deal_description: Optional[str] = None  # Detailed description of the deal/project
    deal_probability: Optional[int] = None  # Percentage chance of closing (0-100)
    weighted_amount: Optional[float] = None  # Deal value in Euros (estimated_value * probability)

    # Financial
    estimated_value: Optional[float] = None
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None
    expected_close_date: Optional[datetime] = None

class DealCreate(DealBase):
    customer_id: Optional[int] = None
    assigned_person_id: Optional[int] = None

class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DealStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assigned_person_id: Optional[int] = None
    estimated_value: Optional[float] = None
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None
    expected_close_date: Optional[datetime] = None
    board_position: Optional[int] = None

class DealResponse(DealBase):
    id: int
    customer_id: Optional[int] = None
    assigned_person_id: Optional[int] = None
    solution_owner_id: Optional[int] = None
    board_position: int
    created_at: datetime
    updated_at: datetime
    actual_close_date: Optional[datetime] = None
    assigned_person: Optional[PersonResponse] = None
    solution_owner: Optional[PersonResponse] = None

    class Config:
        from_attributes = True

# Sprint Board Response
class SprintBoardColumn(BaseModel):
    status: DealStatusEnum
    title: str
    deals: List[DealResponse]
    count: int

class SprintBoardResponse(BaseModel):
    columns: List[SprintBoardColumn]
    total_deals: int
    total_value: float

# Conversation Data Schemas
class ConversationDataBase(BaseModel):
    customer_requirements: Optional[str] = None
    business_goals: Optional[str] = None
    pain_points: Optional[str] = None
    current_solutions: Optional[str] = None
    tech_preferences: Optional[str] = None
    integration_needs: Optional[str] = None
    compliance_requirements: Optional[str] = None
    project_timeline: Optional[str] = None
    urgency_level: Optional[str] = None
    team_size: Optional[str] = None
    location_preference: Optional[str] = None
    communication_style: Optional[str] = None
    decision_makers: Optional[str] = None
    follow_up_needed: Optional[str] = None
    sales_notes: Optional[str] = None

class ConversationDataCreate(ConversationDataBase):
    deal_id: int

class ConversationDataResponse(ConversationDataBase):
    id: int
    deal_id: int
    last_conversation_date: Optional[datetime] = None
    communication_channel: Optional[str] = None
    conversation_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Technical Solution Schemas
class TechnicalSolutionBase(BaseModel):
    solution_summary: Optional[str] = None
    recommended_tech_stack: Optional[str] = None
    architecture_overview: Optional[str] = None
    key_features: Optional[str] = None
    integration_approach: Optional[str] = None
    development_phases: Optional[str] = None
    technical_risks: Optional[str] = None
    performance_considerations: Optional[str] = None
    scalability_notes: Optional[str] = None
    security_considerations: Optional[str] = None
    estimated_development_time: Optional[str] = None
    complexity_score: Optional[float] = None

class TechnicalSolutionResponse(TechnicalSolutionBase):
    id: int
    deal_id: int
    ai_confidence_score: Optional[float] = None
    generated_by: str
    generated_at: datetime
    reviewed_by_human: bool
    human_review_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Resource Allocation Schemas
class ResourceAllocationBase(BaseModel):
    required_roles: Optional[str] = None
    team_composition: Optional[str] = None
    resource_timeline: Optional[str] = None
    development_cost: Optional[float] = None
    infrastructure_cost: Optional[float] = None
    third_party_costs: Optional[float] = None
    contingency_percentage: Optional[float] = None
    total_estimated_cost: Optional[float] = None
    in_house_resources: Optional[str] = None
    external_resources_needed: Optional[str] = None
    skill_gaps: Optional[str] = None
    estimated_start_date: Optional[datetime] = None
    estimated_delivery_date: Optional[datetime] = None
    milestone_breakdown: Optional[str] = None

class ResourceAllocationResponse(ResourceAllocationBase):
    id: int
    deal_id: int
    ai_confidence_score: Optional[float] = None
    generated_by: str
    generated_at: datetime
    reviewed_by_human: bool
    human_review_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Proposal Schemas
class ProposalBase(BaseModel):
    executive_summary: Optional[str] = None
    solution_overview: Optional[str] = None
    business_value: Optional[str] = None
    technical_approach: Optional[str] = None
    implementation_plan: Optional[str] = None
    risk_mitigation: Optional[str] = None
    cost_breakdown: Optional[str] = None
    payment_schedule: Optional[str] = None
    roi_analysis: Optional[str] = None
    project_phases: Optional[str] = None
    key_milestones: Optional[str] = None
    delivery_timeline: Optional[str] = None
    assumptions: Optional[str] = None
    scope_limitations: Optional[str] = None
    terms_and_conditions: Optional[str] = None

class ProposalResponse(ProposalBase):
    id: int
    deal_id: int
    proposal_status: str
    cso_approval: bool
    cso_review_notes: Optional[str] = None
    generated_at: datetime
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# AI Insight Schemas
class AIInsightBase(BaseModel):
    insight_type: str
    title: str
    description: str
    recommendations: Optional[str] = None
    confidence_score: Optional[float] = None
    triggered_by_status: Optional[DealStatusEnum] = None
    relevant_data_points: Optional[str] = None
    suggested_actions: Optional[str] = None

class AIInsightResponse(AIInsightBase):
    id: int
    deal_id: int
    action_taken: bool
    action_notes: Optional[str] = None
    generated_at: datetime
    ai_model_version: Optional[str] = None
    
    class Config:
        from_attributes = True

# Status Update Request
class StatusUpdateRequest(BaseModel):
    new_status: str  # Changed from DealStatusEnum to str for more flexible validation
    change_reason: Optional[str] = None
    board_position: Optional[int] = None

# AI Action Requests
class AIQualificationRequest(BaseModel):
    deal_id: int

class AISolutionRequest(BaseModel):
    deal_id: int

class AIResourceRequest(BaseModel):
    deal_id: int

class AIProposalRequest(BaseModel):
    deal_id: int

# AI Response Schemas
class AIQualificationResponse(BaseModel):
    deal_id: int
    qualification_score: float
    missing_information: List[str]
    suggested_questions: List[str]
    next_steps: List[str]
    confidence: float

class AISolutionResponse(BaseModel):
    deal_id: int
    technical_solution: Dict[str, Any]
    confidence: float
    risks: List[str]
    recommendations: List[str]

class AIResourceResponse(BaseModel):
    deal_id: int
    resource_plan: Dict[str, Any]
    cost_estimate: float
    timeline_estimate: str
    confidence: float
    skill_gaps: List[str]

class AIProposalResponse(BaseModel):
    deal_id: int
    proposal_sections: Dict[str, str]
    executive_summary: str
    total_cost: float
    timeline: str
    confidence: float

# Dashboard Analytics
class DashboardMetrics(BaseModel):
    total_deals: int
    total_pipeline_value: float
    deals_by_status: Dict[str, int]
    average_deal_size: float
    conversion_rate: float
    active_persons: int
    overdue_deals: int
    
class PersonWorkload(BaseModel):
    person: PersonResponse
    active_deals: int
    total_deal_value: float
    availability: float
    overdue_deals: int

class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    person_workloads: List[PersonWorkload]
    recent_ai_insights: List[AIInsightResponse]

# Comment Schemas
class CommentBase(BaseModel):
    commenter_name: str
    commenter_role: Optional[str] = None
    comment_text: str

class CommentCreate(CommentBase):
    deal_id: int

class CommentResponse(CommentBase):
    id: int
    deal_id: int
    created_at: datetime

    class Config:
        from_attributes = True