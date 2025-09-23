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
    Base, Deal, Person, ConversationData, Comment, Contact, DealStatus, Priority, PersonRole
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

    # Decision makers - use actual person names instead of titles
    decision_makers_names = [
        "John Smith, Sarah Johnson",
        "Michael Brown, Lisa Davis, Robert Wilson",
        "Jennifer Garcia, David Miller, Susan Anderson",
        "James Thompson, Patricia White",
        "Christopher Lee, Linda Harris, Daniel Clark",
        "Barbara Lewis, Matthew Walker",
        "Susan Hall, Anthony Allen, Nancy Young",
        "Mark Taylor, Karen Thomas",
        "Paul Jackson, Helen White, Steven Harris",
        "Donna Martin, Kevin Thompson, Betty Garcia"
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
        decision_makers = random.choice(decision_makers_names)
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

        # Generate contract completion tracking data for closed deals
        contract_signed_date = None
        finance_contacted_date = None
        email_reminder_sent = False
        last_reminder_date = None

        if status == 'deal' and actual_close_date:
            # Create various scenarios for contract completion tracking
            days_since_close = (datetime.now() - actual_close_date).days

            # Scenario 1: Both tasks completed within 30 days (40% of deals)
            if random.random() < 0.4:
                contract_signed_date = actual_close_date + timedelta(days=random.randint(1, 25))
                finance_contacted_date = actual_close_date + timedelta(days=random.randint(1, 28))

            # Scenario 2: One task missing and overdue (30% of deals)
            elif random.random() < 0.7 and days_since_close > 30:
                if random.random() < 0.5:
                    # Contract signed but finance not contacted
                    contract_signed_date = actual_close_date + timedelta(days=random.randint(1, 25))
                else:
                    # Finance contacted but contract not signed
                    finance_contacted_date = actual_close_date + timedelta(days=random.randint(1, 28))

                # Set reminder email sent for overdue deals
                email_reminder_sent = True
                last_reminder_date = datetime.now() - timedelta(days=random.randint(1, 7))

            # Scenario 3: Both tasks missing and overdue (20% of deals)
            elif days_since_close > 30:
                email_reminder_sent = True
                last_reminder_date = datetime.now() - timedelta(days=random.randint(1, 7))

            # Scenario 4: Approaching deadline but not overdue (10% of deals)
            # Leave both tasks incomplete for recent deals

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
            'board_position': i % 10,  # Distribute across board positions
            # Contract completion tracking
            'contract_signed_date': contract_signed_date,
            'finance_contacted_date': finance_contacted_date,
            'email_reminder_sent': email_reminder_sent,
            'last_reminder_date': last_reminder_date
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

def create_deal_comments(db: Session, deals, persons):
    """Create realistic comments for deals"""

    # Comment templates by role
    sales_comments = [
        "Customer is very interested in the solution. They want to schedule a demo next week.",
        "Had a great call with the decision maker. Budget is confirmed at ${budget}.",
        "Customer has some concerns about implementation timeline. Need to address this.",
        "Competitor analysis shows we have a strong advantage in this space.",
        "Customer is ready to move forward. Waiting for technical requirements.",
        "Follow-up meeting scheduled for next Tuesday to discuss pricing.",
        "Customer loves our approach. They're comparing with one other vendor.",
        "Need to get legal involved for contract review. Customer is eager to proceed.",
        "Customer asked for references from similar implementations.",
        "Pricing discussion went well. They're within our target range."
    ]

    engineering_comments = [
        "Technical requirements look straightforward. Estimated 3-4 months development.",
        "Customer has some unique integration requirements that need investigation.",
        "Architecture review completed. Recommend microservices approach.",
        "Security requirements are extensive but manageable with our current stack.",
        "Performance requirements are challenging but achievable.",
        "Customer's existing infrastructure is compatible with our solution.",
        "Need to clarify data migration requirements from their legacy system.",
        "Scalability requirements align well with our platform capabilities.",
        "Customer's technical team is very knowledgeable. Good collaboration potential.",
        "Some custom development required but within scope of standard offering."
    ]

    management_comments = [
        "This deal aligns perfectly with our Q4 targets. High priority.",
        "Resource allocation approved. Team can start immediately after contract signing.",
        "Customer profile matches our ideal client. Strong strategic fit.",
        "Recommend fast-tracking this opportunity. Competitive situation.",
        "Budget approval needed for additional resources if we win this deal.",
        "Customer has potential for expansion into other business units.",
        "Risk assessment completed. Low risk, high reward opportunity.",
        "Timeline is aggressive but achievable with current team capacity.",
        "Customer references check out. Financially stable organization.",
        "This could be a showcase project for our new capabilities."
    ]

    # Team member roles mapping
    role_comments = {
        PersonRole.SALES: sales_comments,
        PersonRole.HEAD_OF_ENGINEERING: engineering_comments,
        PersonRole.HEAD_OF_DELIVERY: engineering_comments,
        PersonRole.PROJECT_MANAGER: engineering_comments,
        PersonRole.CSO: management_comments
    }

    comments_created = 0

    for deal in deals:
        # Generate 2-5 comments per deal
        num_comments = random.randint(2, 5)

        for i in range(num_comments):
            # Select random team member
            commenter = random.choice(persons)

            # Get appropriate comment template based on role
            role_comment_pool = role_comments.get(commenter.role, sales_comments)
            comment_text = random.choice(role_comment_pool)

            # Replace budget placeholder if present
            if "{budget}" in comment_text:
                budget_value = f"{deal.estimated_value:,.0f}" if deal.estimated_value else "TBD"
                comment_text = comment_text.replace("{budget}", budget_value)

            # Generate timestamp (within last 30 days)
            days_ago = random.randint(1, 30)
            comment_date = datetime.now() - timedelta(days=days_ago)

            # Create comment
            comment = Comment(
                deal_id=deal.id,
                commenter_name=commenter.name,
                commenter_role=commenter.role.value.title(),
                comment_text=comment_text,
                created_at=comment_date
            )

            db.add(comment)
            comments_created += 1

    db.commit()
    print(f"Created {comments_created} comments across {len(deals)} deals")

def create_dummy_contacts(db: Session, persons: list):
    """Create dummy contacts with realistic data"""

    # Sample companies and industries
    companies = [
        {"name": "TechCorp Manufacturing", "industry": "Manufacturing"},
        {"name": "SecureBank", "industry": "Financial Services"},
        {"name": "HealthCare Solutions", "industry": "Healthcare"},
        {"name": "RetailPlus", "industry": "E-commerce"},
        {"name": "GlobalTrade Corp", "industry": "Supply Chain"},
        {"name": "FastShip Logistics", "industry": "Logistics"},
        {"name": "EduTech Institute", "industry": "Education"},
        {"name": "PropTech Realty", "industry": "Real Estate"},
        {"name": "BuildFast Construction", "industry": "Construction"},
        {"name": "GreenEnergy Solutions", "industry": "Energy"},
        {"name": "DataFlow Analytics", "industry": "Data Analytics"},
        {"name": "CloudFirst Technologies", "industry": "Cloud Services"},
        {"name": "AutoDrive Motors", "industry": "Automotive"},
        {"name": "FoodChain Distributors", "industry": "Food & Beverage"},
        {"name": "MedDevice Innovations", "industry": "Medical Devices"}
    ]

    # Sample positions
    positions = [
        "CEO", "CTO", "CFO", "COO", "VP of Technology", "VP of Sales",
        "Director of IT", "Director of Operations", "Head of Digital",
        "Chief Digital Officer", "VP of Engineering", "Head of Innovation",
        "Director of Strategy", "VP of Business Development", "Chief Innovation Officer"
    ]

    # Sample delivery teams
    delivery_teams = [
        "Alpha Team", "Beta Team", "Gamma Team", "Delta Team", "Enterprise Team",
        "Innovation Lab", "Core Platform Team", "Digital Solutions Team"
    ]

    # Sample statuses with realistic distribution
    statuses = [
        ("lead", 0.3),
        ("qualified_solution", 0.25),
        ("qualified_delivery", 0.2),
        ("qualified_cso", 0.15),
        ("deal", 0.07),
        ("project", 0.03)
    ]

    contacts = []

    for i in range(30):  # Create 30 contacts
        company = random.choice(companies)
        position = random.choice(positions)

        # Generate realistic names
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily",
                      "James", "Maria", "William", "Jennifer", "Richard", "Patricia", "Charles"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                     "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson"]

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"

        # Generate email
        email = f"{first_name.lower()}.{last_name.lower()}@{company['name'].lower().replace(' ', '').replace('corp', 'corp')}.com"

        # Generate phone number
        phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

        # Select status based on distribution
        status_choice = random.random()
        cumulative = 0
        selected_status = "lead"
        for status, probability in statuses:
            cumulative += probability
            if status_choice <= cumulative:
                selected_status = status
                break

        # Generate realistic financial data based on company size and industry
        base_gmv = random.uniform(50000, 2000000)
        estimated_revenue = base_gmv * random.uniform(0.1, 0.3)  # 10-30% of GMV

        # Generate estimated close date (next 3-12 months)
        days_ahead = random.randint(30, 365)
        estimated_close_date = datetime.now() + timedelta(days=days_ahead)

        # Assign contact owner and solution designer
        contact_owner = random.choice([p for p in persons if p.role == PersonRole.SALES])
        solution_designer = random.choice([p for p in persons if p.role in [PersonRole.HEAD_OF_ENGINEERING, PersonRole.HEAD_OF_DELIVERY]])

        # Generate notes
        notes = [
            f"Interested in {company['industry'].lower()} solutions",
            f"Looking to modernize their {company['industry'].lower()} operations",
            f"Evaluating multiple vendors for {company['industry'].lower()} transformation",
            f"Budget approved for Q{random.randint(1,4)} implementation",
            f"Strong technical team, looking for strategic partnership",
            f"Previous experience with similar solutions in {company['industry'].lower()}",
            f"Urgent need due to {company['industry'].lower()} compliance requirements"
        ]

        contact = Contact(
            full_name=full_name,
            position=position,
            company_name=company["name"],
            email=email,
            phone_number=phone,
            gmv=base_gmv,
            estimated_revenue=estimated_revenue,
            estimated_close_date=estimated_close_date,
            contact_owner_id=contact_owner.id,
            status=selected_status,
            delivery_team_assigned=random.choice(delivery_teams),
            solution_designer_id=solution_designer.id,
            note=random.choice(notes),
            created_at=datetime.now() - timedelta(days=random.randint(1, 180))
        )

        db.add(contact)
        contacts.append(contact)

    db.commit()
    print(f"Created {len(contacts)} contacts")
    return contacts

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

        print("\n4. Creating deal comments...")
        create_deal_comments(db, deals, persons)

        print("\n5. Creating contacts...")
        contacts = create_dummy_contacts(db, persons)

        print(f"\n✅ Sprint board initialization complete!")
        print(f"Created:")
        print(f"  - {len(persons)} team members")
        print(f"  - {len(deals)} deals")
        print(f"  - {len(contacts)} contacts")
        print(f"  - Conversation data for deals")

        print(f"\nDeals by status:")
        for status in DealStatus:
            count = len([d for d in deals if d.status == status])
            print(f"  - {status.value.replace('_', ' ').title()}: {count}")

        print(f"\nContacts by status:")
        for status in ["lead", "qualified_solution", "qualified_delivery", "qualified_cso", "deal", "project"]:
            count = len([c for c in contacts if c.status == status])
            print(f"  - {status.replace('_', ' ').title()}: {count}")

        print(f"\nYou can now:")
        print(f"  1. Start the backend: cd backend && uvicorn main:app --reload")
        print(f"  2. Start the frontend: cd frontend && npm start")
        print(f"  3. Visit: http://localhost:3000/sprint-board")
        print(f"  4. Visit: http://localhost:3000/contacts")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_sprint_database()