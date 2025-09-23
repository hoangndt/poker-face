"""
Script to create dummy data for the sprint board system.
This will populate the database with sample deals, persons, and conversation data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from sprint_models import (
    Base, Deal, Person, ConversationData, DealStatus, Priority, PersonRole
)
from models import CustomerData
import csv
from datetime import datetime, timedelta
import random

def create_dummy_persons(db: Session):
    """Create dummy team members"""
    persons_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice.johnson@company.com',
            'role': PersonRole.SALES,
            'department': 'Sales',
            'skills': '{"skills": ["B2B Sales", "Lead Qualification", "CRM Management"]}',
            'availability': 0.8,
            'hourly_rate': 150.0
        },
        {
            'name': 'Bob Chen',
            'email': 'bob.chen@company.com',
            'role': PersonRole.HEAD_OF_ENGINEERING,
            'department': 'Engineering',
            'skills': '{"skills": ["Python", "React", "System Architecture", "Database Design"]}',
            'availability': 0.9,
            'hourly_rate': 200.0
        },
        {
            'name': 'Carol Martinez',
            'email': 'carol.martinez@company.com',
            'role': PersonRole.HEAD_OF_DELIVERY,
            'department': 'Delivery',
            'skills': '{"skills": ["Project Management", "Resource Planning", "Cost Estimation"]}',
            'availability': 0.75,
            'hourly_rate': 180.0
        },
        {
            'name': 'David Wilson',
            'email': 'david.wilson@company.com',
            'role': PersonRole.CSO,
            'department': 'Executive',
            'skills': '{"skills": ["Strategic Planning", "Business Development", "Client Relations"]}',
            'availability': 0.6,
            'hourly_rate': 300.0
        },
        {
            'name': 'Eva Rodriguez',
            'email': 'eva.rodriguez@company.com',
            'role': PersonRole.PROJECT_MANAGER,
            'department': 'Delivery',
            'skills': '{"skills": ["Agile Management", "Team Coordination", "Quality Assurance"]}',
            'availability': 0.85,
            'hourly_rate': 160.0
        }
    ]
    
    created_persons = []
    for person_data in persons_data:
        # Check if person already exists
        existing = db.query(Person).filter(Person.email == person_data['email']).first()
        if not existing:
            person = Person(**person_data)
            db.add(person)
            created_persons.append(person)
        else:
            created_persons.append(existing)
    
    db.commit()
    print(f"Created {len([p for p in created_persons if p.id is None])} new persons")
    
    # Refresh to get IDs
    for person in created_persons:
        db.refresh(person)
    
    return created_persons

def create_dummy_deals(db: Session, persons: list):
    """Create dummy deals across different stages"""
    
    # Get person IDs by role
    person_by_role = {person.role: person.id for person in persons}
    
    deals_data = [
        # LEAD status deals
        {
            'title': 'Manufacturing CRM System - TechCorp',
            'description': 'Custom CRM system for manufacturing operations with inventory tracking',
            'status': 'lead',
            'priority': 'high',
            'customer_name': 'TechCorp Manufacturing',
            'customer_email': 'contact@techcorp.com',
            'estimated_value': 85000.0,
            'budget_range_min': 50000.0,
            'budget_range_max': 100000.0,
            'expected_close_date': datetime.now() + timedelta(days=45),
            'assigned_person_id': person_by_role.get(PersonRole.SALES),
            'board_position': 0
        },
        {
            'title': 'E-commerce Platform - ShopFast',
            'description': 'Modern e-commerce platform with mobile app and payment integration',
            'status': 'lead',
            'priority': 'high',
            'customer_name': 'RetailPlus',
            'customer_email': 'info@retailplus.com',
            'estimated_value': 120000.0,
            'budget_range_min': 75000.0,
            'budget_range_max': 150000.0,
            'expected_close_date': datetime.now() + timedelta(days=60),
            'assigned_person_id': person_by_role.get(PersonRole.SALES),
            'board_position': 1
        },
        {
            'title': 'Healthcare Management System',
            'description': 'Patient management system with appointment scheduling',
            'status': 'lead',
            'priority': 'urgent',
            'customer_name': 'HealthCare Solutions',
            'customer_email': 'admin@healthcare-solutions.com',
            'estimated_value': 200000.0,
            'budget_range_min': 150000.0,
            'budget_range_max': 250000.0,
            'expected_close_date': datetime.now() + timedelta(days=30),
            'assigned_person_id': person_by_role.get(PersonRole.SALES),
            'board_position': 2
        },
        
        # QUALIFIED_SOLUTION status deals
        {
            'title': 'Logistics Platform - FastShip',
            'description': 'Route optimization and fleet management system',
            'status': 'qualified_solution',
            'priority': 'high',
            'customer_name': 'FastShip Logistics',
            'customer_email': 'tech@fastship.com',
            'estimated_value': 90000.0,
            'budget_range_min': 60000.0,
            'budget_range_max': 120000.0,
            'expected_close_date': datetime.now() + timedelta(days=35),
            'assigned_person_id': person_by_role.get(PersonRole.HEAD_OF_ENGINEERING),
            'board_position': 0
        },
        {
            'title': 'Financial Services Platform',
            'description': 'Compliance tracking and reporting automation',
            'status': 'qualified_solution',
            'priority': 'high',
            'customer_name': 'SecureBank',
            'customer_email': 'it@securebank.com',
            'estimated_value': 300000.0,
            'budget_range_min': 250000.0,
            'budget_range_max': 350000.0,
            'expected_close_date': datetime.now() + timedelta(days=90),
            'assigned_person_id': person_by_role.get(PersonRole.HEAD_OF_ENGINEERING),
            'board_position': 1
        },
        
        # QUALIFIED_DELIVERY status deals
        {
            'title': 'Educational Platform - EduTech',
            'description': 'Student management and online learning platform',
            'status': 'qualified_delivery',
            'priority': 'medium',
            'customer_name': 'EduTech Institute',
            'customer_email': 'projects@edutech.edu',
            'estimated_value': 75000.0,
            'budget_range_min': 50000.0,
            'budget_range_max': 100000.0,
            'expected_close_date': datetime.now() + timedelta(days=50),
            'assigned_person_id': person_by_role.get(PersonRole.HEAD_OF_DELIVERY),
            'board_position': 0
        },
        
        # QUALIFIED_CSO status deals
        {
            'title': 'Supply Chain Management - GlobalTrade',
            'description': 'Vendor portal and procurement automation',
            'status': 'qualified_cso',
            'priority': 'high',
            'customer_name': 'GlobalTrade Corp',
            'customer_email': 'procurement@globaltrade.com',
            'estimated_value': 180000.0,
            'budget_range_min': 150000.0,
            'budget_range_max': 200000.0,
            'expected_close_date': datetime.now() + timedelta(days=25),
            'assigned_person_id': person_by_role.get(PersonRole.CSO),
            'board_position': 0
        },
        
        # DEAL status (closed deals)
        {
            'title': 'Real Estate Management - PropTech',
            'description': 'Property listings and client portal system',
            'status': 'deal',
            'priority': 'medium',
            'customer_name': 'PropTech Realty',
            'customer_email': 'systems@proptech.com',
            'estimated_value': 65000.0,
            'expected_close_date': datetime.now() - timedelta(days=5),
            'actual_close_date': datetime.now() - timedelta(days=5),
            'assigned_person_id': person_by_role.get(PersonRole.SALES),
            'board_position': 0
        },
        
        # PROJECT status (active projects)
        {
            'title': 'Construction Management - BuildFast',
            'description': 'Project management and cost tracking system',
            'status': 'project',
            'priority': 'high',
            'customer_name': 'BuildFast Construction',
            'customer_email': 'pm@buildfast.com',
            'estimated_value': 150000.0,
            'expected_close_date': datetime.now() - timedelta(days=30),
            'actual_close_date': datetime.now() - timedelta(days=30),
            'assigned_person_id': person_by_role.get(PersonRole.PROJECT_MANAGER),
            'board_position': 0
        }
    ]
    
    created_deals = []
    for deal_data in deals_data:
        deal = Deal(**deal_data)
        db.add(deal)
        created_deals.append(deal)
    
    db.commit()
    print(f"Created {len(created_deals)} deals")
    
    # Refresh to get IDs
    for deal in created_deals:
        db.refresh(deal)
    
    return created_deals

def create_conversation_data_from_csv(db: Session, deals: list):
    """Create conversation data from the CSV file"""
    
    # Read conversation data from CSV
    csv_file = '/Users/hoangtuan/Desktop/Projects/NFQ/poker-face/datasets/conversation-data.csv'
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            csv_data = list(reader)
        
        print(f"Read {len(csv_data)} conversation records from CSV")
        
        # Match deals with conversation data (first 10 deals get conversation data)
        for i, deal in enumerate(deals[:10]):
            if i < len(csv_data):
                csv_row = csv_data[i]
                
                conversation = ConversationData(
                    deal_id=deal.id,
                    customer_requirements=csv_row.get('customer_requirements', ''),
                    business_goals=csv_row.get('business_goals', ''),
                    pain_points=csv_row.get('pain_points', ''),
                    current_solutions=csv_row.get('current_solutions', ''),
                    tech_preferences=csv_row.get('tech_preferences', ''),
                    integration_needs=csv_row.get('integration_needs', ''),
                    compliance_requirements=csv_row.get('compliance_requirements', ''),
                    project_timeline=csv_row.get('project_timeline', ''),
                    urgency_level=csv_row.get('urgency_level', ''),
                    team_size=csv_row.get('team_size', ''),
                    location_preference=csv_row.get('location_preference', ''),
                    communication_style=csv_row.get('communication_style', ''),
                    decision_makers=csv_row.get('decision_makers', ''),
                    follow_up_needed=csv_row.get('follow_up_needed', ''),
                    sales_notes=csv_row.get('sales_notes', ''),
                    last_conversation_date=datetime.strptime(csv_row.get('conversation_date', '2024-01-01'), '%Y-%m-%d') if csv_row.get('conversation_date') else datetime.now(),
                    communication_channel=csv_row.get('communication_channel', ''),
                    conversation_type=csv_row.get('conversation_type', '')
                )
                
                db.add(conversation)
        
        db.commit()
        print(f"Created conversation data for {min(10, len(deals))} deals")
        
    except FileNotFoundError:
        print(f"Conversation CSV file not found at {csv_file}")
        print("Creating basic conversation data instead...")
        
        # Create basic conversation data for the first few deals
        basic_conversations = [
            {
                'customer_requirements': 'Need custom CRM system for manufacturing operations',
                'business_goals': 'Improve operational efficiency by 40%',
                'pain_points': 'Manual processes, data silos, poor customer visibility',
                'urgency_level': 'Medium',
                'sales_notes': 'Strong technical requirements, budget confirmed'
            },
            {
                'customer_requirements': 'E-commerce platform with advanced analytics',
                'business_goals': 'Increase online sales by 60%',
                'pain_points': 'Poor mobile experience, limited analytics',
                'urgency_level': 'High',
                'sales_notes': 'Very interested in analytics capabilities'
            }
        ]
        
        for i, deal in enumerate(deals[:2]):
            if i < len(basic_conversations):
                conv_data = basic_conversations[i]
                conversation = ConversationData(
                    deal_id=deal.id,
                    **conv_data
                )
                db.add(conversation)
        
        db.commit()
        print(f"Created basic conversation data for {min(2, len(deals))} deals")

def initialize_sprint_database():
    """Initialize the sprint board database with dummy data"""
    
    print("Initializing sprint board database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create dummy data
        print("\n1. Creating team members...")
        persons = create_dummy_persons(db)
        
        print("\n2. Creating deals...")
        deals = create_dummy_deals(db, persons)
        
        print("\n3. Creating conversation data...")
        create_conversation_data_from_csv(db, deals)
        
        print(f"\n✅ Sprint board initialization complete!")
        print(f"Created:")
        print(f"  - {len(persons)} team members")
        print(f"  - {len(deals)} deals")
        print(f"  - Conversation data for deals")
        
        print(f"\nDeals by status:")
        for status in DealStatus:
            count = len([d for d in deals if d.status == status])
            print(f"  - {status.value.replace('_', ' ').title()}: {count}")
        
        print(f"\nYou can now:")
        print(f"  1. Start the backend: cd backend && uvicorn main:app --reload")
        print(f"  2. Start the frontend: cd frontend && npm start")
        print(f"  3. Visit: http://localhost:3000/sprint-board")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_sprint_database()