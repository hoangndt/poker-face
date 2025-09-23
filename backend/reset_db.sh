#!/bin/bash

echo "🗑️  Resetting database..."
python -c "
from database import engine
from sprint_models import Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('✅ Database schema reset')
"

echo "📊 Initializing sample data..."
python init_sprint_db.py
echo "🚀 Database ready!"