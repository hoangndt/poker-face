from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class DealStatus(enum.Enum):
    LEAD = "lead"
    QUALIFIED_SOLUTION = "qualified_solution"
    QUALIFIED_DELIVERY = "qualified_delivery" 
    QUALIFIED_CSO = "qualified_cso"
    DEAL = "deal"
    PROJECT = "project"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class PersonRole(enum.Enum):
    SALES = "sales"
    HEAD_OF_ENGINEERING = "head_of_engineering"
    HEAD_OF_DELIVERY = "head_of_delivery"
    CSO = "cso"
    PROJECT_MANAGER = "project_manager"

# Team Members/Persons
class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    role = Column(Enum(PersonRole), nullable=False)
    department = Column(String)
    skills = Column(Text)  # JSON string of skills
    availability = Column(Float, default=1.0)  # 0.0 to 1.0 (0% to 100% available)
    hourly_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_deals = relationship("Deal", foreign_keys="Deal.assigned_person_id", back_populates="assigned_person")

# Main Deal/Sprint Card
class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="lead")  # Temporarily using String instead of Enum
    priority = Column(String, default="medium")

    # Customer Information
    customer_name = Column(String)
    customer_email = Column(String)
    contact_person = Column(String)  # Primary contact at customer company
    decision_makers = Column(String)  # Key decision makers at customer company

    # Geographic Information
    region = Column(String)  # e.g., "North America", "Europe", "Asia-Pacific"
    country = Column(String)  # e.g., "United States", "Germany", "Japan"

    # Assignment
    assigned_person_id = Column(Integer, ForeignKey("persons.id"))
    assigned_person = relationship("Person", foreign_keys=[assigned_person_id], back_populates="assigned_deals")
    solution_owner_id = Column(Integer, ForeignKey("persons.id"))
    solution_owner = relationship("Person", foreign_keys=[solution_owner_id])

    # Deal Overview
    velocity = Column(String)  # "Fast", "Medium", "Slow"
    deal_stage = Column(String)  # "Closed Won", "Closed Lost", "Negotiation", "Proposal"
    deal_description = Column(Text)  # Detailed description of the deal/project
    deal_probability = Column(Integer)  # Percentage chance of closing (0-100)
    weighted_amount = Column(Float)  # Deal value in Euros (estimated_value * probability)

    # Financial
    estimated_value = Column(Float)
    budget_range_min = Column(Float)
    budget_range_max = Column(Float)

    # Timeline
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expected_close_date = Column(DateTime)
    actual_close_date = Column(DateTime)

    # Sprint Board Position
    board_position = Column(Integer, default=0)  # For ordering within status column
    
    # Relationships
    conversation_data = relationship("ConversationData", back_populates="deal", uselist=False)
    technical_solution = relationship("TechnicalSolution", back_populates="deal", uselist=False)
    resource_allocation = relationship("ResourceAllocation", back_populates="deal", uselist=False)
    proposal = relationship("Proposal", back_populates="deal", uselist=False)
    ai_insights = relationship("AIInsight", back_populates="deal")
    status_history = relationship("StatusHistory", back_populates="deal")

# Customer Conversation Data
class ConversationData(Base):
    __tablename__ = "conversation_data"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), unique=True)
    
    # Requirements
    customer_requirements = Column(Text)
    business_goals = Column(Text)
    pain_points = Column(Text)
    current_solutions = Column(Text)
    
    # Technical Preferences
    tech_preferences = Column(Text)
    integration_needs = Column(Text)
    compliance_requirements = Column(Text)
    
    # Project Details
    project_timeline = Column(String)
    urgency_level = Column(String)
    team_size = Column(String)
    location_preference = Column(String)
    
    # Communication
    communication_style = Column(String)
    decision_makers = Column(Text)
    follow_up_needed = Column(Text)
    sales_notes = Column(Text)
    
    # Metadata
    last_conversation_date = Column(DateTime)
    communication_channel = Column(String)
    conversation_type = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deal = relationship("Deal", back_populates="conversation_data")

# Technical Solution (AI Generated)
class TechnicalSolution(Base):
    __tablename__ = "technical_solutions"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), unique=True)
    
    # AI Generated Content
    solution_summary = Column(Text)
    recommended_tech_stack = Column(Text)  # JSON string
    architecture_overview = Column(Text)
    key_features = Column(Text)  # JSON string
    integration_approach = Column(Text)
    
    # Technical Details
    development_phases = Column(Text)  # JSON string
    technical_risks = Column(Text)  # JSON string
    performance_considerations = Column(Text)
    scalability_notes = Column(Text)
    security_considerations = Column(Text)
    
    # Estimates
    estimated_development_time = Column(String)
    complexity_score = Column(Float)  # 1-10 scale
    
    # AI Metadata
    ai_confidence_score = Column(Float)  # 0-1 scale
    generated_by = Column(String, default="AI_Agent_v1.0")
    generated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by_human = Column(Boolean, default=False)
    human_review_notes = Column(Text)
    
    # Relationships
    deal = relationship("Deal", back_populates="technical_solution")

# Resource Allocation (AI Generated)
class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), unique=True)
    
    # Team Structure
    required_roles = Column(Text)  # JSON string
    team_composition = Column(Text)  # JSON string
    resource_timeline = Column(Text)  # JSON string
    
    # Cost Breakdown
    development_cost = Column(Float)
    infrastructure_cost = Column(Float)
    third_party_costs = Column(Float)
    contingency_percentage = Column(Float)
    total_estimated_cost = Column(Float)
    
    # Resource Details
    in_house_resources = Column(Text)  # JSON string mapping to Person IDs
    external_resources_needed = Column(Text)  # JSON string
    skill_gaps = Column(Text)  # JSON string
    
    # Timeline
    estimated_start_date = Column(DateTime)
    estimated_delivery_date = Column(DateTime)
    milestone_breakdown = Column(Text)  # JSON string
    
    # AI Metadata
    ai_confidence_score = Column(Float)
    generated_by = Column(String, default="AI_Agent_v1.0")
    generated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by_human = Column(Boolean, default=False)
    human_review_notes = Column(Text)
    
    # Relationships
    deal = relationship("Deal", back_populates="resource_allocation")

# Final Proposal (AI Compiled)
class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), unique=True)
    
    # Executive Summary
    executive_summary = Column(Text)
    solution_overview = Column(Text)
    business_value = Column(Text)
    
    # Technical Section
    technical_approach = Column(Text)
    implementation_plan = Column(Text)
    risk_mitigation = Column(Text)
    
    # Financial Section
    cost_breakdown = Column(Text)  # JSON string
    payment_schedule = Column(Text)  # JSON string
    roi_analysis = Column(Text)
    
    # Timeline
    project_phases = Column(Text)  # JSON string
    key_milestones = Column(Text)  # JSON string
    delivery_timeline = Column(Text)
    
    # Terms
    assumptions = Column(Text)
    scope_limitations = Column(Text)
    terms_and_conditions = Column(Text)
    
    # Status
    proposal_status = Column(String, default="draft")  # draft, review, approved, sent, accepted, rejected
    cso_approval = Column(Boolean, default=False)
    cso_review_notes = Column(Text)
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    sent_at = Column(DateTime)
    
    # Relationships
    deal = relationship("Deal", back_populates="proposal")

# AI Insights and Recommendations
class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"))
    
    # Insight Details
    insight_type = Column(String)  # lead_qualification, solution_recommendation, resource_suggestion, etc.
    title = Column(String)
    description = Column(Text)
    recommendations = Column(Text)  # JSON string
    confidence_score = Column(Float)
    
    # Context
    triggered_by_status = Column(String)
    relevant_data_points = Column(Text)  # JSON string
    
    # Actions
    suggested_actions = Column(Text)  # JSON string
    action_taken = Column(Boolean, default=False)
    action_notes = Column(Text)
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    ai_model_version = Column(String)
    
    # Relationships
    deal = relationship("Deal", back_populates="ai_insights")

# Status Change History
class StatusHistory(Base):
    __tablename__ = "status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"))
    
    previous_status = Column(String)
    new_status = Column(String)
    changed_by_person_id = Column(Integer, ForeignKey("persons.id"))
    change_reason = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    deal = relationship("Deal", back_populates="status_history")

# In-house Resource Ratings (for resource allocation AI)
class ResourceRating(Base):
    __tablename__ = "resource_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    
    # Technical Skills (1-10 scale)
    frontend_rating = Column(Float, default=0)
    backend_rating = Column(Float, default=0)
    database_rating = Column(Float, default=0)
    devops_rating = Column(Float, default=0)
    mobile_rating = Column(Float, default=0)
    ai_ml_rating = Column(Float, default=0)
    
    # Domain Expertise
    domain_expertise = Column(Text)  # JSON string of industry/domain knowledge
    technology_expertise = Column(Text)  # JSON string of specific technologies
    
    # Soft Skills
    leadership_rating = Column(Float, default=0)
    communication_rating = Column(Float, default=0)
    problem_solving_rating = Column(Float, default=0)
    
    # Performance Metrics
    project_success_rate = Column(Float, default=0)
    client_satisfaction_score = Column(Float, default=0)
    delivery_timeliness = Column(Float, default=0)
    
    # Availability and Preferences
    current_workload = Column(Float, default=0)  # 0-1 scale
    preferred_project_types = Column(Text)  # JSON string
    availability_start_date = Column(DateTime)
    
    last_updated = Column(DateTime, default=datetime.utcnow)