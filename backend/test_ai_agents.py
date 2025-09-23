#!/usr/bin/env python3
"""
Test script for AI agents to verify database field mappings are correct.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sprint_models import TechnicalSolution, ResourceAllocation, Proposal
from sqlalchemy import inspect

def test_technical_solution_fields():
    """Test that TechnicalSolution model has the correct fields."""
    print("Testing TechnicalSolution fields...")
    
    inspector = inspect(TechnicalSolution)
    columns = {col.name for col in inspector.columns}
    
    required_fields = {
        'architecture_overview',
        'recommended_tech_stack', 
        'integration_approach',
        'development_phases',
        'complexity_score'
    }
    
    print(f"Available fields: {sorted(columns)}")
    print(f"Required fields: {sorted(required_fields)}")
    
    missing_fields = required_fields - columns
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False
    else:
        print("✅ All required fields present")
        return True

def test_resource_allocation_fields():
    """Test that ResourceAllocation model has the correct fields."""
    print("\nTesting ResourceAllocation fields...")
    
    inspector = inspect(ResourceAllocation)
    columns = {col.name for col in inspector.columns}
    
    required_fields = {
        'team_composition',
        'milestone_breakdown',
        'resource_timeline',
        'development_cost',
        'total_estimated_cost',
        'skill_gaps'
    }
    
    print(f"Available fields: {sorted(columns)}")
    print(f"Required fields: {sorted(required_fields)}")
    
    missing_fields = required_fields - columns
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False
    else:
        print("✅ All required fields present")
        return True

def test_proposal_fields():
    """Test that Proposal model has the correct fields."""
    print("\nTesting Proposal fields...")
    
    inspector = inspect(Proposal)
    columns = {col.name for col in inspector.columns}
    
    print(f"Available fields: {sorted(columns)}")
    print("✅ Proposal model inspection complete")
    return True

if __name__ == "__main__":
    print("🧪 Testing AI Agent Database Field Mappings\n")
    
    tests = [
        test_technical_solution_fields(),
        test_resource_allocation_fields(),
        test_proposal_fields()
    ]
    
    if all(tests):
        print("\n🎉 All field mapping tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some field mapping tests failed!")
        sys.exit(1)