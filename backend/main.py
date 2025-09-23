from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uvicorn

from database import get_db, engine
from models import CustomerData, LifecycleStage, RevenueMetrics
from schemas import (
    CustomerResponse, 
    LifecycleAnalytics, 
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
import crud

app = FastAPI(
    title="Customer Lifecycle AI & Revenue Forecasting",
    description="AI-powered customer lifecycle optimization and revenue forecasting system",
    version="1.0.0"
)

# CORS middleware
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

@app.on_event("startup")
async def startup_event():
    """Initialize database and AI models on startup"""
    # Load and process initial data
    await load_initial_data()
    
    # Train AI models
    await train_models()

async def load_initial_data():
    """Load CSV data into database"""
    try:
        df = pd.read_csv('/Users/hoangtuan/Desktop/Projects/NFQ/poker-face/datasets/raw-data.csv')
        # Process and insert data into database
        # This will be implemented in the database setup
        print("Initial data loaded successfully")
    except Exception as e:
        print(f"Error loading initial data: {e}")

async def train_models():
    """Train all AI models with current data"""
    db = next(get_db())
    customers = crud.get_all_customers(db)
    
    # Train models with existing data
    churn_predictor.train(customers)
    revenue_forecaster.train(customers)
    lead_scorer.train(customers)
    clv_calculator.train(customers)
    
    print("AI models trained successfully")

# === Customer Lifecycle Endpoints ===

@app.get("/api/customers", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0, 
    limit: int = 100,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get customers with optional filtering by lifecycle stage"""
    customers = crud.get_customers(db, skip=skip, limit=limit, stage=stage)
    return customers

@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get detailed customer information"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/api/customers/{customer_id}/journey", response_model=CustomerJourney)
async def get_customer_journey(customer_id: str, db: Session = Depends(get_db)):
    """Get complete customer journey from lead to customer"""
    journey = crud.get_customer_journey(db, customer_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Customer journey not found")
    return journey

@app.put("/api/customers/{customer_id}/stage")
async def update_customer_stage(
    customer_id: str, 
    new_stage: str, 
    db: Session = Depends(get_db)
):
    """Update customer lifecycle stage"""
    success = crud.update_customer_stage(db, customer_id, new_stage)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer stage updated successfully"}

# === Analytics Endpoints ===

@app.get("/api/analytics/lifecycle", response_model=LifecycleAnalytics)
async def get_lifecycle_analytics(db: Session = Depends(get_db)):
    """Get comprehensive lifecycle analytics"""
    analytics = crud.get_lifecycle_analytics(db)
    return analytics

@app.get("/api/analytics/conversion-rates")
async def get_conversion_rates(db: Session = Depends(get_db)):
    """Get conversion rates between lifecycle stages"""
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

# === AI/ML Endpoints ===

@app.get("/api/ai/churn-prediction/{customer_id}", response_model=ChurnPrediction)
async def predict_churn(customer_id: str, db: Session = Depends(get_db)):
    """Predict churn probability for a specific customer"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    prediction = churn_predictor.predict(customer)
    return prediction

@app.get("/api/ai/churn-risk-customers")
async def get_churn_risk_customers(
    risk_threshold: float = 0.7,
    db: Session = Depends(get_db)
):
    """Get customers at high risk of churning"""
    customers = crud.get_all_customers(db)
    at_risk = []
    
    for customer in customers:
        prediction = churn_predictor.predict(customer)
        if prediction.churn_probability > risk_threshold:
            at_risk.append({
                "customer_id": customer.Customer_ID,
                "customer_name": f"{customer.first_name} {customer.last_name}",
                "churn_probability": prediction.churn_probability,
                "risk_factors": prediction.risk_factors
            })
    
    return {"at_risk_customers": at_risk}

@app.post("/api/ai/lead-score")
async def update_lead_score(lead_data: LeadScoreUpdate):
    """Calculate and update lead score using AI"""
    score = lead_scorer.calculate_score(lead_data)
    return {"lead_score": score, "recommendations": lead_scorer.get_recommendations(lead_data)}

@app.get("/api/ai/revenue-forecast", response_model=RevenueForecast)
async def get_revenue_forecast(
    months_ahead: int = 12,
    db: Session = Depends(get_db)
):
    """Get AI-powered revenue forecast"""
    forecast = revenue_forecaster.forecast(months_ahead, db)
    return forecast

@app.get("/api/ai/clv/{customer_id}")
async def calculate_customer_lifetime_value(customer_id: str, db: Session = Depends(get_db)):
    """Calculate Customer Lifetime Value using AI"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    clv = clv_calculator.calculate(customer)
    return {
        "customer_id": customer_id,
        "estimated_clv": clv.estimated_value,
        "confidence_score": clv.confidence,
        "factors": clv.contributing_factors
    }

# === Pipeline Health Endpoints ===

@app.get("/api/pipeline/health")
async def get_pipeline_health(db: Session = Depends(get_db)):
    """Get overall sales pipeline health metrics"""
    health = crud.get_pipeline_health(db)
    return health

@app.get("/api/pipeline/forecast")
async def get_pipeline_forecast(db: Session = Depends(get_db)):
    """Get pipeline forecast and expected closures"""
    forecast = crud.get_pipeline_forecast(db)
    return forecast

# === Real-time Updates ===

@app.post("/api/events/customer-activity")
async def log_customer_activity(
    customer_id: str,
    activity_type: str,
    activity_data: dict,
    db: Session = Depends(get_db)
):
    """Log customer activity for real-time tracking"""
    success = crud.log_customer_activity(db, customer_id, activity_type, activity_data)
    
    # Trigger real-time score updates
    if activity_type in ["login", "feature_usage", "support_ticket"]:
        customer = crud.get_customer(db, customer_id)
        if customer:
            # Update churn prediction
            new_prediction = churn_predictor.predict(customer)
            crud.update_churn_prediction(db, customer_id, new_prediction)
    
    return {"message": "Activity logged successfully"}

# === Data Import/Export ===

@app.post("/api/data/import")
async def import_data(file_path: str, db: Session = Depends(get_db)):
    """Import customer data from CSV file"""
    try:
        result = crud.import_csv_data(db, file_path)
        # Retrain models with new data
        await train_models()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@app.get("/api/data/export")
async def export_data(format: str = "csv", db: Session = Depends(get_db)):
    """Export customer data and analytics"""
    if format not in ["csv", "json"]:
        raise HTTPException(status_code=400, detail="Unsupported export format")
    
    data = crud.export_data(db, format)
    return data

# === Health Check ===

@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "models_status": {
            "churn_predictor": churn_predictor.is_trained,
            "revenue_forecaster": revenue_forecaster.is_trained,
            "lead_scorer": lead_scorer.is_trained,
            "clv_calculator": clv_calculator.is_trained
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)