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
        },
        # Additional solution owners
        {
            'name': 'Michael Thompson',
            'email': 'michael.thompson@company.com',
            'role': PersonRole.HEAD_OF_ENGINEERING,
            'department': 'Engineering',
            'skills': '{"skills": ["Cloud Architecture", "DevOps", "Microservices", "AI/ML"]}',
            'availability': 0.8,
            'hourly_rate': 220.0
        },
        {
            'name': 'Sarah Kim',
            'email': 'sarah.kim@company.com',
            'role': PersonRole.HEAD_OF_ENGINEERING,
            'department': 'Engineering',
            'skills': '{"skills": ["Frontend Development", "UX/UI", "Mobile Development"]}',
            'availability': 0.85,
            'hourly_rate': 190.0
        },
        {
            'name': 'James Anderson',
            'email': 'james.anderson@company.com',
            'role': PersonRole.HEAD_OF_DELIVERY,
            'department': 'Delivery',
            'skills': '{"skills": ["Enterprise Solutions", "Integration", "Security"]}',
            'availability': 0.7,
            'hourly_rate': 210.0
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
    """Create 50 dummy deals across different stages with enhanced data"""

    # Get person IDs by role for assignment
    sales_persons = [p.id for p in persons if p.role == PersonRole.SALES]
    engineering_persons = [p.id for p in persons if p.role == PersonRole.HEAD_OF_ENGINEERING]
    delivery_persons = [p.id for p in persons if p.role == PersonRole.HEAD_OF_DELIVERY]
    cso_persons = [p.id for p in persons if p.role == PersonRole.CSO]
    pm_persons = [p.id for p in persons if p.role == PersonRole.PROJECT_MANAGER]

    # All persons for solution owners
    all_persons = [p.id for p in persons]

    # Data for generating realistic deals
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East & Africa"]
    countries = {
        "North America": ["United States", "Canada", "Mexico"],
        "Europe": ["Germany", "United Kingdom", "France", "Netherlands", "Spain", "Italy"],
        "Asia-Pacific": ["Japan", "Australia", "Singapore", "South Korea", "India"],
        "Latin America": ["Brazil", "Argentina", "Chile", "Colombia"],
        "Middle East & Africa": ["UAE", "Saudi Arabia", "South Africa", "Egypt"]
    }

    contact_names = [
        "John Smith", "Emily Davis", "Michael Brown", "Sarah Wilson", "David Johnson",
        "Lisa Anderson", "Robert Taylor", "Jennifer Martinez", "William Garcia", "Maria Rodriguez",
        "James Thompson", "Patricia White", "Christopher Lee", "Linda Harris", "Daniel Clark",
        "Barbara Lewis", "Matthew Walker", "Susan Hall", "Anthony Allen", "Nancy Young"
    ]

    # Decision makers templates for different company sizes
    decision_makers_templates = [
        "CEO, CTO",
        "CEO, CFO, CTO",
        "VP Engineering, Director of Operations",
        "CTO, Head of Product",
        "CEO, VP Sales, CTO",
        "Managing Director, IT Director",
        "President, VP Technology",
        "CEO, Head of Digital Transformation",
        "CTO, VP Engineering, Product Manager",
        "CEO, CFO, Head of IT"
    ]

    velocities = ["Fast", "Medium", "Slow"]
    deal_stages = ["Closed Won", "Closed Lost", "Negotiation", "Proposal", "Discovery", "Qualification"]

    # Base deal templates
    deal_templates = [
        {
            'title': 'Manufacturing CRM System - TechCorp',
            'description': 'Custom CRM system for manufacturing operations with inventory tracking',
            'deal_description': 'Comprehensive CRM solution designed specifically for manufacturing companies, featuring real-time inventory tracking, production planning integration, and customer lifecycle management.',
            'customer_name': 'TechCorp Manufacturing',
            'customer_email': 'contact@techcorp.com',
            'estimated_value': 85000.0,
            'budget_range_min': 50000.0,
            'budget_range_max': 100000.0,
        },
        {
            'title': 'E-commerce Platform - ShopFast',
            'description': 'Modern e-commerce platform with mobile app and payment integration',
            'deal_description': 'Next-generation e-commerce platform with advanced analytics, mobile-first design, multi-payment gateway integration, and AI-powered recommendation engine.',
            'customer_name': 'RetailPlus',
            'customer_email': 'info@retailplus.com',
            'estimated_value': 120000.0,
            'budget_range_min': 75000.0,
            'budget_range_max': 150000.0,
        },
        {
            'title': 'Healthcare Management System',
            'description': 'Patient management system with appointment scheduling',
            'deal_description': 'Comprehensive healthcare management platform featuring patient records, appointment scheduling, billing integration, and HIPAA-compliant data management.',
            'customer_name': 'HealthCare Solutions',
            'customer_email': 'admin@healthcare-solutions.com',
            'estimated_value': 200000.0,
            'budget_range_min': 150000.0,
            'budget_range_max': 250000.0,
        },
        {
            'title': 'Financial Services Platform',
            'description': 'Compliance tracking and reporting automation',
            'deal_description': 'Enterprise-grade financial services platform with automated compliance reporting, risk management, and regulatory tracking capabilities.',
            'customer_name': 'SecureBank',
            'customer_email': 'it@securebank.com',
            'estimated_value': 300000.0,
            'budget_range_min': 250000.0,
            'budget_range_max': 350000.0,
        },
        {
            'title': 'Logistics Platform - FastShip',
            'description': 'Route optimization and fleet management system',
            'deal_description': 'Advanced logistics management system with real-time route optimization, fleet tracking, and delivery performance analytics.',
            'customer_name': 'FastShip Logistics',
            'customer_email': 'tech@fastship.com',
            'estimated_value': 90000.0,
            'budget_range_min': 60000.0,
            'budget_range_max': 120000.0,
        },
        {
            'title': 'Educational Platform - EduTech',
            'description': 'Student management and online learning platform',
            'deal_description': 'Comprehensive educational technology platform with student information system, online learning modules, and performance analytics.',
            'customer_name': 'EduTech Institute',
            'customer_email': 'projects@edutech.edu',
            'estimated_value': 75000.0,
            'budget_range_min': 50000.0,
            'budget_range_max': 100000.0,
        },
        {
            'title': 'Supply Chain Management - GlobalTrade',
            'description': 'Vendor portal and procurement automation',
            'deal_description': 'Enterprise supply chain management solution with vendor portal, automated procurement workflows, and supply chain visibility.',
            'customer_name': 'GlobalTrade Corp',
            'customer_email': 'procurement@globaltrade.com',
            'estimated_value': 180000.0,
            'budget_range_min': 150000.0,
            'budget_range_max': 200000.0,
        },
        {
            'title': 'Real Estate Management - PropTech',
            'description': 'Property listings and client portal system',
            'deal_description': 'Modern real estate management platform with property listings, client portal, virtual tours, and transaction management.',
            'customer_name': 'PropTech Realty',
            'customer_email': 'systems@proptech.com',
            'estimated_value': 65000.0,
            'budget_range_min': 45000.0,
            'budget_range_max': 85000.0,
        },
        {
            'title': 'Construction Management - BuildFast',
            'description': 'Project management and cost tracking system',
            'deal_description': 'Comprehensive construction project management platform with cost tracking, resource allocation, and progress monitoring.',
            'customer_name': 'BuildFast Construction',
            'customer_email': 'pm@buildfast.com',
            'estimated_value': 150000.0,
            'budget_range_min': 120000.0,
            'budget_range_max': 180000.0,
        }
    ]
        

    # Generate 50 deals using the templates
    statuses = ['lead', 'qualified_solution', 'qualified_delivery', 'qualified_cso', 'deal', 'project']
    priorities = ['low', 'medium', 'high', 'urgent']

    created_deals = []

    for i in range(50):
        # Use template cyclically
        template = deal_templates[i % len(deal_templates)]

        # Select region and country
        region = random.choice(regions)
        country = random.choice(countries[region])

        # Generate deal data
        status = random.choice(statuses)
        priority = random.choice(priorities)
        velocity = random.choice(velocities)
        deal_stage = random.choice(deal_stages)
        contact_person = random.choice(contact_names)
        decision_makers = random.choice(decision_makers_templates)
        deal_probability = random.randint(10, 95)

        # Calculate weighted amount in Euros
        estimated_value_eur = template['estimated_value'] * 0.85  # Convert to EUR (approximate)
        weighted_amount = estimated_value_eur * (deal_probability / 100)

        # Assign persons based on status
        if status == 'lead':
            assigned_person_id = random.choice(sales_persons) if sales_persons else None
        elif status == 'qualified_solution':
            assigned_person_id = random.choice(engineering_persons) if engineering_persons else None
        elif status == 'qualified_delivery':
            assigned_person_id = random.choice(delivery_persons) if delivery_persons else None
        elif status == 'qualified_cso':
            assigned_person_id = random.choice(cso_persons) if cso_persons else None
        elif status == 'project':
            assigned_person_id = random.choice(pm_persons) if pm_persons else None
        else:  # deal
            assigned_person_id = random.choice(sales_persons) if sales_persons else None

        solution_owner_id = random.choice(all_persons) if all_persons else None

        # Generate dates
        if status in ['deal', 'project']:
            expected_close_date = datetime.now() - timedelta(days=random.randint(1, 60))
            actual_close_date = expected_close_date + timedelta(days=random.randint(-5, 10))
        else:
            expected_close_date = datetime.now() + timedelta(days=random.randint(15, 120))
            actual_close_date = None

        # Create unique title if it's a duplicate
        title = template['title']
        if i > 0:
            title = f"{template['title']} - {i+1}"

        deal_data = {
            'title': title,
            'description': template['description'],
            'deal_description': template['deal_description'],
            'status': status,
            'priority': priority,
            'customer_name': template['customer_name'],
            'customer_email': template['customer_email'],
            'contact_person': contact_person,
            'decision_makers': decision_makers,
            'region': region,
            'country': country,
            'estimated_value': template['estimated_value'],
            'budget_range_min': template['budget_range_min'],
            'budget_range_max': template['budget_range_max'],
            'expected_close_date': expected_close_date,
            'actual_close_date': actual_close_date,
            'assigned_person_id': assigned_person_id,
            'solution_owner_id': solution_owner_id,
            'velocity': velocity,
            'deal_stage': deal_stage,
            'deal_probability': deal_probability,
            'weighted_amount': weighted_amount,
            'board_position': i % 10  # Distribute across board positions
        }

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