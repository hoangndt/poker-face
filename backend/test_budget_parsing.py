#!/usr/bin/env python3
"""
Test budget parsing function to ensure it handles various string formats correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sprint_api import parse_budget_value

def test_budget_parsing():
    """Test various budget string formats."""
    test_cases = [
        # (input, expected_output)
        ('$252k - $327k', 289500.0),  # Average of range
        ('$150,000', 150000.0),       # With commas
        ('300k', 300000.0),           # No currency symbol
        ('1.5M', 1500000.0),          # Millions
        ('$50k', 50000.0),            # Single k value
        ('0', 0.0),                   # Zero
        (0, 0.0),                     # Numeric zero
        ('', 0.0),                    # Empty string
        (None, 0.0),                  # None
        (150000, 150000.0),           # Already numeric
    ]
    
    print("🧪 Testing Budget Parsing Function\n")
    
    all_passed = True
    for input_val, expected in test_cases:
        try:
            result = parse_budget_value(input_val)
            if abs(result - expected) < 0.01:  # Allow small floating point differences
                print(f"✅ '{input_val}' → {result} (expected {expected})")
            else:
                print(f"❌ '{input_val}' → {result} (expected {expected})")
                all_passed = False
        except Exception as e:
            print(f"❌ '{input_val}' → ERROR: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    if test_budget_parsing():
        print("\n🎉 All budget parsing tests passed!")
    else:
        print("\n❌ Some budget parsing tests failed!")