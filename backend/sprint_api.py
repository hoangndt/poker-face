from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import re
from datetime import datetime, timedelta

from database import get_db
from sprint_models import (
    Deal, Person, ConversationData, TechnicalSolution, 
    ResourceAllocation, Proposal, AIInsight, StatusHistory,
    DealStatus, Priority, PersonRole
)
from sprint_schemas import (
    DealCreate, DealUpdate, DealResponse, SprintBoardResponse,
    SprintBoardColumn, PersonCreate, PersonResponse,
    StatusUpdateRequest, AIQualificationRequest, AIQualificationResponse
)
from ai_agents.lead_qualification_agent import LeadQualificationAgent
from ai_agents.solution_design_agent import SolutionDesignAgent
from ai_agents.delivery_planning_agent import DeliveryPlanningAgent
from ai_agents.proposal_generation_agent import ProposalGenerationAgent

router = APIRouter(prefix="/api/sprint", tags=["sprint"])


def normalize_status(status) -> str:
    """
    Normalize status value to string for comparison.
    Handles both enum and string status values.
    """
    if isinstance(status, str):
        return status.lower()
    else:
        # Assume it's a DealStatus enum
        return status.value.lower()


def parse_budget_value(budget_str) -> float:
    """
    Parse budget string like '$252k - $327k' or '$150,000' to numeric value.
    Returns the average of range or the single value.
    """
    if not budget_str or budget_str == 0:
        return 0.0
    
    if isinstance(budget_str, (int, float)):
        return float(budget_str)
    
    # Remove currency symbols and spaces
    cleaned = str(budget_str).replace('$', '').replace(',', '').replace(' ', '').lower()
    
    # Handle range like "252k - 327k"
    if ' - ' in cleaned or '-' in cleaned:
        parts = re.split(r'\s*-\s*', cleaned)
        if len(parts) == 2:
            try:
                low = _convert_to_number(parts[0])
                high = _convert_to_number(parts[1])
                return (low + high) / 2  # Return average
            except:
                pass
    
    # Handle single value
    try:
        return _convert_to_number(cleaned)
    except:
        return 0.0

def _convert_to_number(value_str: str) -> float:
    """Convert string like '252k' or '1.5m' to numeric value."""
    value_str = value_str.strip().lower()
    
    if value_str.endswith('k'):
        return float(value_str[:-1]) * 1000
    elif value_str.endswith('m'):
        return float(value_str[:-1]) * 1000000
    else:
        return float(value_str)


# Initialize AI agents
lead_qualification_agent = LeadQualificationAgent()
solution_design_agent = SolutionDesignAgent()
delivery_planning_agent = DeliveryPlanningAgent()
proposal_generation_agent = ProposalGenerationAgent()

# ========================
# SPRINT BOARD ENDPOINTS
# ========================

@router.get("/board", response_model=SprintBoardResponse)
async def get_sprint_board(db: Session = Depends(get_db)):
    """Get the complete sprint board with all deals organized by status"""
    try:
        # Get all deals
        deals = db.query(Deal).all()
        
        # Organize deals by status
        columns = []
        total_value = 0.0
        
        for status in DealStatus:
            # Compare using the enum value since database stores strings
            status_deals = [deal for deal in deals if str(deal.status) == status.value]
            
            # Sort by board position
            status_deals.sort(key=lambda x: x.board_position)
            
            # Calculate column value
            column_value = sum([deal.estimated_value or 0 for deal in status_deals])
            total_value += column_value
            
            columns.append(SprintBoardColumn(
                status=status,
                title=status.value.replace('_', ' ').title(),
                deals=[DealResponse.from_orm(deal) for deal in status_deals],
                count=len(status_deals)
            ))
        
        return SprintBoardResponse(
            columns=columns,
            total_deals=len(deals),
            total_value=total_value
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sprint board: {str(e)}")

# ========================
# DEAL CRUD ENDPOINTS
# ========================

@router.get("/deals", response_model=List[DealResponse])
async def get_deals(
    status: Optional[DealStatus] = None,
    assigned_person_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get deals with optional filtering"""
    query = db.query(Deal)
    
    if status:
        query = query.filter(Deal.status == status)
    if assigned_person_id:
        query = query.filter(Deal.assigned_person_id == assigned_person_id)
    
    deals = query.all()
    return [DealResponse.from_orm(deal) for deal in deals]

@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get a specific deal by ID"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponse.from_orm(deal)

@router.get("/deals/{deal_id}/detailed")
async def get_deal_detailed(deal_id: int, db: Session = Depends(get_db)):
    """Get comprehensive deal information including all related data"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Get all related data
    conversation_data = db.query(ConversationData).filter(ConversationData.deal_id == deal_id).first()
    technical_solution = db.query(TechnicalSolution).filter(TechnicalSolution.deal_id == deal_id).first()
    resource_allocation = db.query(ResourceAllocation).filter(ResourceAllocation.deal_id == deal_id).first()
    proposal = db.query(Proposal).filter(Proposal.deal_id == deal_id).first()
    ai_insights = db.query(AIInsight).filter(AIInsight.deal_id == deal_id).all()
    status_history = db.query(StatusHistory).filter(StatusHistory.deal_id == deal_id).order_by(StatusHistory.timestamp.desc()).all()
    
    # Build comprehensive response
    detailed_deal = {
        "deal": DealResponse.from_orm(deal).dict(),
        "conversation_data": conversation_data.__dict__ if conversation_data else None,
        "technical_solution": technical_solution.__dict__ if technical_solution else None,
        "resource_allocation": resource_allocation.__dict__ if resource_allocation else None,
        "proposal": proposal.__dict__ if proposal else None,
        "ai_insights": [insight.__dict__ for insight in ai_insights],
        "status_history": [history.__dict__ for history in status_history],
        "timeline": _build_timeline(deal, status_history, ai_insights),
        "activity_summary": _build_activity_summary(deal, conversation_data, ai_insights)
    }
    
    return detailed_deal

def _build_timeline(deal, status_history, ai_insights):
    """Build a chronological timeline of deal activities"""
    timeline = []
    
    # Add deal creation
    timeline.append({
        "date": deal.created_at.isoformat(),
        "type": "creation",
        "title": "Deal Created",
        "description": f"Lead '{deal.title}' was created",
        "icon": "circle"
    })
    
    # Add status changes
    for history in status_history:
        timeline.append({
            "date": history.timestamp.isoformat(),
            "type": "status_change",
            "title": f"Status Changed",
            "description": f"Moved from {history.previous_status} to {history.new_status}",
            "icon": "arrow-right"
        })
    
    # Add AI insights
    for insight in ai_insights:
        timeline.append({
            "date": insight.generated_at.isoformat(),
            "type": "ai_insight",
            "title": f"AI {insight.insight_type.replace('_', ' ').title()}",
            "description": insight.description,
            "icon": "brain"
        })
    
    # Sort by date
    timeline.sort(key=lambda x: x["date"], reverse=True)
    return timeline

def _build_activity_summary(deal, conversation_data, ai_insights):
    """Build activity summary statistics"""
    return {
        "days_since_creation": (datetime.utcnow() - deal.created_at).days,
        "last_conversation": conversation_data.last_conversation_date.isoformat() if conversation_data and conversation_data.last_conversation_date else None,
        "ai_insights_count": len(ai_insights),
        "status": deal.status if isinstance(deal.status, str) else deal.status.value,
        "priority": deal.priority if isinstance(deal.priority, str) else deal.priority.value,
        "assigned": deal.assigned_person.name if deal.assigned_person else "Unassigned"
    }

@router.post("/deals", response_model=DealResponse)
async def create_deal(deal_data: DealCreate, db: Session = Depends(get_db)):
    """Create a new deal"""
    try:
        # Get the highest board position for the status
        max_position = db.query(Deal).filter(
            Deal.status == deal_data.status
        ).count()
        
        deal = Deal(
            **deal_data.dict(),
            board_position=max_position
        )
        
        db.add(deal)
        db.commit()
        db.refresh(deal)
        
        return DealResponse.from_orm(deal)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating deal: {str(e)}")

@router.put("/deals/{deal_id}", response_model=DealResponse)
async def update_deal(deal_id: int, deal_data: DealUpdate, db: Session = Depends(get_db)):
    """Update a deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        for field, value in deal_data.dict(exclude_unset=True).items():
            setattr(deal, field, value)
        
        deal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(deal)
        
        return DealResponse.from_orm(deal)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating deal: {str(e)}")

@router.put("/deals/{deal_id}/status")
async def update_deal_status(
    deal_id: int, 
    status_data: StatusUpdateRequest, 
    db: Session = Depends(get_db)
):
    """Update deal status and handle status-specific logic"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        old_status = deal.status
        new_status = status_data.new_status
        
        # Convert string status to enum if needed
        if isinstance(new_status, str):
            try:
                new_status = DealStatus(new_status)
            except ValueError:
                # If direct value lookup fails, try by name
                try:
                    new_status = DealStatus[new_status.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid status: {new_status}. Valid statuses: {[status.value for status in DealStatus]}"
                    )
        
        # Update deal status - convert enum to string value
        deal.status = new_status.value if hasattr(new_status, 'value') else str(new_status)
        deal.updated_at = datetime.utcnow()
        
        # Update board position if provided
        if status_data.board_position is not None:
            deal.board_position = status_data.board_position
        else:
            # Set to end of new column - compare with string value
            status_value = new_status.value if hasattr(new_status, 'value') else str(new_status)
            max_position = db.query(Deal).filter(
                Deal.status == status_value,
                Deal.id != deal_id
            ).count()
            deal.board_position = max_position
        
        # Auto-assign person based on status - pass string value
        status_value = new_status.value if hasattr(new_status, 'value') else str(new_status)
        deal.assigned_person_id = _get_auto_assigned_person(status_value, db)
        
        # Log status change
        status_history = StatusHistory(
            deal_id=deal_id,
            previous_status=normalize_status(old_status),
            new_status=normalize_status(new_status),
            change_reason=status_data.change_reason
        )
        db.add(status_history)
        
        # Trigger AI insights for new status
        normalized_new_status = normalize_status(new_status)
        qualified_statuses = [
            normalize_status(DealStatus.QUALIFIED_SOLUTION), 
            normalize_status(DealStatus.QUALIFIED_DELIVERY), 
            normalize_status(DealStatus.QUALIFIED_CSO)
        ]
        if normalized_new_status in qualified_statuses:
            _trigger_ai_insight_for_status(deal_id, new_status, db)
        
        db.commit()
        db.refresh(deal)
        
        return {"message": "Deal status updated successfully", "deal": DealResponse.from_orm(deal)}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating deal status: {str(e)}")

@router.delete("/deals/{deal_id}")
async def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    """Delete a deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        db.delete(deal)
        db.commit()
        return {"message": "Deal deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting deal: {str(e)}")

# ========================
# PERSON MANAGEMENT ENDPOINTS
# ========================

@router.get("/persons", response_model=List[PersonResponse])
async def get_persons(db: Session = Depends(get_db)):
    """Get all persons/team members"""
    persons = db.query(Person).all()
    return [PersonResponse.from_orm(person) for person in persons]

@router.post("/persons", response_model=PersonResponse)
async def create_person(person_data: PersonCreate, db: Session = Depends(get_db)):
    """Create a new person/team member"""
    try:
        person = Person(**person_data.dict())
        db.add(person)
        db.commit()
        db.refresh(person)
        return PersonResponse.from_orm(person)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating person: {str(e)}")

# ========================
# AI INSIGHT ENDPOINTS
# ========================

@router.get("/ai/insight/{deal_id}")
async def get_ai_insight(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Get AI insight for a specific deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        # Use the deal's current status for AI insight
        current_status = normalize_status(deal.status)
        
        if current_status == normalize_status(DealStatus.LEAD):
            return await _trigger_lead_qualification(deal_id, db)
        elif current_status == normalize_status(DealStatus.QUALIFIED_SOLUTION):
            return {"message": "Solution AI agent not implemented yet"}
        elif current_status == normalize_status(DealStatus.QUALIFIED_DELIVERY):
            return {"message": "Delivery AI agent not implemented yet"}
        elif current_status == normalize_status(DealStatus.QUALIFIED_CSO):
            return {"message": "CSO AI agent not implemented yet"}
        else:
            return {"message": f"No AI insights available for status: {current_status}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI insight: {str(e)}")

@router.post("/ai/insight/{deal_id}")
async def trigger_ai_insight(
    deal_id: int,
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Trigger AI insight for a specific deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        current_status = normalize_status(request_data.get('current_status', deal.status))
        
        if current_status == normalize_status(DealStatus.LEAD):
            return await _trigger_lead_qualification(deal_id, db)
        elif current_status == normalize_status(DealStatus.QUALIFIED_SOLUTION):
            return await _trigger_solution_design(deal_id, db)
        elif current_status == normalize_status(DealStatus.QUALIFIED_DELIVERY):
            return await _trigger_delivery_planning(deal_id, db)
        elif current_status == normalize_status(DealStatus.QUALIFIED_CSO):
            return await _trigger_proposal_generation(deal_id, db)
        else:
            return {"message": f"No AI insights available for status: {current_status}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering AI insight: {str(e)}")

@router.post("/ai/qualification/{deal_id}", response_model=AIQualificationResponse)
async def trigger_ai_qualification(deal_id: int, db: Session = Depends(get_db)):
    """Trigger lead qualification AI analysis"""
    return await _trigger_lead_qualification(deal_id, db)

# ========================
# DASHBOARD ENDPOINTS
# ========================

@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get sprint dashboard metrics"""
    try:
        deals = db.query(Deal).all()
        persons = db.query(Person).all()
        
        # Calculate metrics
        total_deals = len(deals)
        total_pipeline_value = sum([deal.estimated_value or 0 for deal in deals])
        
        deals_by_status = {}
        for status in DealStatus:
            deals_by_status[status.value] = len([d for d in deals if normalize_status(d.status) == normalize_status(status)])
        
        excluded_statuses = [normalize_status(DealStatus.DEAL), normalize_status(DealStatus.PROJECT)]
        active_deals = [d for d in deals if normalize_status(d.status) not in excluded_statuses]
        average_deal_size = total_pipeline_value / len(active_deals) if active_deals else 0
        
        return {
            "metrics": {
                "total_deals": total_deals,
                "total_pipeline_value": total_pipeline_value,
                "deals_by_status": deals_by_status,
                "average_deal_size": average_deal_size,
                "conversion_rate": 0.25,  # Placeholder
                "active_persons": len(persons),
                "overdue_deals": 0  # Placeholder
            },
            "person_workloads": [],  # Placeholder
            "recent_ai_insights": []  # Placeholder
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")

# ========================
# HELPER FUNCTIONS
# ========================

def _get_auto_assigned_person(status, db: Session) -> Optional[int]:
    """Auto-assign person based on deal status"""
    # Normalize status to string for comparison
    normalized_status = normalize_status(status)
    
    role_mapping = {
        normalize_status(DealStatus.LEAD): PersonRole.SALES,
        normalize_status(DealStatus.QUALIFIED_SOLUTION): PersonRole.HEAD_OF_ENGINEERING,
        normalize_status(DealStatus.QUALIFIED_DELIVERY): PersonRole.HEAD_OF_DELIVERY,
        normalize_status(DealStatus.QUALIFIED_CSO): PersonRole.CSO,
        normalize_status(DealStatus.DEAL): PersonRole.SALES,
        normalize_status(DealStatus.PROJECT): PersonRole.PROJECT_MANAGER
    }
    
    required_role = role_mapping.get(normalized_status)
    if required_role:
        person = db.query(Person).filter(Person.role == required_role).first()
        return person.id if person else None
    
    return None

def _trigger_ai_insight_for_status(deal_id: int, status: DealStatus, db: Session):
    """Trigger appropriate AI insight based on status"""
    # This would trigger different AI agents based on status
    # For now, just create a placeholder insight
    
    insight = AIInsight(
        deal_id=deal_id,
        insight_type=f"{status.value}_analysis",
        title=f"AI Analysis for {status.value.replace('_', ' ').title()}",
        description=f"Automatic AI analysis triggered for status change to {status.value}",
        triggered_by_status=normalize_status(status),
        ai_model_version="v1.0"
    )
    
    db.add(insight)

async def _trigger_lead_qualification(deal_id: int, db: Session) -> AIQualificationResponse:
    """Trigger lead qualification AI analysis"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Get conversation data
    conversation_data = db.query(ConversationData).filter(
        ConversationData.deal_id == deal_id
    ).first()
    
    # Prepare data for AI agent
    customer_data = {
        'id': deal.id,
        'Industry': deal.customer_name,  # Placeholder
        'Decision_Maker_Role': conversation_data.decision_makers if conversation_data else None,
        'budget_range_min': deal.budget_range_min,
        'budget_range_max': deal.budget_range_max,
    }
    
    conversation_dict = {}
    if conversation_data:
        conversation_dict = {
            'customer_requirements': conversation_data.customer_requirements,
            'business_goals': conversation_data.business_goals,
            'pain_points': conversation_data.pain_points,
            'tech_preferences': conversation_data.tech_preferences,
            'project_timeline': conversation_data.project_timeline,
            'urgency_level': conversation_data.urgency_level,
            'decision_makers': conversation_data.decision_makers,
            'sales_notes': conversation_data.sales_notes
        }
    
    # Run AI analysis
    analysis = lead_qualification_agent.analyze_lead(customer_data, conversation_dict)
    
    # Store AI insight
    insight = AIInsight(
        deal_id=deal_id,
        insight_type="lead_qualification",
        title="Lead Qualification Analysis",
        description=f"Qualification Score: {analysis['qualification_score']:.1f}% - {analysis['qualification_level']}",
        recommendations=json.dumps(analysis['recommendations']),
        confidence_score=analysis['confidence'],
        triggered_by_status=normalize_status(DealStatus.LEAD),
        relevant_data_points=json.dumps(analysis['missing_information']),
        suggested_actions=json.dumps(analysis['next_steps']),
        ai_model_version="lead_qualification_v1.0"
    )
    
    db.add(insight)
    db.commit()
    
    return AIQualificationResponse(
        deal_id=deal_id,
        qualification_score=analysis['qualification_score'],
        missing_information=analysis['missing_information'],
        suggested_questions=analysis['suggested_questions'][:5],
        next_steps=analysis['next_steps'],
        confidence=analysis['confidence']
    )

async def _trigger_solution_design(deal_id: int, db: Session) -> dict:
    """Trigger solution design AI analysis"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Get conversation data
    conversation_data = db.query(ConversationData).filter(
        ConversationData.deal_id == deal_id
    ).first()
    
    # Get existing technical solution data (if any)
    technical_solution = db.query(TechnicalSolution).filter(
        TechnicalSolution.deal_id == deal_id
    ).first()
    
    # Prepare data for AI agent
    customer_data = {
        'id': deal.id,
        'Industry': deal.customer_name,  # Using customer_name as placeholder
        'budget_range_min': deal.budget_range_min,
        'budget_range_max': deal.budget_range_max,
    }
    
    conversation_dict = {}
    if conversation_data:
        conversation_dict = {
            'customer_requirements': conversation_data.customer_requirements,
            'business_goals': conversation_data.business_goals,
            'pain_points': conversation_data.pain_points,
            'tech_preferences': conversation_data.tech_preferences,
            'project_timeline': conversation_data.project_timeline,
            'urgency_level': conversation_data.urgency_level,
            'decision_makers': conversation_data.decision_makers,
            'sales_notes': conversation_data.sales_notes
        }
    
    technical_dict = {}
    if technical_solution:
        technical_dict = {
            'existing_architecture': technical_solution.architecture_overview,
            'technology_stack': technical_solution.recommended_tech_stack,
            'integration_requirements': technical_solution.integration_approach
        }
    
    # Run AI analysis
    analysis = solution_design_agent.analyze_solution_requirements(
        customer_data, conversation_dict, technical_dict
    )
    
    # Store or update technical solution
    if technical_solution:
        technical_solution.architecture_overview = analysis.get('recommended_architecture', '')
        technical_solution.recommended_tech_stack = json.dumps(analysis.get('technology_stack', {}))
        technical_solution.integration_approach = json.dumps(analysis.get('integration_requirements', []))
        technical_solution.development_phases = json.dumps(analysis.get('implementation_phases', []))
        technical_solution.complexity_score = analysis.get('solution_score', 0)
    else:
        technical_solution = TechnicalSolution(
            deal_id=deal_id,
            architecture_overview=analysis.get('recommended_architecture', ''),
            recommended_tech_stack=json.dumps(analysis.get('technology_stack', {})),
            integration_approach=json.dumps(analysis.get('integration_requirements', [])),
            development_phases=json.dumps(analysis.get('implementation_phases', [])),
            complexity_score=analysis.get('solution_score', 0)
        )
        db.add(technical_solution)
    
    # Store AI insight
    insight = AIInsight(
        deal_id=deal_id,
        insight_type="solution_design",
        title="Technical Solution Design",
        description=f"Solution Score: {analysis['solution_score']:.1f}% - {analysis['solution_type']}",
        recommendations=json.dumps(analysis['recommendations']),
        confidence_score=analysis['confidence'],
        triggered_by_status=normalize_status(DealStatus.QUALIFIED_SOLUTION),
        relevant_data_points=json.dumps(analysis['complexity_factors']),
        suggested_actions=json.dumps(analysis['implementation_phases']),
        ai_model_version="solution_design_v1.0"
    )
    
    db.add(insight)
    db.commit()
    
    return {
        "deal_id": deal_id,
        "message": "Solution design analysis completed",
        "solution_score": analysis['solution_score'],
        "solution_type": analysis['solution_type'],
        "architecture": analysis['recommended_architecture'],
        "technology_stack": analysis['technology_stack'],
        "timeline": analysis['estimated_timeline'],
        "confidence": analysis['confidence']
    }

async def _trigger_delivery_planning(deal_id: int, db: Session) -> dict:
    """Trigger delivery planning AI analysis"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Get conversation data
    conversation_data = db.query(ConversationData).filter(
        ConversationData.deal_id == deal_id
    ).first()
    
    # Get technical solution data
    technical_solution = db.query(TechnicalSolution).filter(
        TechnicalSolution.deal_id == deal_id
    ).first()
    
    # Get existing resource allocation data (if any)
    resource_allocation = db.query(ResourceAllocation).filter(
        ResourceAllocation.deal_id == deal_id
    ).first()
    
    # Prepare data for AI agent
    customer_data = {
        'id': deal.id,
        'Industry': deal.customer_name,
        'budget_range_min': deal.budget_range_min,
        'budget_range_max': deal.budget_range_max,
    }
    
    conversation_dict = {}
    if conversation_data:
        conversation_dict = {
            'customer_requirements': conversation_data.customer_requirements,
            'business_goals': conversation_data.business_goals,
            'pain_points': conversation_data.pain_points,
            'tech_preferences': conversation_data.tech_preferences,
            'project_timeline': conversation_data.project_timeline,
            'urgency_level': conversation_data.urgency_level,
            'decision_makers': conversation_data.decision_makers,
            'sales_notes': conversation_data.sales_notes
        }
    
    solution_dict = {}
    if technical_solution:
        solution_dict = {
            'solution_type': technical_solution.architecture_overview,
            'technology_stack': json.loads(technical_solution.recommended_tech_stack or '{}'),
            'integration_requirements': json.loads(technical_solution.integration_approach or '[]'),
            'implementation_phases': json.loads(technical_solution.development_phases or '[]'),
            'solution_score': technical_solution.complexity_score
        }
    
    # Run AI analysis
    analysis = delivery_planning_agent.analyze_delivery_requirements(
        customer_data, conversation_dict, solution_dict
    )
    
    # Store or update resource allocation
    if resource_allocation:
        resource_allocation.team_composition = json.dumps(analysis.get('team_composition', []))
        resource_allocation.milestone_breakdown = json.dumps(analysis.get('project_phases', []))
        resource_allocation.resource_timeline = json.dumps(analysis.get('resource_timeline', ''))
        
        # Extract budget estimate and set cost fields with proper parsing
        budget_data = analysis.get('budget_estimate', {})
        resource_allocation.development_cost = parse_budget_value(budget_data.get('development_cost', 0))
        resource_allocation.total_estimated_cost = parse_budget_value(budget_data.get('total_cost', 0))
        
        resource_allocation.skill_gaps = json.dumps(analysis.get('risk_mitigation', []))
    else:
        budget_data = analysis.get('budget_estimate', {})
        resource_allocation = ResourceAllocation(
            deal_id=deal_id,
            team_composition=json.dumps(analysis.get('team_composition', [])),
            milestone_breakdown=json.dumps(analysis.get('project_phases', [])),
            resource_timeline=json.dumps(analysis.get('resource_timeline', '')),
            development_cost=parse_budget_value(budget_data.get('development_cost', 0)),
            total_estimated_cost=parse_budget_value(budget_data.get('total_cost', 0)),
            skill_gaps=json.dumps(analysis.get('risk_mitigation', []))
        )
        db.add(resource_allocation)
    
    # Store AI insight
    insight = AIInsight(
        deal_id=deal_id,
        insight_type="delivery_planning",
        title="Delivery Planning Analysis",
        description=f"Delivery Score: {analysis['delivery_score']:.1f}% - {analysis['delivery_approach']}",
        recommendations=json.dumps(analysis['recommendations']),
        confidence_score=analysis['confidence'],
        triggered_by_status=normalize_status(DealStatus.QUALIFIED_DELIVERY),
        relevant_data_points=json.dumps(analysis['risk_mitigation']),
        suggested_actions=json.dumps(analysis['quality_assurance']),
        ai_model_version="delivery_planning_v1.0"
    )
    
    db.add(insight)
    db.commit()
    
    return {
        "deal_id": deal_id,
        "message": "Delivery planning analysis completed",
        "delivery_score": analysis['delivery_score'],
        "delivery_approach": analysis['delivery_approach'],
        "team_composition": analysis['team_composition'],
        "timeline": analysis['resource_timeline'],
        "budget_estimate": analysis['budget_estimate'],
        "confidence": analysis['confidence']
    }

async def _trigger_proposal_generation(deal_id: int, db: Session) -> dict:
    """Trigger proposal generation AI analysis"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Get all related data
    conversation_data = db.query(ConversationData).filter(
        ConversationData.deal_id == deal_id
    ).first()
    
    technical_solution = db.query(TechnicalSolution).filter(
        TechnicalSolution.deal_id == deal_id
    ).first()
    
    resource_allocation = db.query(ResourceAllocation).filter(
        ResourceAllocation.deal_id == deal_id
    ).first()
    
    # Get existing proposal data (if any)
    proposal = db.query(Proposal).filter(
        Proposal.deal_id == deal_id
    ).first()
    
    # Prepare data for AI agent
    customer_data = {
        'id': deal.id,
        'Industry': deal.customer_name,
        'budget_range_min': deal.budget_range_min,
        'budget_range_max': deal.budget_range_max,
    }
    
    conversation_dict = {}
    if conversation_data:
        conversation_dict = {
            'customer_requirements': conversation_data.customer_requirements,
            'business_goals': conversation_data.business_goals,
            'pain_points': conversation_data.pain_points,
            'tech_preferences': conversation_data.tech_preferences,
            'project_timeline': conversation_data.project_timeline,
            'urgency_level': conversation_data.urgency_level,
            'decision_makers': conversation_data.decision_makers,
            'sales_notes': conversation_data.sales_notes
        }
    
    solution_dict = {}
    if technical_solution:
        solution_dict = {
            'solution_type': technical_solution.architecture_overview,
            'technology_stack': json.loads(technical_solution.recommended_tech_stack or '{}'),
            'integration_requirements': json.loads(technical_solution.integration_approach or '[]'),
            'implementation_phases': json.loads(technical_solution.development_phases or '[]'),
            'solution_score': technical_solution.complexity_score
        }
    
    delivery_dict = {}
    if resource_allocation:
        delivery_dict = {
            'team_composition': json.loads(resource_allocation.team_composition or '[]'),
            'project_phases': json.loads(resource_allocation.milestone_breakdown or '[]'),
            'resource_timeline': json.loads(resource_allocation.resource_timeline or '""'),
            'budget_estimate': {
                'development_cost': resource_allocation.development_cost or 0,
                'total_cost': resource_allocation.total_estimated_cost or 0
            },
            'delivery_approach': 'Agile'  # Default
        }
    
    # Run AI analysis
    analysis = proposal_generation_agent.analyze_proposal_requirements(
        customer_data, conversation_dict, solution_dict, delivery_dict
    )
    
    # Store or update proposal
    if proposal:
        proposal.proposal_summary = f"Proposal Score: {analysis['proposal_score']:.1f}%"
        proposal.pricing_model = analysis.get('pricing_model', '')
        proposal.commercial_terms = json.dumps(analysis.get('commercial_terms', {}))
        proposal.value_proposition = json.dumps(analysis.get('value_proposition', []))
        proposal.competitive_analysis = json.dumps(analysis.get('competitive_advantages', []))
        proposal.risk_mitigation = json.dumps(analysis.get('risk_assessment', {}))
    else:
        proposal = Proposal(
            deal_id=deal_id,
            proposal_summary=f"Proposal Score: {analysis['proposal_score']:.1f}%",
            pricing_model=analysis.get('pricing_model', ''),
            commercial_terms=json.dumps(analysis.get('commercial_terms', {})),
            value_proposition=json.dumps(analysis.get('value_proposition', [])),
            competitive_analysis=json.dumps(analysis.get('competitive_advantages', [])),
            risk_mitigation=json.dumps(analysis.get('risk_assessment', {}))
        )
        db.add(proposal)
    
    # Store AI insight
    insight = AIInsight(
        deal_id=deal_id,
        insight_type="proposal_generation",
        title="Commercial Proposal Analysis",
        description=f"Proposal Score: {analysis['proposal_score']:.1f}% - {analysis['pricing_model']}",
        recommendations=json.dumps(analysis['recommendations']),
        confidence_score=analysis['confidence'],
        triggered_by_status=normalize_status(DealStatus.QUALIFIED_CSO),
        relevant_data_points=json.dumps(analysis['negotiation_strategy']),
        suggested_actions=json.dumps(analysis['success_metrics']),
        ai_model_version="proposal_generation_v1.0"
    )
    
    db.add(insight)
    db.commit()
    
    return {
        "deal_id": deal_id,
        "message": "Commercial proposal analysis completed",
        "proposal_score": analysis['proposal_score'],
        "pricing_model": analysis['pricing_model'],
        "commercial_terms": analysis['commercial_terms'],
        "value_proposition": analysis['value_proposition'],
        "confidence": analysis['confidence']
    }