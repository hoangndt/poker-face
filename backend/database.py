from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./customer_lifecycle.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CustomerData(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    gender = Column(String)
    ip_address = Column(String)
    
    # Lead Information
    Lead_ID = Column(String, index=True)
    Lead_Source = Column(String, index=True)
    Lead_Creation_Date = Column(DateTime)
    Lead_Score = Column(Float)
    
    # Marketing Qualified Lead
    MQL_Flag = Column(Boolean, default=False)
    MQL_Date = Column(DateTime)
    
    # Sales Qualified Lead
    SQL_Flag = Column(Boolean, default=False)
    SQL_Date = Column(DateTime)
    
    # Customer
    Customer_Flag = Column(Boolean, default=False)
    Conversion_Date = Column(DateTime)
    Customer_ID = Column(String, index=True)
    
    # Company Information
    Industry = Column(String, index=True)
    Company_Size = Column(Integer)
    Region = Column(String, index=True)
    Decision_Maker_Role = Column(String)
    
    # Revenue Metrics
    ACV_USD = Column(Float)  # Annual Contract Value
    Sales_Cycle_Days = Column(Integer)
    CAC_USD = Column(Float)  # Customer Acquisition Cost
    LTV_USD = Column(Float)  # Lifetime Value
    
    # Churn Information
    Churn_Flag = Column(Boolean, default=False)
    Churn_Date = Column(DateTime)
    Customer_Tenure_Months = Column(Integer)
    Renewals_Count = Column(Integer)
    Expansion_Flag = Column(Boolean, default=False)
    
    # Product Usage
    Logins_Per_Month = Column(Integer)
    Active_Features_Used = Column(Integer)
    Product_Usage_Hours = Column(Float)
    
    # Customer Success
    Tickets_Raised = Column(Integer)
    Avg_Response_Time_Support = Column(Float)
    NPS_Score = Column(Float)
    
    # Forecasting
    Stage_Probability = Column(Float)
    Expected_Close_Date = Column(DateTime)
    Forecasted_Revenue = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LifecycleStage(Base):
    __tablename__ = "lifecycle_stages"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    stage = Column(String, index=True)  # Lead, MQL, SQL, Customer, Churned
    entered_date = Column(DateTime)
    exited_date = Column(DateTime)
    duration_days = Column(Integer)
    
class CustomerActivity(Base):
    __tablename__ = "customer_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    activity_type = Column(String, index=True)
    activity_data = Column(Text)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

class ChurnPredictions(Base):
    __tablename__ = "churn_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    churn_probability = Column(Float)
    risk_factors = Column(Text)  # JSON string
    prediction_date = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)

class RevenueForecast(Base):
    __tablename__ = "revenue_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    forecast_date = Column(DateTime)
    forecast_period = Column(String)  # monthly, quarterly
    predicted_revenue = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    actual_revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)