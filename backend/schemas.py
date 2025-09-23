from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    Customer_ID: Optional[str]
    Industry: Optional[str]
    Region: Optional[str]
    Lead_Score: Optional[float]
    MQL_Flag: bool
    SQL_Flag: bool
    Customer_Flag: bool
    Churn_Flag: bool
    ACV_USD: Optional[float]
    LTV_USD: Optional[float]
    NPS_Score: Optional[float]
    Stage_Probability: Optional[float]
    Forecasted_Revenue: Optional[float]
    
    class Config:
        from_attributes = True

class LifecycleAnalytics(BaseModel):
    total_leads: int
    total_mqls: int
    total_sqls: int
    total_customers: int
    churned_customers: int
    lead_to_mql_rate: float
    mql_to_sql_rate: float
    sql_to_customer_rate: float
    overall_conversion_rate: float
    average_sales_cycle_days: float
    total_revenue: float
    average_clv: float

class RevenueForecast(BaseModel):
    forecast_period: str
    predicted_revenue: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    monthly_forecast: List[Dict[str, Any]]
    growth_rate: float
    seasonality_factors: Dict[str, float]

class ChurnPrediction(BaseModel):
    customer_id: str
    churn_probability: float
    risk_level: str  # Low, Medium, High
    risk_factors: List[str]
    recommendations: List[str]
    prediction_confidence: float

class LeadScoreUpdate(BaseModel):
    Lead_ID: str
    Industry: Optional[str]
    Company_Size: Optional[int]
    Region: Optional[str]
    Lead_Source: Optional[str]
    Decision_Maker_Role: Optional[str]
    recent_activities: Optional[List[Dict[str, Any]]]

class CustomerJourney(BaseModel):
    customer_id: str
    stages: List[Dict[str, Any]]
    total_journey_days: int
    current_stage: str
    key_milestones: List[Dict[str, Any]]
    engagement_score: float

class RevenueMetrics(BaseModel):
    total_revenue: float
    monthly_recurring_revenue: float
    annual_recurring_revenue: float
    average_deal_size: float
    customer_acquisition_cost: float
    customer_lifetime_value: float
    payback_period_months: float
    churn_rate: float
    expansion_revenue: float