"""
Vietnam-specific Customer Lifecycle Models
Based on Gradion's actual workflow and pain points
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib

class GradionLeadScorer:
    """
    Vietnam-specific lead scoring based on Gradion's actual criteria:
    - Lead Score ≤109 → MQL
    - Lead Score ≥110 → SQL  
    - Book Consultant = TRUE → SQL (override)
    """
    
    def __init__(self):
        self.mql_threshold = 109
        self.sql_threshold = 110
        self.model = None
        
    def calculate_vietnam_lead_score(self, lead_data: Dict) -> Dict:
        """Calculate lead score using Gradion's specific criteria"""
        
        score = 0
        details = []
        
        # Source scoring (matching Gradion's channels)
        source_scores = {
            'LinkedIn Ads': 25,
            'Sales Navigator': 30,
            'Google Ads': 20,
            'Facebook Ads': 15,
            'Events': 35,  # Automation World, ACE Grand Opening, DMEXCO
            'Landing Page': 20,
            'Whitepaper Download': 25,
            'Checklist Download': 20,
            'Scorecard Download': 25,
            'Webinar': 30
        }
        
        lead_source = lead_data.get('lead_source', '')
        if lead_source in source_scores:
            source_score = source_scores[lead_source]
            score += source_score
            details.append(f"Source ({lead_source}): +{source_score}")
        
        # Industry scoring (DACH/APAC focus)
        industry_scores = {
            'Manufacturing': 30,
            'Automotive': 25,
            'Technology': 25,
            'Consulting': 20,
            'Financial Services': 15
        }
        
        industry = lead_data.get('industry', '')
        if industry in industry_scores:
            industry_score = industry_scores[industry]
            score += industry_score
            details.append(f"Industry ({industry}): +{industry_score}")
        
        # Region scoring (matching Gradion's target regions)
        region_scores = {
            'DACH': 35,  # Germany, Austria, Switzerland
            'APAC': 30,  # Asia Pacific
            'Vietnam': 40,  # Home market
            'EU': 25,
            'US': 15
        }
        
        region = lead_data.get('region', '')
        if region in region_scores:
            region_score = region_scores[region]
            score += region_score
            details.append(f"Region ({region}): +{region_score}")
        
        # Company size scoring
        company_size = lead_data.get('company_size', 0)
        if company_size >= 1000:
            score += 30
            details.append("Large Enterprise: +30")
        elif company_size >= 250:
            score += 25
            details.append("Mid-Market: +25")
        elif company_size >= 50:
            score += 20
            details.append("SMB: +20")
        else:
            score += 10
            details.append("Small Business: +10")
        
        # Role scoring (Decision Maker focus)
        role_scores = {
            'CEO': 35,
            'CTO': 30,
            'VP Engineering': 30,
            'Head of Operations': 25,
            'Director': 25,
            'Manager': 20,
            'Senior': 15,
            'Junior': 5
        }
        
        role = lead_data.get('decision_maker_role', '')
        for role_key, role_score in role_scores.items():
            if role_key.lower() in role.lower():
                score += role_score
                details.append(f"Role ({role_key}): +{role_score}")
                break
        
        # Behavioral scoring (HubSpot activities)
        activities = lead_data.get('activities', [])
        for activity in activities:
            activity_type = activity.get('type', '')
            if activity_type == 'whitepaper_download':
                score += 15
                details.append("Whitepaper Download: +15")
            elif activity_type == 'webinar_attend':
                score += 20
                details.append("Webinar Attendance: +20")
            elif activity_type == 'email_open':
                score += 2
                details.append("Email Open: +2")
            elif activity_type == 'email_click':
                score += 5
                details.append("Email Click: +5")
            elif activity_type == 'website_visit':
                score += 3
                details.append("Website Visit: +3")
        
        # Book Consultant override (critical for Gradion)
        book_consultant = lead_data.get('book_consultant', False)
        if book_consultant:
            score = max(score, self.sql_threshold)
            details.append("Book Consultant = TRUE: SQL Override")
        
        # Determine stage
        if score >= self.sql_threshold or book_consultant:
            stage = 'SQL'
            action = 'Assign to Sales (Round Robin by Region)'
        elif score >= self.mql_threshold:
            stage = 'MQL'
            action = 'Sales follow-up within 1 day'
        else:
            stage = 'Lead'
            action = 'Continue nurturing campaign'
        
        return {
            'lead_score': score,
            'stage': stage,
            'action': action,
            'scoring_details': details,
            'book_consultant_override': book_consultant
        }

class VietnamChurnPredictor:
    """
    Enhanced churn prediction focusing on Vietnamese customer success metrics
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_columns = [
            'nps_score', 'support_tickets', 'product_usage_hours',
            'renewal_months_remaining', 'expansion_flag', 'cs_touch_frequency'
        ]
        
    def predict_churn_risk(self, customer_data: Dict) -> Dict:
        """Enhanced churn prediction with CS intervention triggers"""
        
        # Extract Vietnamese-specific risk factors
        risk_factors = []
        risk_score = 0.0
        
        # NPS-based risk (critical for Vietnamese market)
        nps_score = customer_data.get('nps_score', 5)
        if nps_score <= 3:
            risk_score += 0.4
            risk_factors.append("Low NPS Score (Detractor)")
        elif nps_score <= 6:
            risk_score += 0.2
            risk_factors.append("Neutral NPS Score")
        
        # Support ticket volume (Vietnamese customers expect high touch)
        ticket_count = customer_data.get('support_tickets', 0)
        if ticket_count > 10:  # Last 30 days
            risk_score += 0.3
            risk_factors.append("High support ticket volume")
        
        # Product usage patterns
        usage_hours = customer_data.get('product_usage_hours', 0)
        if usage_hours < 10:  # Monthly threshold
            risk_score += 0.25
            risk_factors.append("Low product engagement")
        
        # Renewal timeline risk
        renewal_months = customer_data.get('renewal_months_remaining', 12)
        if renewal_months <= 2:
            risk_score += 0.2
            risk_factors.append("Approaching renewal")
        
        # CS touch frequency (important in Vietnamese business culture)
        cs_touches = customer_data.get('cs_touch_frequency', 4)  # Per quarter
        if cs_touches < 2:
            risk_score += 0.15
            risk_factors.append("Insufficient Customer Success touchpoints")
        
        # Calculate final risk level
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.7:
            risk_level = "Critical"
            cs_action = "Immediate Account Manager call + Executive escalation"
        elif risk_score >= 0.5:
            risk_level = "High"
            cs_action = "Schedule Customer Success call within 48h"
        elif risk_score >= 0.3:
            risk_level = "Medium"
            cs_action = "Increase touchpoint frequency + Usage review"
        else:
            risk_level = "Low"
            cs_action = "Continue standard CS cadence"
        
        return {
            'churn_probability': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'cs_action': cs_action,
            'recommended_interventions': self._get_intervention_strategy(risk_factors)
        }
    
    def _get_intervention_strategy(self, risk_factors: List[str]) -> List[str]:
        """Vietnamese-specific intervention strategies"""
        interventions = []
        
        if "Low NPS Score" in ' '.join(risk_factors):
            interventions.append("Conduct detailed satisfaction survey in Vietnamese")
            interventions.append("Arrange face-to-face meeting if in Vietnam")
        
        if "High support ticket volume" in ' '.join(risk_factors):
            interventions.append("Assign dedicated technical consultant")
            interventions.append("Provide additional training sessions")
        
        if "Low product engagement" in ' '.join(risk_factors):
            interventions.append("Schedule product usage optimization session")
            interventions.append("Provide Vietnamese language training materials")
        
        if "Approaching renewal" in ' '.join(risk_factors):
            interventions.append("Early renewal discussion with added value")
            interventions.append("Present expansion opportunities")
        
        return interventions

class ExpansionRevenuePredictor:
    """
    Predict upsell/cross-sell opportunities based on Vietnamese customer patterns
    """
    
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
    def predict_expansion_opportunity(self, customer_data: Dict) -> Dict:
        """Predict expansion revenue potential"""
        
        base_acv = customer_data.get('acv_usd', 50000)
        expansion_score = 0.0
        opportunities = []
        
        # Success indicators for expansion
        nps_score = customer_data.get('nps_score', 5)
        if nps_score >= 8:  # Promoters
            expansion_score += 0.3
            opportunities.append("High satisfaction - Ready for upsell discussion")
        
        # Usage patterns
        usage_trend = customer_data.get('usage_trend', 'stable')  # growing, stable, declining
        if usage_trend == 'growing':
            expansion_score += 0.25
            opportunities.append("Growing usage - Suggest higher tier package")
        
        # Contract maturity
        contract_months = customer_data.get('contract_months_active', 6)
        if contract_months >= 6:  # Stable customer
            expansion_score += 0.2
            opportunities.append("Established customer - Cross-sell ready")
        
        # Industry-specific opportunities
        industry = customer_data.get('industry', '')
        if industry in ['Manufacturing', 'Automotive']:
            expansion_score += 0.15
            opportunities.append("Industry fit for advanced consulting packages")
        
        # Predicted expansion revenue
        expansion_multiplier = 1 + (expansion_score * 1.5)  # Up to 150% increase
        predicted_expansion = base_acv * (expansion_multiplier - 1)
        
        return {
            'expansion_probability': expansion_score,
            'predicted_expansion_revenue': predicted_expansion,
            'opportunities': opportunities,
            'recommended_packages': self._get_package_recommendations(customer_data),
            'optimal_timing': self._get_optimal_timing(customer_data)
        }
    
    def _get_package_recommendations(self, customer_data: Dict) -> List[str]:
        """Vietnamese market-specific package recommendations"""
        packages = []
        
        industry = customer_data.get('industry', '')
        current_acv = customer_data.get('acv_usd', 50000)
        
        if industry == 'Manufacturing':
            if current_acv < 100000:
                packages.append("Manufacturing Automation Consulting (+$50K)")
                packages.append("Process Optimization Package (+$30K)")
        
        if industry == 'Technology':
            packages.append("Digital Transformation Roadmap (+$40K)")
            packages.append("Agile Implementation Services (+$25K)")
        
        # General expansions
        packages.append("Training & Certification Program (+$15K)")
        packages.append("Dedicated Account Management (+$20K)")
        
        return packages
    
    def _get_optimal_timing(self, customer_data: Dict) -> str:
        """Determine optimal timing for expansion discussions"""
        
        contract_months = customer_data.get('contract_months_active', 6)
        renewal_months = customer_data.get('renewal_months_remaining', 12)
        nps_score = customer_data.get('nps_score', 5)
        
        if nps_score >= 8 and contract_months >= 3:
            return "Immediate - High satisfaction window"
        elif renewal_months <= 4:
            return "During renewal negotiations"
        elif contract_months >= 6:
            return "Mid-contract review period"
        else:
            return "Wait for 6-month milestone"

class RegionAssignmentEngine:
    """
    Round Robin assignment logic matching Gradion's regional structure
    """
    
    def __init__(self):
        self.sales_reps = {
            'DACH': ['Hans Mueller', 'Anna Schmidt', 'Klaus Weber'],
            'APAC': ['Nguyen Van A', 'Li Wei', 'Tanaka San'],
            'Vietnam': ['Tran Duc B', 'Le Thi C', 'Pham Van D'],
            'EU': ['Pierre Dubois', 'Marco Rossi'],
            'US': ['John Smith', 'Sarah Johnson']
        }
        self.current_assignment = {region: 0 for region in self.sales_reps.keys()}
    
    def assign_sql_lead(self, lead_data: Dict) -> Dict:
        """Assign SQL lead using Round Robin by region"""
        
        region = lead_data.get('region', 'EU')  # Default to EU
        
        if region not in self.sales_reps:
            region = 'EU'  # Fallback
        
        # Round Robin assignment
        reps = self.sales_reps[region]
        current_index = self.current_assignment[region]
        assigned_rep = reps[current_index % len(reps)]
        
        # Update for next assignment
        self.current_assignment[region] = (current_index + 1) % len(reps)
        
        # Calculate expected follow-up time (1 business day per Gradion workflow)
        follow_up_sla = "1 business day"
        
        return {
            'assigned_sales_rep': assigned_rep,
            'region': region,
            'follow_up_sla': follow_up_sla,
            'assignment_time': datetime.now().isoformat(),
            'auto_email_sent': True,
            'booking_confirmation': lead_data.get('book_consultant', False)
        }

# Usage example for testing
if __name__ == "__main__":
    # Test Vietnamese lead scoring
    scorer = GradionLeadScorer()
    
    sample_lead = {
        'lead_source': 'LinkedIn Ads',
        'industry': 'Manufacturing',
        'region': 'DACH',
        'company_size': 500,
        'decision_maker_role': 'CTO',
        'book_consultant': False,
        'activities': [
            {'type': 'whitepaper_download'},
            {'type': 'webinar_attend'},
            {'type': 'email_open'},
            {'type': 'website_visit'}
        ]
    }
    
    result = scorer.calculate_vietnam_lead_score(sample_lead)
    print("Lead Scoring Result:")
    print(f"Score: {result['lead_score']}")
    print(f"Stage: {result['stage']}")
    print(f"Action: {result['action']}")
    print("Details:", result['scoring_details'])