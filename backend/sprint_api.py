from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import json
import re
from datetime import datetime, timedelta

from database import get_db
from sprint_models import (
    Deal, Person, ConversationData, TechnicalSolution,
    ResourceAllocation, Proposal, AIInsight, StatusHistory, Comment, Contact,
    CustomerSatisfaction, DealStatus, Priority, PersonRole
)
from sprint_schemas import (
    DealCreate, DealUpdate, DealResponse, SprintBoardResponse,
    SprintBoardColumn, PersonCreate, PersonResponse,
    StatusUpdateRequest, AIQualificationRequest, AIQualificationResponse,
    CommentCreate, CommentResponse, ContractCompletionStatus,
    ContactCreate, ContactUpdate, ContactResponse
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


def get_contract_completion_status(deal):
    """
    Calculate contract completion status for a closed deal.
    Returns dict with completion status, warnings, and missing tasks.
    """
    if not deal.actual_close_date or normalize_status(deal.status) != "deal":
        return {
            "is_applicable": False,
            "is_overdue": False,
            "missing_tasks": [],
            "days_since_close": 0,
            "deadline_date": None,
            "needs_reminder": False,
            "all_tasks_completed": False
        }

    # Calculate days since deal was closed
    days_since_close = (datetime.utcnow() - deal.actual_close_date).days
    deadline_date = deal.actual_close_date + timedelta(days=30)
    is_overdue = days_since_close > 30

    # Check which tasks are missing
    missing_tasks = []
    if not deal.contract_signed_date:
        missing_tasks.append("Contract Signed")
    if not deal.finance_contacted_date:
        missing_tasks.append("Finance Contacted")

    # Determine if reminder email should be sent
    needs_reminder = (
        is_overdue and
        len(missing_tasks) > 0 and
        (not deal.email_reminder_sent or
         (deal.last_reminder_date and
          (datetime.utcnow() - deal.last_reminder_date).days >= 7))
    )

    return {
        "is_applicable": True,
        "is_overdue": is_overdue,
        "missing_tasks": missing_tasks,
        "days_since_close": days_since_close,
        "deadline_date": deadline_date,
        "needs_reminder": needs_reminder,
        "all_tasks_completed": len(missing_tasks) == 0
    }


def create_deal_response_with_contract_status(deal):
    """
    Create a DealResponse with contract completion status included.
    """
    # Get contract completion status
    contract_status = get_contract_completion_status(deal)

    # Create the deal response data
    deal_data = {
        'id': deal.id,
        'title': deal.title,
        'description': deal.description,
        'status': deal.status,
        'priority': deal.priority,
        'customer_name': deal.customer_name,
        'customer_email': deal.customer_email,
        'contact_person': deal.contact_person,
        'decision_makers': deal.decision_makers,
        'region': deal.region,
        'country': deal.country,
        'assigned_person_id': deal.assigned_person_id,
        'solution_owner_id': deal.solution_owner_id,
        'velocity': deal.velocity,
        'deal_stage': deal.deal_stage,
        'deal_description': deal.deal_description,
        'deal_probability': deal.deal_probability,
        'weighted_amount': deal.weighted_amount,
        'estimated_value': deal.estimated_value,
        'budget_range_min': deal.budget_range_min,
        'budget_range_max': deal.budget_range_max,
        'expected_close_date': deal.expected_close_date,
        'board_position': deal.board_position,
        'created_at': deal.created_at,
        'updated_at': deal.updated_at,
        'actual_close_date': deal.actual_close_date,
        'assigned_person': deal.assigned_person,
        'solution_owner': deal.solution_owner,
        'contract_signed_date': deal.contract_signed_date,
        'finance_contacted_date': deal.finance_contacted_date,
        'email_reminder_sent': deal.email_reminder_sent,
        'last_reminder_date': deal.last_reminder_date,
        'contract_completion_status': ContractCompletionStatus(**contract_status)
    }

    return DealResponse(**deal_data)


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
                deals=[create_deal_response_with_contract_status(deal) for deal in status_deals],
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
    comments = db.query(Comment).filter(Comment.deal_id == deal_id).order_by(Comment.created_at.desc()).all()
    
    # Build comprehensive response
    detailed_deal = {
        "deal": DealResponse.from_orm(deal).dict(),
        "conversation_data": conversation_data.__dict__ if conversation_data else None,
        "technical_solution": technical_solution.__dict__ if technical_solution else None,
        "resource_allocation": resource_allocation.__dict__ if resource_allocation else None,
        "proposal": proposal.__dict__ if proposal else None,
        "ai_insights": [insight.__dict__ for insight in ai_insights],
        "status_history": [history.__dict__ for history in status_history],
        "comments": [CommentResponse.from_orm(comment).dict() for comment in comments],
        "timeline": _build_timeline(deal, status_history, ai_insights),
        "activity_summary": _build_activity_summary(deal, conversation_data, ai_insights)
    }
    
    return detailed_deal

@router.post("/deals/{deal_id}/comments")
async def create_comment(deal_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    """Add a new comment to a deal"""
    # Verify deal exists
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Create new comment
    db_comment = Comment(
        deal_id=deal_id,
        commenter_name=comment.commenter_name,
        commenter_role=comment.commenter_role,
        comment_text=comment.comment_text
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return CommentResponse.from_orm(db_comment)

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """Delete a comment by ID"""
    # Find the comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Delete the comment
    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}

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

        # Calculate conversion rate based on actual data
        closed_deals = [d for d in deals if normalize_status(d.status) in [normalize_status(DealStatus.DEAL), normalize_status(DealStatus.PROJECT)]]
        conversion_rate = len(closed_deals) / total_deals if total_deals > 0 else 0

        # Calculate overdue deals (deals past expected close date)
        from datetime import datetime
        current_date = datetime.now()
        overdue_deals = [d for d in active_deals if d.expected_close_date and d.expected_close_date < current_date]

        return {
            "metrics": {
                "total_deals": total_deals,
                "total_pipeline_value": total_pipeline_value,
                "deals_by_status": deals_by_status,
                "average_deal_size": average_deal_size,
                "conversion_rate": conversion_rate,
                "active_persons": len(persons),
                "overdue_deals": len(overdue_deals),
                "closed_deals": len(closed_deals),
                "active_deals": len(active_deals)
            },
            "person_workloads": [],  # Placeholder
            "recent_ai_insights": []  # Placeholder
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")


@router.get("/dashboard/analytics")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get enhanced dashboard analytics with historical data and trends"""
    try:
        deals = db.query(Deal).all()
        contacts = db.query(Contact).all()

        # Generate historical sales data based on actual deals
        from datetime import datetime, timedelta
        import random

        # Calculate quarterly sales from actual deals (with some mock enhancement)
        quarterly_targets = {
            "Q1 2024": 1500000,
            "Q2 2024": 2000000,
            "Q3 2024": 1800000,
            "Q4 2024": 2500000
        }

        historical_sales = []
        for quarter, target in quarterly_targets.items():
            # Use a portion of actual pipeline + some realistic variation
            base_amount = sum([deal.estimated_value or 0 for deal in deals[:12]]) / 4  # Quarter of pipeline
            variation = random.uniform(0.7, 1.3)  # ±30% variation
            amount = int(base_amount * variation)
            deals_closed = random.randint(6, 15)

            historical_sales.append({
                "quarter": quarter,
                "amount": amount,
                "target": target,
                "deals_closed": deals_closed
            })

        # Country sales analysis - Group by actual countries
        country_sales = {}
        for deal in deals:
            country = deal.country or "Unknown"
            if country not in country_sales:
                country_sales[country] = {"amount": 0, "count": 0}
            country_sales[country]["amount"] += deal.estimated_value or 0
            country_sales[country]["count"] += 1

        # Sort countries by amount and get top countries for better visualization
        sorted_countries = sorted(country_sales.items(), key=lambda x: x[1]["amount"], reverse=True)
        top_countries = dict(sorted_countries[:8])  # Show top 8 countries

        # Sales by status/stage analysis - Map database statuses to dashboard stage names
        status_to_stage_map = {
            "lead": "Prospecting",
            "qualified_solution": "Qualification",
            "qualified_delivery": "Needs Analysis",
            "qualified_cso": "Value Proposition",
            "deal": "Proposal/Price Quote",
            "project": "Negotiation/Review"
        }

        stage_sales = {}
        for deal in deals:
            status = deal.status or "lead"
            stage_name = status_to_stage_map.get(status, "Prospecting")
            if stage_name not in stage_sales:
                stage_sales[stage_name] = {"amount": 0, "count": 0}
            stage_sales[stage_name]["amount"] += deal.estimated_value or 0
            stage_sales[stage_name]["count"] += 1

        # Add missing stages with zero values to match dashboard expectations
        expected_stages = ["Prospecting", "Qualification", "Needs Analysis", "Value Proposition",
                          "Id. Decision Makers", "Perception Analysis", "Proposal/Price Quote", "Negotiation/Review"]
        for stage in expected_stages:
            if stage not in stage_sales:
                stage_sales[stage] = {"amount": 0, "count": 0}

        # Lead source analysis - Generate realistic data based on deal distribution
        lead_source_options = ["Web", "Inquiry", "Phone Inquiry", "Partner Referral", "Purchased List", "Other Sources"]
        lead_sources = {}

        # Distribute deals across lead sources with realistic proportions
        total_pipeline = sum([deal.estimated_value or 0 for deal in deals])
        source_distributions = {
            "Web": 0.35,  # 35% of pipeline
            "Inquiry": 0.25,  # 25% of pipeline
            "Phone Inquiry": 0.15,  # 15% of pipeline
            "Partner Referral": 0.10,  # 10% of pipeline
            "Purchased List": 0.08,  # 8% of pipeline
            "Other Sources": 0.07   # 7% of pipeline
        }

        for source, percentage in source_distributions.items():
            amount = int(total_pipeline * percentage)
            count = max(1, int(len(deals) * percentage))
            lead_sources[source] = {"amount": amount, "count": count}

        # Top accounts by expected revenue
        account_revenue = {}
        for deal in deals:
            company = deal.customer_name or "Unknown"
            if company not in account_revenue:
                account_revenue[company] = {"amount": 0, "count": 0}
            account_revenue[company]["amount"] += deal.estimated_value or 0
            account_revenue[company]["count"] += 1

        # Sort and get top accounts
        top_accounts = sorted(account_revenue.items(), key=lambda x: x[1]["amount"], reverse=True)[:6]

        # Monthly trend data (mock)
        monthly_trends = []
        import random
        from datetime import datetime, timedelta

        for i in range(12):
            month_date = datetime.now() - timedelta(days=30 * i)
            monthly_trends.append({
                "month": month_date.strftime("%b %Y"),
                "revenue": random.randint(200000, 800000),
                "deals": random.randint(5, 20),
                "contacts": random.randint(10, 50)
            })

        monthly_trends.reverse()  # Show chronological order

        return {
            "historical_sales": historical_sales,
            "country_analysis": [
                {"country": k, "amount": v["amount"], "count": v["count"]}
                for k, v in top_countries.items()
            ],
            "stage_analysis": [
                {"stage": k, "amount": v["amount"], "count": v["count"]}
                for k, v in stage_sales.items()
            ],
            "lead_source_analysis": [
                {"source": k, "amount": v["amount"], "count": v["count"]}
                for k, v in lead_sources.items()
            ],
            "top_accounts": [
                {"account": k, "amount": v["amount"], "count": v["count"]}
                for k, v in top_accounts
            ],
            "monthly_trends": monthly_trends,
            "summary": {
                "total_pipeline": sum([deal.estimated_value or 0 for deal in deals]),
                "total_sales": sum([deal.estimated_value or 0 for deal in deals if deal.deal_stage == "Closed Won"]),
                "total_contacts": len(contacts),
                "avg_deal_size": sum([deal.estimated_value or 0 for deal in deals]) / len(deals) if deals else 0,
                "win_rate": 0.23  # Mock win rate
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard analytics: {str(e)}")

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
    
    # Run AI analysis with error handling
    try:
        analysis = lead_qualification_agent.analyze_lead(customer_data, conversation_dict)
    except Exception as e:
        print(f"AI lead qualification failed completely: {e}")
        # Return a basic analysis when AI fails
        analysis = {
            'qualification_score': 70.0,
            'qualification_level': 'Qualified',
            'missing_information': ['Budget confirmation', 'Timeline details'],
            'suggested_questions': [
                'What is your budget range?',
                'When do you need this implemented?',
                'Who are the key decision makers?'
            ],
            'next_steps': ['Schedule technical discussion', 'Prepare proposal'],
            'recommendations': ['Proceed with qualification', 'Gather more requirements'],
            'confidence': 65.0
        }
    
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
    
    # Run AI analysis with error handling
    try:
        analysis = solution_design_agent.analyze_solution_requirements(
            customer_data, conversation_dict, technical_dict
        )
    except Exception as e:
        print(f"AI solution design failed completely: {e}")
        # Return a basic analysis when AI fails
        analysis = {
            'solution_score': 85.0,
            'solution_type': 'Web Application',
            'recommended_architecture': 'Microservices Architecture',
            'technology_stack': {
                'frontend': 'React',
                'backend': 'Node.js',
                'database': 'PostgreSQL'
            },
            'integration_requirements': ['REST API', 'Authentication'],
            'implementation_phases': ['Setup', 'Core Development', 'Integration', 'Testing'],
            'complexity_factors': ['Database design', 'API integration'],
            'recommendations': ['Use proven technologies', 'Implement in phases'],
            'estimated_timeline': '3-4 months',
            'confidence': 75.0
        }
    
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
    
    # Run AI analysis with error handling
    try:
        analysis = delivery_planning_agent.analyze_delivery_requirements(
            customer_data, conversation_dict, solution_dict
        )
    except Exception as e:
        print(f"AI delivery planning failed completely: {e}")
        # Return a basic analysis when AI fails
        analysis = {
            'delivery_score': 80.0,
            'delivery_approach': 'Agile',
            'team_composition': [
                {'role': 'Project Manager', 'allocation': '50%'},
                {'role': 'Senior Developer', 'allocation': '100%'},
                {'role': 'Frontend Developer', 'allocation': '100%'}
            ],
            'project_phases': ['Planning', 'Development', 'Testing', 'Deployment'],
            'resource_timeline': 'Q1 2024',
            'budget_estimate': {'development_cost': 100000, 'total_cost': 120000},
            'risk_mitigation': ['Regular code reviews', 'Automated testing'],
            'quality_assurance': ['Unit testing', 'Integration testing'],
            'recommendations': ['Start with MVP', 'Iterative development'],
            'confidence': 70.0
        }
    
    # Store or update resource allocation
    if resource_allocation:
        resource_allocation.team_composition = json.dumps(analysis.get('team_composition', []))
        resource_allocation.milestone_breakdown = json.dumps(analysis.get('project_phases', []))
        resource_allocation.resource_timeline = json.dumps(analysis.get('resource_timeline', ''))
        
        # Extract budget estimate and set cost fields with proper parsing
        budget_data = analysis.get('budget_estimate', {})
        resource_allocation.development_cost = parse_budget_value(budget_data.get('development_cost', 0))
        resource_allocation.total_estimated_cost = parse_budget_value(budget_data.get('total_cost', budget_data.get('total_estimate', 0)))
        
        resource_allocation.skill_gaps = json.dumps(analysis.get('risk_mitigation', []))
        resource_allocation.ai_confidence_score = analysis.get('confidence', 70.0)
    else:
        budget_data = analysis.get('budget_estimate', {})
        resource_allocation = ResourceAllocation(
            deal_id=deal_id,
            team_composition=json.dumps(analysis.get('team_composition', [])),
            milestone_breakdown=json.dumps(analysis.get('project_phases', [])),
            resource_timeline=json.dumps(analysis.get('resource_timeline', '')),
            development_cost=parse_budget_value(budget_data.get('development_cost', 0)),
            total_estimated_cost=parse_budget_value(budget_data.get('total_cost', budget_data.get('total_estimate', 0))),
            skill_gaps=json.dumps(analysis.get('risk_mitigation', [])),
            ai_confidence_score=analysis.get('confidence', 70.0)
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
    
    # Run AI analysis with error handling
    try:
        print(f"Attempting proposal generation for deal {deal_id}")
        analysis = proposal_generation_agent.analyze_proposal_requirements(
            customer_data, conversation_dict, solution_dict, delivery_dict
        )
        print(f"Proposal generation successful for deal {deal_id}")
    except Exception as e:
        print(f"AI proposal generation failed completely: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Return a basic analysis when AI fails
        analysis = {
            'proposal_score': 75.0,
            'pricing_model': 'Time & Materials',
            'commercial_terms': {'payment_terms': '30 days', 'warranty': '12 months'},
            'value_proposition': ['Cost-effective solution', 'Proven technology stack'],
            'competitive_advantages': ['Experienced team', 'Agile methodology'],
            'risk_assessment': {'technical_risk': 'Low', 'delivery_risk': 'Medium'},
            'recommendations': ['Proceed with detailed proposal', 'Schedule technical review'],
            'negotiation_strategy': ['Emphasize value', 'Flexible on timeline'],
            'success_metrics': ['On-time delivery', 'Budget adherence'],
            'confidence': 60.0
        }

    # Validate analysis data
    try:
        print(f"Validating analysis data: {analysis}")
        required_fields = ['proposal_score', 'pricing_model', 'commercial_terms', 'value_proposition',
                          'competitive_advantages', 'risk_assessment', 'recommendations',
                          'negotiation_strategy', 'success_metrics', 'confidence']
        for field in required_fields:
            if field not in analysis:
                print(f"Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")
        print("Analysis data validation successful")
    except Exception as e:
        print(f"Analysis validation failed: {e}")
        raise e
    
    # Store or update proposal
    try:
        print("Storing proposal data...")
        if proposal:
            proposal.executive_summary = f"Proposal Score: {analysis['proposal_score']:.1f}% - {analysis.get('pricing_model', '')}"
            proposal.solution_overview = json.dumps(analysis.get('value_proposition', []))
            proposal.business_value = json.dumps(analysis.get('competitive_advantages', []))
            proposal.cost_breakdown = json.dumps(analysis.get('commercial_terms', {}))
            proposal.risk_mitigation = json.dumps(analysis.get('risk_assessment', {}))
        else:
            proposal = Proposal(
                deal_id=deal_id,
                executive_summary=f"Proposal Score: {analysis['proposal_score']:.1f}% - {analysis.get('pricing_model', '')}",
                solution_overview=json.dumps(analysis.get('value_proposition', [])),
                business_value=json.dumps(analysis.get('competitive_advantages', [])),
                cost_breakdown=json.dumps(analysis.get('commercial_terms', {})),
                risk_mitigation=json.dumps(analysis.get('risk_assessment', {}))
            )
            db.add(proposal)
        print("Proposal data stored successfully")
    except Exception as e:
        print(f"Error storing proposal data: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e

    # Store AI insight
    try:
        print("Storing AI insight...")
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
        print("AI insight stored successfully")
    except Exception as e:
        print(f"Error storing AI insight: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e
    
    return {
        "deal_id": deal_id,
        "message": "Commercial proposal analysis completed",
        "proposal_score": analysis['proposal_score'],
        "pricing_model": analysis['pricing_model'],
        "commercial_terms": analysis['commercial_terms'],
        "value_proposition": analysis['value_proposition'],
        "confidence": analysis['confidence']
    }


# ==================== CONTACTS MANAGEMENT ENDPOINTS ====================

@router.get("/contacts", response_model=List[ContactResponse])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    company: Optional[str] = None,
    contact_owner_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all contacts with optional filtering and pagination.
    """
    query = db.query(Contact)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Contact.full_name.ilike(search_term)) |
            (Contact.company_name.ilike(search_term)) |
            (Contact.email.ilike(search_term)) |
            (Contact.position.ilike(search_term))
        )

    if status:
        query = query.filter(Contact.status == status)

    if company:
        query = query.filter(Contact.company_name.ilike(f"%{company}%"))

    if contact_owner_id:
        query = query.filter(Contact.contact_owner_id == contact_owner_id)

    # Apply pagination
    contacts = query.offset(skip).limit(limit).all()

    return contacts


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Get a specific contact by ID.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """
    Create a new contact.
    """
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Update only provided fields
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    contact.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Delete a contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}


@router.get("/contacts/stats/summary")
def get_contacts_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics for contacts.
    """
    total_contacts = db.query(Contact).count()

    # Count by status
    status_counts = {}
    for status in ["lead", "qualified_solution", "qualified_delivery", "qualified_cso", "deal", "project"]:
        count = db.query(Contact).filter(Contact.status == status).count()
        status_counts[status] = count

    # Total estimated revenue
    total_estimated_revenue = db.query(Contact.estimated_revenue).filter(
        Contact.estimated_revenue.isnot(None)
    ).all()
    total_revenue = sum([r[0] for r in total_estimated_revenue if r[0]])

    # Average GMV
    avg_gmv = db.query(Contact.gmv).filter(Contact.gmv.isnot(None)).all()
    average_gmv = sum([g[0] for g in avg_gmv if g[0]]) / len(avg_gmv) if avg_gmv else 0

    return {
        "total_contacts": total_contacts,
        "status_distribution": status_counts,
        "total_estimated_revenue": total_revenue,
        "average_gmv": average_gmv
    }

# Customer Success Endpoints
@router.get("/customer-success/summary")
async def get_customer_success_summary(db: Session = Depends(get_db)):
    """Get customer success summary statistics"""
    try:
        # Get all closed won deals with satisfaction data
        closed_deals = db.query(Deal).filter(Deal.deal_stage == "Closed Won").all()

        # Calculate summary statistics
        total_customers = len(closed_deals)
        total_revenue = sum([deal.estimated_value or 0 for deal in closed_deals])
        average_deal_size = total_revenue / total_customers if total_customers > 0 else 0

        # Get satisfaction metrics
        satisfaction_data = db.query(CustomerSatisfaction).all()
        avg_satisfaction = sum([cs.overall_satisfaction_score or 0 for cs in satisfaction_data]) / len(satisfaction_data) if satisfaction_data else 0
        avg_nps = sum([cs.nps_score or 0 for cs in satisfaction_data]) / len(satisfaction_data) if satisfaction_data else 0

        # Health status distribution
        health_counts = {"Green": 0, "Yellow": 0, "Red": 0}
        for cs in satisfaction_data:
            if cs.customer_health_status in health_counts:
                health_counts[cs.customer_health_status] += 1

        return {
            "total_customers": total_customers,
            "total_revenue": total_revenue,
            "average_deal_size": average_deal_size,
            "average_satisfaction_score": round(avg_satisfaction, 1),
            "average_nps_score": round(avg_nps, 0),
            "health_status_distribution": health_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customer success summary: {str(e)}")

@router.get("/customer-success/customers")
async def get_customer_success_list(
    search: Optional[str] = None,
    sort_by: Optional[str] = "close_date",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    """Get list of customers with successful deals"""
    try:
        # Base query for closed won deals
        query = db.query(Deal).filter(Deal.deal_stage == "Closed Won")

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Deal.customer_name.ilike(search_term),
                    Deal.title.ilike(search_term),
                    Deal.contact_person.ilike(search_term)
                )
            )

        # Apply sorting
        if sort_by == "deal_value":
            order_column = Deal.estimated_value
        elif sort_by == "close_date":
            order_column = Deal.actual_close_date
        elif sort_by == "customer_name":
            order_column = Deal.customer_name
        else:
            order_column = Deal.actual_close_date

        if sort_order == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

        deals = query.all()

        # Format response with satisfaction data
        customers = []
        for deal in deals:
            satisfaction = db.query(CustomerSatisfaction).filter(CustomerSatisfaction.deal_id == deal.id).first()

            customer_data = {
                "id": deal.id,
                "customer_name": deal.customer_name,
                "deal_title": deal.title,
                "deal_value": deal.estimated_value,
                "close_date": deal.actual_close_date,
                "assigned_person": {
                    "name": deal.assigned_person.name if deal.assigned_person else None,
                    "email": deal.assigned_person.email if deal.assigned_person else None
                },
                "region": deal.region,
                "country": deal.country,
                "implementation_time": deal.implementation_time,
                "satisfaction": {
                    "overall_score": satisfaction.overall_satisfaction_score if satisfaction else None,
                    "nps_score": satisfaction.nps_score if satisfaction else None,
                    "health_status": satisfaction.customer_health_status if satisfaction else "Unknown",
                    "implementation_status": satisfaction.implementation_status if satisfaction else "Unknown",
                    "completion_percentage": satisfaction.completion_percentage if satisfaction else 0
                } if satisfaction else None
            }
            customers.append(customer_data)

        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customer success list: {str(e)}")

@router.get("/customer-success/customers/{deal_id}")
async def get_customer_success_detail(deal_id: int, db: Session = Depends(get_db)):
    """Get detailed customer success information for a specific deal"""
    try:
        # Get the deal
        deal = db.query(Deal).filter(Deal.id == deal_id, Deal.deal_stage == "Closed Won").first()
        if not deal:
            raise HTTPException(status_code=404, detail="Customer not found or deal not closed")

        # Get satisfaction data
        satisfaction = db.query(CustomerSatisfaction).filter(CustomerSatisfaction.deal_id == deal_id).first()

        # Get conversation data for additional context
        conversation = db.query(ConversationData).filter(ConversationData.deal_id == deal_id).first()

        return {
            "deal": {
                "id": deal.id,
                "title": deal.title,
                "customer_name": deal.customer_name,
                "contact_person": deal.contact_person,
                "customer_email": deal.customer_email,
                "estimated_value": deal.estimated_value,
                "actual_close_date": deal.actual_close_date,
                "expected_close_date": deal.expected_close_date,
                "implementation_time": deal.implementation_time,
                "region": deal.region,
                "country": deal.country,
                "deal_description": deal.deal_description,
                "assigned_person": {
                    "name": deal.assigned_person.name if deal.assigned_person else None,
                    "email": deal.assigned_person.email if deal.assigned_person else None,
                    "department": deal.assigned_person.department if deal.assigned_person else None
                }
            },
            "satisfaction": {
                "overall_satisfaction_score": satisfaction.overall_satisfaction_score,
                "nps_score": satisfaction.nps_score,
                "customer_health_status": satisfaction.customer_health_status,
                "implementation_status": satisfaction.implementation_status,
                "completion_percentage": satisfaction.completion_percentage,
                "current_phase": satisfaction.current_phase,
                "latest_feedback": satisfaction.latest_feedback,
                "testimonial": satisfaction.testimonial,
                "last_contact_date": satisfaction.last_contact_date,
                "next_check_in_date": satisfaction.next_check_in_date,
                "support_tickets_count": satisfaction.support_tickets_count,
                "support_tickets_resolved": satisfaction.support_tickets_resolved,
                "usage_score": satisfaction.usage_score,
                "created_at": satisfaction.created_at,
                "updated_at": satisfaction.updated_at
            } if satisfaction else None,
            "conversation": {
                "customer_requirements": conversation.customer_requirements if conversation else None,
                "business_goals": conversation.business_goals if conversation else None,
                "pain_points": conversation.pain_points if conversation else None
            } if conversation else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customer success detail: {str(e)}")