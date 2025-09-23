#!/usr/bin/env python3

# Simple script to fix the init script enum values

import re

# Read the original file
with open('init_sprint_db.py', 'r') as f:
    content = f.read()

# Fix corrupted enum references
content = re.sub(r'DealStatus\.[A-Z_]+\.value\.value', 'DealStatus.LEAD.value', content)
content = re.sub(r'Priority\.[A-Z_]+\.value\.value', 'Priority.HIGH.value', content)

# Fix specific status values based on position in file
content = content.replace("'status': DealStatus.LEAD.value,", "'status': 'lead',")
content = content.replace("'status': DealStatus.QUALIFIED_SOLUTION.value,", "'status': 'qualified_solution',")
content = content.replace("'status': DealStatus.QUALIFIED_DELIVERY.value,", "'status': 'qualified_delivery',")
content = content.replace("'status': DealStatus.QUALIFIED_CSO.value,", "'status': 'qualified_cso',")
content = content.replace("'status': DealStatus.DEAL.value,", "'status': 'deal',")
content = content.replace("'status': DealStatus.PROJECT.value,", "'status': 'project',")

# Fix priority values
content = content.replace("'priority': Priority.HIGH.value,", "'priority': 'high',")
content = content.replace("'priority': Priority.MEDIUM.value,", "'priority': 'medium',")
content = content.replace("'priority': Priority.LOW.value,", "'priority': 'low',")
content = content.replace("'priority': Priority.URGENT.value,", "'priority': 'urgent',")

# Write the fixed file
with open('init_sprint_db.py', 'w') as f:
    f.write(content)

print("Fixed init script enum references")