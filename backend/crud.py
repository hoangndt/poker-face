from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models import CustomerData, LifecycleStage, CustomerActivity, ChurnPredictions
from schemas import LifecycleAnalytics, RevenueMetrics

def get_customers(db: Session, skip: int = 0, limit: int = 100, stage: Optional[str] = None):
    """Get customers with optional filtering"""
    query = db.query(CustomerData)
    
    if stage:
        if stage.lower() == "lead":
            query = query.filter(CustomerData.Customer_Flag == False)
        elif stage.lower() == "mql":
            query = query.filter(CustomerData.MQL_Flag == True)
        elif stage.lower() == "sql":
            query = query.filter(CustomerData.SQL_Flag == True)
        elif stage.lower() == "customer":
            query = query.filter(CustomerData.Customer_Flag == True)
        elif stage.lower() == "churned":
            query = query.filter(CustomerData.Churn_Flag == True)
    
    return query.offset(skip).limit(limit).all()

def get_customer(db: Session, customer_id: int):
    """Get a specific customer by ID"""
    return db.query(CustomerData).filter(CustomerData.id == customer_id).first()

def get_all_customers(db: Session):
    """Get all customers for model training"""
    return db.query(CustomerData).all()

def update_customer_stage(db: Session, customer_id: int, new_stage: str):
    """Update customer lifecycle stage"""
    customer = get_customer(db, customer_id)
    if not customer:
        return False
    
    # Update flags based on stage
    if new_stage.lower() == "mql":
        customer.MQL_Flag = True
        customer.MQL_Date = datetime.utcnow()
    elif new_stage.lower() == "sql":
        customer.SQL_Flag = True
        customer.SQL_Date = datetime.utcnow()
    elif new_stage.lower() == "customer":
        customer.Customer_Flag = True
        customer.Conversion_Date = datetime.utcnow()
    elif new_stage.lower() == "churned":
        customer.Churn_Flag = True
        customer.Churn_Date = datetime.utcnow()
    
    customer.updated_at = datetime.utcnow()
    db.commit()
    return True

def get_lifecycle_analytics(db: Session) -> LifecycleAnalytics:
    """Get comprehensive lifecycle analytics"""
    total_records = db.query(CustomerData).count()
    total_mqls = db.query(CustomerData).filter(CustomerData.MQL_Flag == True).count()
    total_sqls = db.query(CustomerData).filter(CustomerData.SQL_Flag == True).count()
    total_customers = db.query(CustomerData).filter(CustomerData.Customer_Flag == True).count()
    churned_customers = db.query(CustomerData).filter(CustomerData.Churn_Flag == True).count()
    
    # Calculate conversion rates
    lead_to_mql_rate = (total_mqls / total_records * 100) if total_records > 0 else 0
    mql_to_sql_rate = (total_sqls / total_mqls * 100) if total_mqls > 0 else 0
    sql_to_customer_rate = (total_customers / total_sqls * 100) if total_sqls > 0 else 0
    overall_conversion_rate = (total_customers / total_records * 100) if total_records > 0 else 0
    
    # Calculate averages
    avg_sales_cycle = db.query(func.avg(CustomerData.Sales_Cycle_Days)).filter(
        CustomerData.Customer_Flag == True
    ).scalar() or 0
    
    total_revenue = db.query(func.sum(CustomerData.ACV_USD)).filter(
        CustomerData.Customer_Flag == True
    ).scalar() or 0
    
    avg_clv = db.query(func.avg(CustomerData.LTV_USD)).filter(
        CustomerData.Customer_Flag == True
    ).scalar() or 0
    
    return LifecycleAnalytics(
        total_leads=total_records,
        total_mqls=total_mqls,
        total_sqls=total_sqls,
        total_customers=total_customers,
        churned_customers=churned_customers,
        lead_to_mql_rate=lead_to_mql_rate,
        mql_to_sql_rate=mql_to_sql_rate,
        sql_to_customer_rate=sql_to_customer_rate,
        overall_conversion_rate=overall_conversion_rate,
        average_sales_cycle_days=avg_sales_cycle,
        total_revenue=total_revenue,
        average_clv=avg_clv
    )

def get_conversion_rates(db: Session):
    """Get detailed conversion rates between stages"""
    # This would typically involve more complex queries to track stage transitions
    analytics = get_lifecycle_analytics(db)
    
    return {
        "funnel_metrics": {
            "leads": analytics.total_leads,
            "mqls": analytics.total_mqls,
            "sqls": analytics.total_sqls,
            "customers": analytics.total_customers,
            "churned": analytics.churned_customers
        },
        "conversion_rates": {
            "lead_to_mql": analytics.lead_to_mql_rate,
            "mql_to_sql": analytics.mql_to_sql_rate,
            "sql_to_customer": analytics.sql_to_customer_rate,
            "overall": analytics.overall_conversion_rate
        },
        "time_metrics": {
            "average_sales_cycle_days": analytics.average_sales_cycle_days
        }
    }

def get_revenue_metrics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> RevenueMetrics:
    """Get revenue metrics and KPIs"""
    query = db.query(CustomerData).filter(CustomerData.Customer_Flag == True)
    
    if start_date:
        query = query.filter(CustomerData.Conversion_Date >= start_date)
    if end_date:
        query = query.filter(CustomerData.Conversion_Date <= end_date)
    
    customers = query.all()
    
    if not customers:
        return RevenueMetrics(
            total_revenue=0,
            monthly_recurring_revenue=0,
            annual_recurring_revenue=0,
            average_deal_size=0,
            customer_acquisition_cost=0,
            customer_lifetime_value=0,
            payback_period_months=0,
            churn_rate=0,
            expansion_revenue=0
        )
    
    total_revenue = sum([c.ACV_USD or 0 for c in customers])
    expansion_revenue = sum([c.ACV_USD or 0 for c in customers if c.Expansion_Flag])
    
    # Calculate other metrics
    avg_deal_size = total_revenue / len(customers) if customers else 0
    avg_cac = sum([c.CAC_USD or 0 for c in customers]) / len(customers) if customers else 0
    avg_clv = sum([c.LTV_USD or 0 for c in customers]) / len(customers) if customers else 0
    
    # Calculate churn rate
    total_customer_count = db.query(CustomerData).filter(CustomerData.Customer_Flag == True).count()
    churned_count = db.query(CustomerData).filter(CustomerData.Churn_Flag == True).count()
    churn_rate = (churned_count / total_customer_count * 100) if total_customer_count > 0 else 0
    
    # Payback period
    payback_period = (avg_cac / (avg_deal_size / 12)) if avg_deal_size > 0 else 0
    
    return RevenueMetrics(
        total_revenue=total_revenue,
        monthly_recurring_revenue=total_revenue / 12,  # Simplified
        annual_recurring_revenue=total_revenue,
        average_deal_size=avg_deal_size,
        customer_acquisition_cost=avg_cac,
        customer_lifetime_value=avg_clv,
        payback_period_months=payback_period,
        churn_rate=churn_rate,
        expansion_revenue=expansion_revenue
    )

def get_customer_journey(db: Session, customer_id: int):
    """Get complete customer journey"""
    customer = get_customer(db, customer_id)
    if not customer:
        return None
    
    stages = []
    current_stage = "Lead"
    
    # Build journey stages
    if customer.Lead_Creation_Date:
        stages.append({
            "stage": "Lead",
            "date": customer.Lead_Creation_Date.isoformat() if customer.Lead_Creation_Date else None,
            "score": customer.Lead_Score,
            "source": customer.Lead_Source
        })
    
    if customer.MQL_Flag and customer.MQL_Date:
        stages.append({
            "stage": "MQL",
            "date": customer.MQL_Date.isoformat(),
            "duration_from_lead": (customer.MQL_Date - customer.Lead_Creation_Date).days if customer.Lead_Creation_Date else 0
        })
        current_stage = "MQL"
    
    if customer.SQL_Flag and customer.SQL_Date:
        stages.append({
            "stage": "SQL",
            "date": customer.SQL_Date.isoformat(),
            "duration_from_mql": (customer.SQL_Date - customer.MQL_Date).days if customer.MQL_Date else 0
        })
        current_stage = "SQL"
    
    if customer.Customer_Flag and customer.Conversion_Date:
        stages.append({
            "stage": "Customer",
            "date": customer.Conversion_Date.isoformat(),
            "acv": customer.ACV_USD,
            "sales_cycle_days": customer.Sales_Cycle_Days
        })
        current_stage = "Customer"
    
    if customer.Churn_Flag:
        current_stage = "Churned"
        if customer.Churn_Date:
            stages.append({
                "stage": "Churned",
                "date": customer.Churn_Date.isoformat(),
                "tenure_months": customer.Customer_Tenure_Months
            })
    
    total_days = 0
    if customer.Lead_Creation_Date and customer.Conversion_Date:
        total_days = (customer.Conversion_Date - customer.Lead_Creation_Date).days
    
    return {
        "customer_id": customer_id,
        "stages": stages,
        "total_journey_days": total_days,
        "current_stage": current_stage,
        "key_milestones": [
            {"type": "First Contact", "date": customer.Lead_Creation_Date.isoformat() if customer.Lead_Creation_Date else None},
            {"type": "Became Customer", "date": customer.Conversion_Date.isoformat() if customer.Conversion_Date else None}
        ],
        "engagement_score": min((customer.NPS_Score or 0) + (customer.Logins_Per_Month or 0) * 2, 100)
    }

def get_pipeline_health(db: Session):
    """Get sales pipeline health metrics"""
    # Current pipeline value
    pipeline_value = db.query(func.sum(CustomerData.Forecasted_Revenue)).filter(
        CustomerData.Customer_Flag == False,
        CustomerData.Churn_Flag == False
    ).scalar() or 0
    
    # Pipeline by stage
    leads_value = db.query(func.sum(CustomerData.Forecasted_Revenue)).filter(
        CustomerData.MQL_Flag == False,
        CustomerData.Customer_Flag == False
    ).scalar() or 0
    
    mql_value = db.query(func.sum(CustomerData.Forecasted_Revenue)).filter(
        CustomerData.MQL_Flag == True,
        CustomerData.SQL_Flag == False
    ).scalar() or 0
    
    sql_value = db.query(func.sum(CustomerData.Forecasted_Revenue)).filter(
        CustomerData.SQL_Flag == True,
        CustomerData.Customer_Flag == False
    ).scalar() or 0
    
    return {
        "total_pipeline_value": pipeline_value,
        "pipeline_by_stage": {
            "leads": leads_value,
            "mqls": mql_value,
            "sqls": sql_value
        },
        "weighted_pipeline": pipeline_value * 0.3,  # Simplified weighting
        "pipeline_velocity": 45,  # Average days in pipeline
        "win_rate": 0.25  # 25% win rate
    }

def get_pipeline_forecast(db: Session):
    """Get pipeline forecast and expected closures"""
    # Get opportunities expected to close in next 90 days
    future_date = datetime.utcnow() + timedelta(days=90)
    
    upcoming_closes = db.query(CustomerData).filter(
        CustomerData.Expected_Close_Date <= future_date,
        CustomerData.Customer_Flag == False,
        CustomerData.Churn_Flag == False
    ).all()
    
    forecast_data = []
    for customer in upcoming_closes:
        if customer.Expected_Close_Date and customer.Forecasted_Revenue:
            forecast_data.append({
                "customer_id": customer.id,
                "customer_name": f"{customer.first_name} {customer.last_name}",
                "expected_close_date": customer.Expected_Close_Date.isoformat(),
                "forecasted_revenue": customer.Forecasted_Revenue,
                "probability": customer.Stage_Probability or 50,
                "weighted_revenue": (customer.Forecasted_Revenue * (customer.Stage_Probability or 50) / 100)
            })
    
    total_forecast = sum([f["weighted_revenue"] for f in forecast_data])
    
    return {
        "forecast_period": "Next 90 days",
        "total_weighted_forecast": total_forecast,
        "opportunity_count": len(forecast_data),
        "opportunities": forecast_data
    }

def log_customer_activity(db: Session, customer_id: int, activity_type: str, activity_data: dict):
    """Log customer activity for real-time tracking"""
    activity = CustomerActivity(
        customer_id=str(customer_id),
        activity_type=activity_type,
        activity_data=json.dumps(activity_data),
        timestamp=datetime.utcnow()
    )
    
    db.add(activity)
    db.commit()
    return True

def update_churn_prediction(db: Session, customer_id: int, prediction):
    """Update churn prediction for a customer"""
    churn_pred = ChurnPredictions(
        customer_id=str(customer_id),
        churn_probability=prediction.churn_probability,
        risk_factors=json.dumps(prediction.risk_factors),
        prediction_date=datetime.utcnow(),
        model_version="1.0"
    )
    
    db.add(churn_pred)
    db.commit()
    return True

def import_csv_data(db: Session, file_path: str):
    """Import customer data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        
        # Convert date columns
        date_columns = [
            'Lead_Creation_Date', 'MQL_Date', 'SQL_Date', 
            'Conversion_Date', 'Churn_Date', 'Expected_Close_Date'
        ]
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Insert data
        imported_count = 0
        for _, row in df.iterrows():
            # Check if customer already exists
            existing = db.query(CustomerData).filter(
                CustomerData.email == row['email']
            ).first()
            
            if not existing:
                customer = CustomerData(**row.to_dict())
                db.add(customer)
                imported_count += 1
        
        db.commit()
        return {
            "message": f"Successfully imported {imported_count} customers",
            "total_processed": len(df)
        }
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Import failed: {str(e)}")

def export_data(db: Session, format: str):
    """Export customer data and analytics"""
    customers = db.query(CustomerData).all()
    
    if format == "csv":
        # Convert to DataFrame and return CSV
        data = []
        for customer in customers:
            customer_dict = {
                "id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "email": customer.email,
                "stage": "Customer" if customer.Customer_Flag else "Lead",
                "revenue": customer.ACV_USD,
                "churn_risk": "Yes" if customer.Churn_Flag else "No"
            }
            data.append(customer_dict)
        
        return {"data": data, "format": "csv"}
    
    elif format == "json":
        return {
            "customers": [
                {
                    "id": c.id,
                    "name": f"{c.first_name} {c.last_name}",
                    "email": c.email,
                    "customer_flag": c.Customer_Flag,
                    "revenue": c.ACV_USD
                } for c in customers
            ],
            "export_date": datetime.utcnow().isoformat()
        }

def get_high_risk_customers(db: Session, risk_threshold: float = 0.7):
    """Get customers with high churn risk based on various factors"""
    # For now, we'll use simple heuristics since we don't have a trained ML model
    # In a real implementation, you'd use a proper churn prediction model
    
    # Get customers who are active but showing risk signals
    risky_customers = db.query(CustomerData).filter(
        CustomerData.Customer_Flag == True,
        CustomerData.Churn_Flag == False
    ).all()
    
    high_risk_list = []
    for customer in risky_customers:
        risk_score = 0.0
        risk_factors = []
        
        # Low ACV customers are at higher risk
        if customer.ACV_USD and customer.ACV_USD < 1000:
            risk_score += 0.3
            risk_factors.append("Low ACV")
        
        # Old customers without recent activity
        if customer.MQL_Date:
            days_since_mql = (datetime.utcnow() - customer.MQL_Date).days
            if days_since_mql > 365:
                risk_score += 0.4
                risk_factors.append("Long time since MQL")
        
        # Missing important fields indicate lack of engagement
        missing_fields = 0
        if not customer.Industry:
            missing_fields += 1
        if not customer.Decision_Maker_Role:
            missing_fields += 1
        if not customer.Region:
            missing_fields += 1
            
        if missing_fields > 1:
            risk_score += 0.3
            risk_factors.append("Incomplete profile")
        
        if risk_score >= risk_threshold:
            high_risk_list.append({
                "id": customer.id,
                "name": f"{customer.first_name or ''} {customer.last_name or ''}".strip(),
                "email": customer.email,
                "company": customer.Industry,
                "risk_score": round(risk_score, 2),
                "risk_factors": risk_factors,
                "acv": customer.ACV_USD,
                "customer_since": customer.Conversion_Date.isoformat() if customer.Conversion_Date else None
            })
    
    # Sort by risk score descending
    high_risk_list.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return high_risk_list