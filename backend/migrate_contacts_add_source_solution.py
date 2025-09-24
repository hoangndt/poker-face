#!/usr/bin/env python3
"""
Migration script to add lead_source and solution_interest columns to contacts table
and populate them with realistic dummy data.
"""

import sqlite3
import random
from datetime import datetime

# Define the source and solution options
LEAD_SOURCES = [
    "SEO",
    "Networking Event", 
    "Summit Event",
    "Cold Outreach",
    "Referral",
    "Social Media",
    "Website Form",
    "Trade Show",
    "Partner Referral",
    "Content Marketing"
]

SOLUTION_INTERESTS = [
    "Enterprise Software",
    "Cloud Infrastructure", 
    "Data Analytics",
    "CRM Solutions",
    "Marketing Automation",
    "Cybersecurity",
    "AI/ML Platform",
    "E-commerce Platform",
    "Business Intelligence",
    "Integration Services"
]

# Define realistic combinations - certain sources are more likely to be interested in specific solutions
SOURCE_SOLUTION_PREFERENCES = {
    "SEO": ["Enterprise Software", "CRM Solutions", "Marketing Automation", "E-commerce Platform"],
    "Networking Event": ["Enterprise Software", "Business Intelligence", "CRM Solutions", "AI/ML Platform"],
    "Summit Event": ["Enterprise Software", "AI/ML Platform", "Cloud Infrastructure", "Data Analytics"],
    "Cold Outreach": ["CRM Solutions", "Marketing Automation", "Enterprise Software", "Business Intelligence"],
    "Referral": ["Enterprise Software", "Cloud Infrastructure", "Cybersecurity", "Integration Services"],
    "Social Media": ["Marketing Automation", "E-commerce Platform", "CRM Solutions", "AI/ML Platform"],
    "Website Form": ["Enterprise Software", "Cloud Infrastructure", "Data Analytics", "CRM Solutions"],
    "Trade Show": ["Enterprise Software", "Cybersecurity", "Cloud Infrastructure", "Business Intelligence"],
    "Partner Referral": ["Integration Services", "Enterprise Software", "Cloud Infrastructure", "Cybersecurity"],
    "Content Marketing": ["Data Analytics", "AI/ML Platform", "Business Intelligence", "Marketing Automation"]
}

def get_weighted_solution(source):
    """Get a solution interest based on the lead source with realistic weighting"""
    preferred_solutions = SOURCE_SOLUTION_PREFERENCES.get(source, SOLUTION_INTERESTS)
    
    # 70% chance of getting a preferred solution, 30% chance of any solution
    if random.random() < 0.7:
        return random.choice(preferred_solutions)
    else:
        return random.choice(SOLUTION_INTERESTS)

def migrate_contacts():
    """Add new columns and populate with realistic data"""
    
    # Connect to database
    conn = sqlite3.connect('customer_lifecycle.db')
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add lead_source column if it doesn't exist
        if 'lead_source' not in columns:
            print("Adding lead_source column...")
            cursor.execute("ALTER TABLE contacts ADD COLUMN lead_source TEXT")
        else:
            print("lead_source column already exists")
            
        # Add solution_interest column if it doesn't exist
        if 'solution_interest' not in columns:
            print("Adding solution_interest column...")
            cursor.execute("ALTER TABLE contacts ADD COLUMN solution_interest TEXT")
        else:
            print("solution_interest column already exists")
        
        # Get all contacts that need data
        cursor.execute("SELECT id, full_name, company_name FROM contacts WHERE lead_source IS NULL OR solution_interest IS NULL")
        contacts = cursor.fetchall()
        
        print(f"Found {len(contacts)} contacts to update...")
        
        # Update each contact with realistic data
        for contact_id, full_name, company_name in contacts:
            # Select a random lead source
            lead_source = random.choice(LEAD_SOURCES)
            
            # Select a solution interest based on the lead source
            solution_interest = get_weighted_solution(lead_source)
            
            # Update the contact
            cursor.execute("""
                UPDATE contacts 
                SET lead_source = ?, solution_interest = ?, updated_at = ?
                WHERE id = ?
            """, (lead_source, solution_interest, datetime.utcnow(), contact_id))
            
            print(f"Updated {full_name} ({company_name}): {lead_source} → {solution_interest}")
        
        # Commit changes
        conn.commit()
        print(f"\nSuccessfully updated {len(contacts)} contacts!")
        
        # Show summary statistics
        print("\n=== SUMMARY STATISTICS ===")
        
        print("\nLead Source Distribution:")
        cursor.execute("SELECT lead_source, COUNT(*) FROM contacts GROUP BY lead_source ORDER BY COUNT(*) DESC")
        for source, count in cursor.fetchall():
            print(f"  {source}: {count}")
            
        print("\nSolution Interest Distribution:")
        cursor.execute("SELECT solution_interest, COUNT(*) FROM contacts GROUP BY solution_interest ORDER BY COUNT(*) DESC")
        for solution, count in cursor.fetchall():
            print(f"  {solution}: {count}")
            
        print("\nTop Source-Solution Combinations:")
        cursor.execute("""
            SELECT lead_source, solution_interest, COUNT(*) as count 
            FROM contacts 
            GROUP BY lead_source, solution_interest 
            ORDER BY count DESC 
            LIMIT 10
        """)
        for source, solution, count in cursor.fetchall():
            print(f"  {source} → {solution}: {count}")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting contacts migration...")
    migrate_contacts()
    print("Migration completed!")
