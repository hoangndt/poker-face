from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uvicorn
import json

from database import get_db, engine
from models import CustomerData, LifecycleStage, CustomerActivity, ChurnPredictions, RevenueForecastData
from schemas import (
    CustomerResponse, 
    LifecycleAnalytics,
    RevenueMetrics,
    RevenueForecast, 
    ChurnPrediction,
    LeadScoreUpdate,
    CustomerJourney
)
from ai_models import (
    ChurnPredictor, 
    RevenueForecaster, 
    LeadScorer, 
    CLVCalculator
)
from vietnam_models import (
    GradionLeadScorer,
    VietnamChurnPredictor,
    ExpansionRevenuePredictor,
    RegionAssignmentEngine
)
import crud

app = FastAPI(
    title="Customer Lifecycle AI API",
    description="AI-powered Customer Lifecycle Management and Revenue Forecasting",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models
churn_predictor = ChurnPredictor()
revenue_forecaster = RevenueForecaster()
lead_scorer = LeadScorer()
clv_calculator = CLVCalculator()

# Initialize Vietnam-specific models
gradion_scorer = GradionLeadScorer()
vietnam_churn_predictor = VietnamChurnPredictor()
expansion_predictor = ExpansionRevenuePredictor()
region_assigner = RegionAssignmentEngine()

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ========================
# CUSTOMER ENDPOINTS
# ========================

@app.get("/api/customers", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0, 
    limit: int = 100, 
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get customers with optional filtering"""
    customers = crud.get_customers(db, skip=skip, limit=limit, stage=stage)
    return customers

@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/api/customers/{customer_id}/journey", response_model=CustomerJourney)
async def get_customer_journey(customer_id: str, db: Session = Depends(get_db)):
    """Get customer journey and stage progression"""
    journey = crud.get_customer_journey(db, customer_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Customer journey not found")
    return journey

@app.put("/api/customers/{customer_id}/stage")
async def update_customer_stage(
    customer_id: int, 
    stage_data: dict,
    db: Session = Depends(get_db)
):
    """Update customer lifecycle stage"""
    updated_customer = crud.update_customer_stage(db, customer_id, stage_data)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer stage updated successfully"}

# ========================
# ANALYTICS ENDPOINTS
# ========================

@app.get("/api/analytics/lifecycle", response_model=LifecycleAnalytics)
async def get_lifecycle_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get lifecycle conversion analytics"""
    analytics = crud.get_lifecycle_analytics(db)
    return analytics

@app.get("/api/analytics/conversion-rates")
async def get_conversion_rates(db: Session = Depends(get_db)):
    """Get detailed conversion rates by stage"""
    rates = crud.get_conversion_rates(db)
    return rates

@app.get("/api/analytics/revenue-metrics", response_model=RevenueMetrics)
async def get_revenue_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get revenue metrics and KPIs"""
    metrics = crud.get_revenue_metrics(db, start_date, end_date)
    return metrics

# ========================
# AI/ML ENDPOINTS
# ========================

@app.get("/api/ai/churn-prediction/{customer_id}")
async def get_churn_prediction(customer_id: int, db: Session = Depends(get_db)):
    """Get churn prediction for a specific customer"""
    try:
        # Get customer data
        customer = db.query(CustomerData).filter(CustomerData.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get prediction
        prediction = churn_predictor.predict(customer)
        
        # Store prediction in database
        db_prediction = ChurnPredictions(
            customer_id=str(customer.id),
            churn_probability=prediction.churn_probability,
            risk_factors=json.dumps(prediction.risk_factors),
            model_version="v1.0"
        )
        db.add(db_prediction)
        db.commit()
        
        return {
            "customer_id": customer.id,
            "churn_probability": prediction.churn_probability,
            "risk_level": prediction.risk_level,
            "risk_factors": prediction.risk_factors,
            "recommendations": prediction.recommendations,
            "prediction_confidence": prediction.prediction_confidence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting churn: {str(e)}")

@app.post("/api/ai/train-models")
async def train_ai_models(db: Session = Depends(get_db)):
    """Train all AI models with current customer data"""
    try:
        # Get all customers for training
        customers = db.query(CustomerData).all()
        
        if len(customers) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Need at least 10 customers to train the model"
            )
        
        # Check if we have both churned and non-churned customers
        churned_customers = [c for c in customers if c.Churn_Flag]
        active_customers = [c for c in customers if not c.Churn_Flag]
        
        if len(churned_customers) == 0 or len(active_customers) == 0:
            raise HTTPException(
                status_code=400,
                detail="Need both churned and active customers to train the model"
            )
        
        # Train churn prediction model
        churn_predictor.train(customers)
        
        # Train revenue forecasting model (if available)
        try:
            revenue_forecaster.train(customers)
        except Exception as e:
            print(f"Warning: Could not train revenue forecaster: {e}")
        
        # Train lead scoring model (if available)
        try:
            lead_scorer.train(customers)
        except Exception as e:
            print(f"Warning: Could not train lead scorer: {e}")
        
        return {
            "message": "Models trained successfully",
            "total_customers": len(customers),
            "churned_customers": len(churned_customers),
            "active_customers": len(active_customers),
            "models_trained": ["churn_predictor"],
            "training_timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")

@app.get("/api/ai/model-status")
async def get_model_status(db: Session = Depends(get_db)):
    """Get the training status of AI models"""
    try:
        # Count customers
        total_customers = db.query(CustomerData).count()
        churned_customers = db.query(CustomerData).filter(CustomerData.Churn_Flag == True).count()
        active_customers = db.query(CustomerData).filter(CustomerData.Churn_Flag == False).count()
        
        return {
            "churn_predictor": {
                "is_trained": churn_predictor.is_trained,
                "feature_importance": churn_predictor.feature_importance if churn_predictor.is_trained else {}
            },
            "data_summary": {
                "total_customers": total_customers,
                "churned_customers": churned_customers,
                "active_customers": active_customers,
                "can_train": total_customers >= 10 and churned_customers > 0 and active_customers > 0
            },
            "recommendations": [
                "Use POST /api/ai/train-models to train the models" if not churn_predictor.is_trained else "Models are trained and ready",
                f"Current data: {total_customers} total customers ({churned_customers} churned, {active_customers} active)",
                "Need at least 10 customers with both churned and active examples to train"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")

@app.post("/api/ai/create-sample-data")
async def create_sample_data(db: Session = Depends(get_db)):
    """Create sample customer data for training (development only)"""
    try:
        # Check if we already have enough data
        existing_count = db.query(CustomerData).count()
        if existing_count >= 50:
            return {
                "message": "Already have sufficient data",
                "existing_customers": existing_count
            }
        
        # Create sample customers with some churned examples
        sample_customers = []
        
        for i in range(20):
            # Create some regular customers
            customer = CustomerData(
                first_name=f"Customer{i}",
                last_name=f"Test{i}",
                email=f"customer{i}@example.com",
                Customer_ID=f"CUST{i:03d}",
                Customer_Flag=True,
                Customer_Tenure_Months=np.random.randint(1, 48),
                NPS_Score=np.random.randint(1, 10),
                Tickets_Raised=np.random.randint(0, 20),
                Product_Usage_Hours=np.random.uniform(1, 100),
                ACV_USD=np.random.uniform(500, 50000),
                Company_Size=np.random.randint(10, 1000),
                Industry=np.random.choice(["Technology", "Finance", "Healthcare", "Manufacturing"]),
                Region=np.random.choice(["North America", "Europe", "Asia", "Australia"]),
                # Some customers are churned (20% chance)
                Churn_Flag=np.random.random() < 0.2,
                Conversion_Date=datetime.utcnow() - timedelta(days=np.random.randint(30, 1000))
            )
            sample_customers.append(customer)
        
        # Add to database
        db.add_all(sample_customers)
        db.commit()
        
        return {
            "message": f"Created {len(sample_customers)} sample customers",
            "total_customers": existing_count + len(sample_customers),
            "next_step": "Use POST /api/ai/train-models to train the AI models"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sample data: {str(e)}")

@app.get("/api/ai/churn-risk-customers")
async def get_churn_risk_customers(
    risk_threshold: float = 0.7,
    db: Session = Depends(get_db)
):
    """Get customers with high churn risk"""
    try:
        customers = crud.get_high_risk_customers(db, risk_threshold)
        return {"high_risk_customers": customers, "threshold": risk_threshold}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting risk customers: {str(e)}")

@app.get("/api/ai/revenue-forecast", response_model=RevenueForecast)
async def get_revenue_forecast(
    months_ahead: int = 12,
    db: Session = Depends(get_db)
):
    """Get revenue forecast for specified months ahead"""
    try:
        # Get historical data
        historical_data = crud.get_historical_revenue(db)
        
        # Generate forecast
        forecast = revenue_forecaster.forecast_revenue(historical_data, months_ahead)
        
        return forecast
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forecasting revenue: {str(e)}")

@app.get("/api/ai/clv/{customer_id}")
async def get_customer_clv(customer_id: int, db: Session = Depends(get_db)):
    """Calculate Customer Lifetime Value"""
    try:
        # Get customer data
        customer = db.query(CustomerData).filter(CustomerData.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Prepare data for CLV calculation
        customer_data = {
            'monthly_revenue': (customer.ACV_USD or 0) / 12,
            'tenure_months': customer.Customer_Tenure_Months or 1,
            'churn_probability': 0.1,  # Default low churn
            'expansion_probability': 0.2
        }
        
        clv_result = clv_calculator.calculate_clv(customer_data)
        return clv_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CLV: {str(e)}")

@app.post("/api/ai/lead-score", response_model=LeadScoreUpdate)
async def calculate_lead_score(lead_data: dict):
    """Calculate lead score for new leads"""
    try:
        score_result = lead_scorer.score_lead(lead_data)
        return score_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating lead score: {str(e)}")

# ========================
# PIPELINE ENDPOINTS
# ========================

@app.get("/api/pipeline/health")
async def get_pipeline_health(db: Session = Depends(get_db)):
    """Get pipeline health metrics"""
    health = crud.get_pipeline_health(db)
    return health

@app.get("/api/pipeline/forecast")
async def get_pipeline_forecast(db: Session = Depends(get_db)):
    """Get pipeline forecast and opportunities"""
    forecast = crud.get_pipeline_forecast(db)
    return forecast

# ========================
# VIETNAM-SPECIFIC ENDPOINTS
# ========================

@app.post("/api/vietnam/gradion-lead-score")
async def calculate_gradion_lead_score(lead_data: dict):
    """
    Calculate lead score using Gradion's specific criteria:
    - ≤109 → MQL, ≥110 → SQL
    - Book Consultant = TRUE → SQL override
    """
    try:
        result = gradion_scorer.calculate_vietnam_lead_score(lead_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating lead score: {str(e)}")

@app.get("/api/vietnam/churn-prediction/{customer_id}")
async def get_vietnam_churn_prediction(
    customer_id: str, 
    db: Session = Depends(get_db)
):
    """Enhanced churn prediction with Vietnamese Customer Success focus"""
    try:
        # Get customer data
        customer = db.query(CustomerData).filter(CustomerData.Customer_ID == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Prepare data for Vietnam model
        customer_data = {
            'nps_score': customer.NPS_Score or 5,
            'support_tickets': customer.Tickets_Raised or 0,
            'product_usage_hours': customer.Product_Usage_Hours or 0,
            'renewal_months_remaining': 6,  # Calculate from contract data
            'expansion_flag': customer.Expansion_Flag or False,
            'cs_touch_frequency': 4  # Default quarterly touches
        }
        
        # Get Vietnam-specific prediction
        result = vietnam_churn_predictor.predict_churn_risk(customer_data)
        
        # Store prediction in database
        prediction = ChurnPredictions(
            customer_id=customer_id,
            churn_probability=result['churn_probability'],
            risk_factors=json.dumps(result['risk_factors']),
            model_version="vietnam_v1.0"
        )
        db.add(prediction)
        db.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting churn: {str(e)}")

@app.get("/api/vietnam/data-quality-report")
async def get_data_quality_report(db: Session = Depends(get_db)):
    """
    Generate data quality report focusing on MQL/SQL conversion tracking issues
    mentioned in the Vietnamese workflow
    """
    try:
        # Check for data inconsistencies
        customers = db.query(CustomerData).all()
        
        issues = []
        inconsistent_count = 0
        
        for customer in customers:
            customer_issues = []
            
            # Check MQL flag without MQL date
            if customer.MQL_Flag and not customer.MQL_Date:
                customer_issues.append("MQL flag set but no MQL date")
            
            # Check SQL flag without SQL date
            if customer.SQL_Flag and not customer.SQL_Date:
                customer_issues.append("SQL flag set but no SQL date")
            
            # Check Customer flag without conversion date
            if customer.Customer_Flag and not customer.Conversion_Date:
                customer_issues.append("Customer flag set but no conversion date")
            
            # Check lead score vs MQL/SQL flags consistency
            if customer.Lead_Score:
                if customer.Lead_Score >= 110 and not customer.SQL_Flag:
                    customer_issues.append("Lead score ≥110 but not marked as SQL")
                elif customer.Lead_Score <= 109 and customer.Lead_Score > 0 and not customer.MQL_Flag:
                    customer_issues.append("Lead score ≤109 but not marked as MQL")
            
            if customer_issues:
                inconsistent_count += 1
                issues.append({
                    'customer_id': customer.Customer_ID or f"ID_{customer.id}",
                    'email': customer.email,
                    'issues': customer_issues
                })
        
        # Calculate data quality metrics
        total_customers = len(customers)
        data_quality_score = (total_customers - inconsistent_count) / total_customers * 100 if total_customers > 0 else 0
        
        return {
            'total_customers': total_customers,
            'inconsistent_records': inconsistent_count,
            'data_quality_score': round(data_quality_score, 2),
            'issues': issues[:10],  # Return first 10 issues
            'recommendations': [
                "Implement automated lead scoring validation in HubSpot",
                "Add required date fields when lifecycle stage flags are set",
                "Create weekly data quality monitoring dashboard",
                "Set up alerts for score/stage mismatches"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data quality report: {str(e)}")

@app.get("/api/vietnam/cs-intervention-queue")
async def get_cs_intervention_queue(db: Session = Depends(get_db)):
    """
    Generate Customer Success intervention queue for Vietnamese market
    Based on NPS scores, engagement levels, and cultural factors
    """
    try:
        # Get all active customers (not churned)
        customers = db.query(CustomerData).filter(
            CustomerData.Churn_Flag == False
        ).all()
        
        intervention_list = []
        risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for customer in customers:
            risk_score = 0
            risk_factors = []
            next_action = "Monitor"
            risk_level = "low"
            
            # Vietnamese-specific risk factors
            # 1. Low engagement (missing profile info)
            if not customer.Industry or not customer.Decision_Maker_Role:
                risk_score += 25
                risk_factors.append("Incomplete profile")
            
            # 2. Low ACV indicates potential churn risk (for customers)
            if customer.Customer_Flag and customer.ACV_USD and customer.ACV_USD < 2000:
                risk_score += 30
                risk_factors.append("Low contract value")
                
            # 3. Long time without MQL progression
            if customer.MQL_Date:
                days_since_mql = (datetime.utcnow() - customer.MQL_Date).days
                if days_since_mql > 180:
                    risk_score += 20
                    risk_factors.append("Stale MQL")
            
            # 4. SQL not converting to customer
            if customer.SQL_Flag and not customer.Customer_Flag:
                if customer.SQL_Date:
                    days_since_sql = (datetime.utcnow() - customer.SQL_Date).days
                    if days_since_sql > 90:
                        risk_score += 25
                        risk_factors.append("SQL not converting")
                else:
                    risk_score += 15
                    risk_factors.append("SQL without date")
            
            # 5. Long-time customer without recent engagement
            if customer.Customer_Flag and customer.Conversion_Date:
                days_as_customer = (datetime.utcnow() - customer.Conversion_Date).days
                if days_as_customer > 365 and not customer.SQL_Date:
                    risk_score += 20
                    risk_factors.append("Long-time customer, low engagement")
            
            # Determine risk level and next action
            if risk_score >= 75:
                risk_level = "critical"
                next_action = "Immediate escalation to CS manager"
            elif risk_score >= 50:
                risk_level = "high"
                next_action = "Schedule relationship-building call"
            elif risk_score >= 25:
                risk_level = "medium"
                next_action = "Send cultural engagement content"
            else:
                risk_level = "low"
                next_action = "Continue standard nurturing"
            
            risk_levels[risk_level] += 1
            
            if risk_score >= 25:  # Only include medium+ risk customers
                intervention_list.append({
                    'name': f"{customer.first_name or ''} {customer.last_name or ''}".strip(),
                    'email': customer.email,
                    'company': customer.Industry,  # Using Industry as company info
                    'risk_level': risk_level,
                    'score': risk_score,
                    'risk_factors': risk_factors,
                    'next_action': next_action,
                    'acv': customer.ACV_USD,
                    'days_as_customer': (datetime.utcnow() - customer.Conversion_Date).days if customer.Conversion_Date else None,
                    'is_customer': customer.Customer_Flag
                })
        
        # Sort by risk score descending
        intervention_list.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'total_at_risk': len(intervention_list),
            'by_risk_level': risk_levels,
            'customers': intervention_list,
            'cultural_recommendations': [
                "Schedule face-to-face meetings when possible",
                "Provide Vietnamese language support materials",
                "Respect relationship-building timeline expectations",
                "Offer family/company event invitations"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CS intervention queue: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)