#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing database imports...")
    from database import get_db, engine
    print("✅ Database imports successful")
    
    print("Testing model imports...")
    from models import CustomerData, LifecycleStage, CustomerActivity, ChurnPredictions, RevenueForecastData
    print("✅ Model imports successful")
    
    print("Testing schema imports...")
    from schemas import CustomerResponse, LifecycleAnalytics, RevenueMetrics, RevenueForecast, ChurnPrediction
    print("✅ Schema imports successful")
    
    print("Testing CRUD imports...")
    import crud
    print("✅ CRUD imports successful")
    
    print("Testing AI model imports...")
    from ai_models import ChurnPredictor, RevenueForecaster, LeadScorer, CLVCalculator
    print("✅ AI model imports successful")
    
    print("Testing main app import...")
    from main import app
    print("✅ Main app import successful")
    
    print("\n🎉 All imports successful! The FastAPI app should start correctly.")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()