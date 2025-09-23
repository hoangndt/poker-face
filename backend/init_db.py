import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from datetime import datetime
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import create_engine, SessionLocal
from models import Base, CustomerData

def create_database():
    """Create database tables"""
    engine = create_engine("sqlite:///./customer_lifecycle.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def load_csv_data(csv_file_path: str):
    """Load CSV data into the database"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from CSV")
        
        # Convert date columns
        date_columns = [
            'Lead_Creation_Date', 'MQL_Date', 'SQL_Date', 
            'Conversion_Date', 'Churn_Date', 'Expected_Close_Date'
        ]
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean and prepare data
        df = df.fillna({
            'Lead_Score': 0,
            'ACV_USD': 0,
            'LTV_USD': 0,
            'CAC_USD': 0,
            'Sales_Cycle_Days': 0,
            'Customer_Tenure_Months': 0,
            'Renewals_Count': 0,
            'Logins_Per_Month': 0,
            'Active_Features_Used': 0,
            'Product_Usage_Hours': 0,
            'Tickets_Raised': 0,
            'Avg_Response_Time_Support': 0,
            'NPS_Score': 0,
            'Stage_Probability': 0,
            'Forecasted_Revenue': 0,
            'Company_Size': 0
        })
        
        # Create database session
        db = SessionLocal()
        
        # Insert data
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                # Check if customer already exists
                existing = db.query(CustomerData).filter(
                    CustomerData.email == row['email']
                ).first()
                
                if not existing:
                    customer = CustomerData(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        gender=row.get('gender'),
                        ip_address=row.get('ip_address'),
                        Lead_ID=str(row.get('Lead_ID', '')),
                        Lead_Source=row.get('Lead_Source'),
                        Lead_Creation_Date=row.get('Lead_Creation_Date') if pd.notna(row.get('Lead_Creation_Date')) else None,
                        Lead_Score=float(row.get('Lead_Score', 0)),
                        MQL_Flag=bool(row.get('MQL_Flag')),
                        MQL_Date=row.get('MQL_Date') if pd.notna(row.get('MQL_Date')) else None,
                        SQL_Flag=bool(row.get('SQL_Flag')),
                        SQL_Date=row.get('SQL_Date') if pd.notna(row.get('SQL_Date')) else None,
                        Customer_Flag=bool(row.get('Customer_Flag')),
                        Conversion_Date=row.get('Conversion_Date') if pd.notna(row.get('Conversion_Date')) else None,
                        Customer_ID=str(row.get('Customer_ID', '')),
                        Industry=row.get('Industry'),
                        Company_Size=int(row.get('Company_Size', 0)),
                        Region=row.get('Region'),
                        Decision_Maker_Role=row.get('Decision_Maker_Role'),
                        ACV_USD=float(row.get('ACV_USD', 0)),
                        Sales_Cycle_Days=int(row.get('Sales_Cycle_Days', 0)),
                        CAC_USD=float(row.get('CAC_USD', 0)),
                        LTV_USD=float(row.get('LTV_USD', 0)),
                        Churn_Flag=bool(row.get('Churn_Flag')),
                        Churn_Date=row.get('Churn_Date') if pd.notna(row.get('Churn_Date')) else None,
                        Customer_Tenure_Months=int(row.get('Customer_Tenure_Months', 0)),
                        Renewals_Count=int(row.get('Renewals_Count', 0)),
                        Expansion_Flag=bool(row.get('Expansion_Flag')),
                        Logins_Per_Month=int(row.get('Logins_Per_Month', 0)),
                        Active_Features_Used=int(row.get('Active_Features_Used', 0)),
                        Product_Usage_Hours=float(row.get('Product_Usage_Hours', 0)),
                        Tickets_Raised=int(row.get('Tickets_Raised', 0)),
                        Avg_Response_Time_Support=float(row.get('Avg_Response_Time_Support', 0)),
                        NPS_Score=float(row.get('NPS_Score', 0)),
                        Stage_Probability=float(row.get('Stage_Probability', 0)),
                        Expected_Close_Date=row.get('Expected_Close_Date') if pd.notna(row.get('Expected_Close_Date')) else None,
                        Forecasted_Revenue=float(row.get('Forecasted_Revenue', 0))
                    )
                    
                    db.add(customer)
                    inserted_count += 1
                    
                    if inserted_count % 100 == 0:
                        print(f"Inserted {inserted_count} customers...")
                        
            except Exception as e:
                print(f"Error inserting row {row.get('id', 'unknown')}: {str(e)}")
                continue
        
        db.commit()
        db.close()
        
        print(f"Successfully inserted {inserted_count} customers into database")
        return inserted_count
        
    except Exception as e:
        print(f"Error loading CSV data: {str(e)}")
        return 0

def verify_data():
    """Verify the loaded data"""
    db = SessionLocal()
    
    total_customers = db.query(CustomerData).count()
    total_leads = db.query(CustomerData).filter(CustomerData.Customer_Flag == False).count()
    total_converted = db.query(CustomerData).filter(CustomerData.Customer_Flag == True).count()
    total_churned = db.query(CustomerData).filter(CustomerData.Churn_Flag == True).count()
    
    print("\n=== Database Verification ===")
    print(f"Total records: {total_customers}")
    print(f"Leads: {total_leads}")
    print(f"Customers: {total_converted}")
    print(f"Churned: {total_churned}")
    
    # Show some sample data
    sample_customers = db.query(CustomerData).limit(5).all()
    print("\n=== Sample Data ===")
    for customer in sample_customers:
        print(f"ID: {customer.id}, Name: {customer.first_name} {customer.last_name}, "
              f"Stage: {'Customer' if customer.Customer_Flag else 'Lead'}, "
              f"Revenue: ${customer.ACV_USD or 0}")
    
    db.close()

if __name__ == "__main__":
    # Create database
    create_database()
    
    # Load CSV data
    csv_path = "/Users/hoangtuan/Desktop/Projects/NFQ/poker-face/datasets/raw-data.csv"
    if os.path.exists(csv_path):
        load_csv_data(csv_path)
        verify_data()
    else:
        print(f"CSV file not found at {csv_path}")
        print("Please ensure the CSV file exists at the specified path")