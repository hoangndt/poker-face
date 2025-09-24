import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score
from typing import List, Dict, Any
import joblib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ChurnPredictionResult:
    customer_id: str
    churn_probability: float
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]
    prediction_confidence: float

@dataclass
class CLVResult:
    estimated_value: float
    confidence: float
    contributing_factors: List[str]

class ChurnPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = {}
        self.is_trained = False
        
    def prepare_features(self, customers):
        """Prepare features for churn prediction"""
        features = []
        
        for customer in customers:
            feature_row = [
                customer.Customer_Tenure_Months or 0,
                customer.Logins_Per_Month or 0,
                customer.Active_Features_Used or 0,
                customer.Product_Usage_Hours or 0,
                customer.Tickets_Raised or 0,
                customer.Avg_Response_Time_Support or 0,
                customer.NPS_Score or 0,
                customer.Renewals_Count or 0,
                1 if customer.Expansion_Flag else 0,
                customer.ACV_USD or 0,
                customer.LTV_USD or 0,
                customer.Company_Size or 0
            ]
            features.append(feature_row)
            
        return np.array(features)
    
    def train(self, customers):
        """Train the churn prediction model"""
        if not customers:
            return
            
        X = self.prepare_features(customers)
        y = [1 if c.Churn_Flag else 0 for c in customers]
        
        if len(set(y)) < 2:  # Need both classes
            return
            
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Store feature importance
        feature_names = [
            'tenure_months', 'logins_per_month', 'active_features', 
            'usage_hours', 'tickets_raised', 'response_time', 
            'nps_score', 'renewals', 'expansion_flag', 'acv', 'ltv', 'company_size'
        ]
        
        self.feature_importance = dict(zip(
            feature_names, 
            self.model.feature_importances_
        ))
        
        self.is_trained = True
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Churn prediction model accuracy: {accuracy:.3f}")
    
    def predict(self, customer) -> ChurnPredictionResult:
        """Predict churn probability for a customer"""
        if not self.is_trained:
            return ChurnPredictionResult(
                customer_id=customer.Customer_ID or str(customer.id),
                churn_probability=0.5,
                risk_level="Unknown",
                risk_factors=["Model not trained"],
                recommendations=["Train the model with sufficient data"],
                prediction_confidence=0.0
            )
        
        # Prepare features
        features = self.prepare_features([customer])
        features_scaled = self.scaler.transform(features)
        
        # Predict
        churn_prob = self.model.predict_proba(features_scaled)[0][1]
        
        # Determine risk level
        if churn_prob < 0.3:
            risk_level = "Low"
        elif churn_prob < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(customer)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(customer, risk_factors)
        
        return ChurnPredictionResult(
            customer_id=customer.Customer_ID or str(customer.id),
            churn_probability=churn_prob,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            prediction_confidence=max(churn_prob, 1 - churn_prob)
        )
    
    def _identify_risk_factors(self, customer) -> List[str]:
        """Identify specific risk factors for a customer"""
        risk_factors = []
        
        if (customer.NPS_Score or 0) < 30:
            risk_factors.append("Low NPS Score")
        if (customer.Logins_Per_Month or 0) < 5:
            risk_factors.append("Low Login Frequency")
        if (customer.Active_Features_Used or 0) < 3:
            risk_factors.append("Limited Feature Usage")
        if (customer.Tickets_Raised or 0) > 10:
            risk_factors.append("High Support Ticket Volume")
        if (customer.Avg_Response_Time_Support or 0) > 24:
            risk_factors.append("Slow Support Response")
        if not customer.Expansion_Flag and (customer.Customer_Tenure_Months or 0) > 12:
            risk_factors.append("No Account Expansion")
            
        return risk_factors
    
    def _generate_recommendations(self, customer, risk_factors) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if "Low NPS Score" in risk_factors:
            recommendations.append("Schedule customer success call to address satisfaction")
        if "Low Login Frequency" in risk_factors:
            recommendations.append("Implement user engagement campaign")
        if "Limited Feature Usage" in risk_factors:
            recommendations.append("Provide feature training and onboarding")
        if "High Support Ticket Volume" in risk_factors:
            recommendations.append("Proactive account review and technical optimization")
        if "Slow Support Response" in risk_factors:
            recommendations.append("Prioritize support response for this customer")
        if "No Account Expansion" in risk_factors:
            recommendations.append("Present upselling and expansion opportunities")
            
        return recommendations

class RevenueForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_importance = {}

    def train(self, deals):
        """Train revenue forecasting model using Deal data"""
        if not deals:
            return

        # Prepare features from deals
        X, y = self._prepare_deal_features(deals)

        if len(X) < 10:  # Need sufficient data
            print(f"Not enough data for training: {len(X)} samples (need at least 10)")
            return

        X_scaled = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Store feature importance
        feature_names = [
            'estimated_value', 'deal_probability', 'velocity_encoded', 'stage_encoded',
            'days_since_creation', 'region_encoded', 'has_assigned_person', 'implementation_time_encoded'
        ]

        self.feature_importance = dict(zip(
            feature_names,
            self.model.feature_importances_
        ))

        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = np.mean((y_test - y_pred) ** 2)
        r2 = self.model.score(X_test, y_test)
        print(f"Revenue forecasting MSE: {mse:.2f}, R²: {r2:.3f}")

    def _prepare_deal_features(self, deals):
        """Prepare features for revenue forecasting from Deal objects"""
        X = []
        y = []

        # Create encoders for categorical variables
        velocities = ['Fast', 'Medium', 'Slow']
        stages = ['Lead', 'Qualification', 'Discovery', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
        regions = ['North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East & Africa']
        implementation_times = ['2-3 months', '3-4 months', '4-6 months', '6-8 months', '8-12 months', '12-18 months', '18-24 months', '2-3 years']

        for deal in deals:
            if deal.estimated_value and deal.deal_probability is not None:
                # Calculate days since creation
                if deal.created_at:
                    days_since_creation = (datetime.now() - deal.created_at).days
                else:
                    days_since_creation = 0

                # Encode categorical variables
                velocity_encoded = velocities.index(deal.velocity) if deal.velocity in velocities else 1  # Default to Medium
                stage_encoded = stages.index(deal.deal_stage) if deal.deal_stage in stages else 0  # Default to Lead
                region_encoded = regions.index(deal.region) if deal.region in regions else 0  # Default to North America
                implementation_time_encoded = implementation_times.index(deal.implementation_time) if deal.implementation_time in implementation_times else 2  # Default to 4-6 months

                features = [
                    deal.estimated_value,
                    deal.deal_probability / 100.0,  # Normalize to 0-1
                    velocity_encoded,
                    stage_encoded,
                    days_since_creation,
                    region_encoded,
                    1 if deal.assigned_person_id else 0,
                    implementation_time_encoded
                ]

                X.append(features)
                # Target is the weighted amount (estimated_value * probability)
                y.append(deal.estimated_value * (deal.deal_probability / 100.0))

        return np.array(X), np.array(y)
    
    def forecast(self, months_ahead: int, deals):
        """Generate revenue forecast based on current pipeline"""
        if not self.is_trained:
            # Fallback to simple calculation based on current pipeline
            return self._simple_pipeline_forecast(deals, months_ahead)

        # Get current pipeline deals (not closed)
        pipeline_deals = [d for d in deals if d.deal_stage not in ['Closed Won', 'Closed Lost']]

        if not pipeline_deals:
            return self._simple_pipeline_forecast(deals, months_ahead)

        # Prepare features for pipeline deals
        X_pipeline, _ = self._prepare_deal_features(pipeline_deals)

        if len(X_pipeline) == 0:
            return self._simple_pipeline_forecast(deals, months_ahead)

        # Scale features
        X_pipeline_scaled = self.scaler.transform(X_pipeline)

        # Predict weighted amounts for pipeline deals
        predicted_weighted_amounts = self.model.predict(X_pipeline_scaled)

        # Calculate monthly distribution based on expected close dates and deal velocity
        monthly_forecast = []
        total_predicted = 0

        for month in range(1, months_ahead + 1):
            month_revenue = 0
            current_date = datetime.now()
            target_date = current_date + timedelta(days=30 * month)

            for i, deal in enumerate(pipeline_deals):
                # Estimate probability of closing in this month based on deal characteristics
                close_probability = self._calculate_monthly_close_probability(deal, month, target_date)
                month_revenue += predicted_weighted_amounts[i] * close_probability

            monthly_forecast.append({
                "month": month,
                "predicted_revenue": month_revenue,
                "period": target_date.strftime("%Y-%m")
            })
            total_predicted += month_revenue

        # Calculate confidence intervals based on model performance
        confidence_factor = 0.15  # 15% confidence interval

        return {
            "forecast_period": f"{months_ahead} months",
            "predicted_revenue": total_predicted,
            "confidence_interval_lower": total_predicted * (1 - confidence_factor),
            "confidence_interval_upper": total_predicted * (1 + confidence_factor),
            "monthly_forecast": monthly_forecast,
            "pipeline_deals_count": len(pipeline_deals),
            "total_pipeline_value": sum(d.estimated_value for d in pipeline_deals if d.estimated_value),
            "feature_importance": self.feature_importance,
            "seasonality_factors": {
                "Q1": 0.9, "Q2": 1.1, "Q3": 0.95, "Q4": 1.15
            }
        }

    def _calculate_monthly_close_probability(self, deal, month, target_date):
        """Calculate probability of deal closing in a specific month"""
        # Base probability from deal probability
        base_prob = (deal.deal_probability or 0) / 100.0

        # Adjust based on deal velocity
        velocity_multiplier = {
            'Fast': 1.5,
            'Medium': 1.0,
            'Slow': 0.6
        }.get(deal.velocity, 1.0)

        # Adjust based on deal stage
        stage_multiplier = {
            'Lead': 0.1,
            'Qualification': 0.2,
            'Discovery': 0.3,
            'Proposal': 0.6,
            'Negotiation': 0.8,
            'Closed Won': 0.0,  # Already closed
            'Closed Lost': 0.0  # Already closed
        }.get(deal.deal_stage, 0.3)

        # Time decay - deals are more likely to close sooner
        time_decay = max(0.1, 1.0 - (month - 1) * 0.1)

        # Expected close date influence
        if deal.expected_close_date:
            days_to_expected = (deal.expected_close_date - datetime.now()).days
            expected_month = max(1, days_to_expected // 30)
            if month == expected_month:
                time_decay *= 2.0  # Higher probability in expected month

        return min(1.0, base_prob * velocity_multiplier * stage_multiplier * time_decay)

    def _simple_pipeline_forecast(self, deals, months_ahead):
        """Simple fallback forecast when model is not trained"""
        # Calculate current pipeline value
        pipeline_deals = [d for d in deals if d.deal_stage not in ['Closed Won', 'Closed Lost']]
        total_pipeline = sum(d.estimated_value * (d.deal_probability / 100.0) for d in pipeline_deals if d.estimated_value and d.deal_probability)

        # Historical monthly revenue from closed deals
        closed_deals = [d for d in deals if d.deal_stage == 'Closed Won' and d.actual_close_date]
        if closed_deals:
            # Calculate average monthly revenue from last 12 months
            recent_deals = [d for d in closed_deals if d.actual_close_date and (datetime.now() - d.actual_close_date).days <= 365]
            monthly_avg = sum(d.estimated_value for d in recent_deals if d.estimated_value) / 12 if recent_deals else 0
        else:
            monthly_avg = total_pipeline / (months_ahead * 4)  # Assume 25% conversion per month

        # Simple growth assumption
        growth_rate = 0.02  # 2% monthly growth

        monthly_forecast = []
        total_predicted = 0

        for month in range(1, months_ahead + 1):
            predicted = monthly_avg * (1 + growth_rate) ** month
            monthly_forecast.append({
                "month": month,
                "predicted_revenue": predicted,
                "period": (datetime.now() + timedelta(days=30*month)).strftime("%Y-%m")
            })
            total_predicted += predicted

        return {
            "forecast_period": f"{months_ahead} months",
            "predicted_revenue": total_predicted,
            "confidence_interval_lower": total_predicted * 0.7,
            "confidence_interval_upper": total_predicted * 1.3,
            "monthly_forecast": monthly_forecast,
            "pipeline_deals_count": len(pipeline_deals),
            "total_pipeline_value": sum(d.estimated_value for d in pipeline_deals if d.estimated_value),
            "model_status": "untrained",
            "seasonality_factors": {
                "Q1": 0.9, "Q2": 1.1, "Q3": 0.95, "Q4": 1.15
            }
        }

class LeadScorer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        
    def train(self, customers):
        """Train lead scoring model"""
        if not customers:
            return
            
        X, y = self._prepare_lead_features(customers)
        
        if len(X) < 10:
            return
            
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        print("Lead scoring model trained successfully")
    
    def _prepare_lead_features(self, customers):
        """Prepare features for lead scoring"""
        X = []
        y = []
        
        # Encode categorical variables
        industries = list(set([c.Industry for c in customers if c.Industry]))
        regions = list(set([c.Region for c in customers if c.Region]))
        sources = list(set([c.Lead_Source for c in customers if c.Lead_Source]))
        roles = list(set([c.Decision_Maker_Role for c in customers if c.Decision_Maker_Role]))
        
        for customer in customers:
            if customer.Lead_Score:
                features = [
                    customer.Company_Size or 0,
                    industries.index(customer.Industry) if customer.Industry in industries else 0,
                    regions.index(customer.Region) if customer.Region in regions else 0,
                    sources.index(customer.Lead_Source) if customer.Lead_Source in sources else 0,
                    roles.index(customer.Decision_Maker_Role) if customer.Decision_Maker_Role in roles else 0,
                    1 if customer.Customer_Flag else 0
                ]
                X.append(features)
                y.append(customer.Lead_Score)
                
        return np.array(X), np.array(y)
    
    def calculate_score(self, lead_data) -> float:
        """Calculate lead score"""
        if not self.is_trained:
            return 50.0  # Default score
        
        # This is a simplified scoring algorithm
        score = 0
        
        # Company size scoring
        company_size = lead_data.get('Company_Size', 0)
        if company_size > 1000:
            score += 30
        elif company_size > 100:
            score += 20
        else:
            score += 10
        
        # Industry scoring
        high_value_industries = ['Tech', 'Finance', 'Manufacturing']
        if lead_data.get('Industry') in high_value_industries:
            score += 25
        
        # Region scoring
        if lead_data.get('Region') in ['US', 'DACH']:
            score += 20
        
        # Role scoring
        if lead_data.get('Decision_Maker_Role') in ['CEO', 'CTO']:
            score += 25
        
        return min(score, 100)  # Cap at 100
    
    def get_recommendations(self, lead_data) -> List[str]:
        """Get recommendations for lead nurturing"""
        recommendations = []
        
        score = self.calculate_score(lead_data)
        
        if score >= 80:
            recommendations.append("High-priority lead - immediate sales follow-up")
            recommendations.append("Schedule demo with decision maker")
        elif score >= 60:
            recommendations.append("Medium-priority lead - nurture with targeted content")
            recommendations.append("Send industry-specific case studies")
        else:
            recommendations.append("Long-term nurturing required")
            recommendations.append("Add to marketing automation sequence")
            
        return recommendations

class CLVCalculator:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def train(self, customers):
        """Train CLV calculation model"""
        if not customers:
            return
            
        X, y = self._prepare_clv_features(customers)
        
        if len(X) < 10:
            return
            
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        print("CLV calculation model trained successfully")
    
    def _prepare_clv_features(self, customers):
        """Prepare features for CLV calculation"""
        X = []
        y = []
        
        for customer in customers:
            if customer.LTV_USD and customer.Customer_Flag:
                features = [
                    customer.ACV_USD or 0,
                    customer.Customer_Tenure_Months or 0,
                    customer.Renewals_Count or 0,
                    1 if customer.Expansion_Flag else 0,
                    customer.NPS_Score or 0,
                    customer.Company_Size or 0,
                    customer.Logins_Per_Month or 0
                ]
                X.append(features)
                y.append(customer.LTV_USD)
                
        return np.array(X), np.array(y)
    
    def calculate(self, customer) -> CLVResult:
        """Calculate Customer Lifetime Value"""
        if not self.is_trained or not customer.Customer_Flag:
            # Simple CLV calculation
            acv = customer.ACV_USD or 0
            tenure = customer.Customer_Tenure_Months or 12
            estimated_clv = acv * (tenure / 12) * 1.2  # Assuming 20% growth
            
            return CLVResult(
                estimated_value=estimated_clv,
                confidence=0.5,
                contributing_factors=["Basic calculation - insufficient training data"]
            )
        
        # Prepare features
        features = [[
            customer.ACV_USD or 0,
            customer.Customer_Tenure_Months or 0,
            customer.Renewals_Count or 0,
            1 if customer.Expansion_Flag else 0,
            customer.NPS_Score or 0,
            customer.Company_Size or 0,
            customer.Logins_Per_Month or 0
        ]]
        
        # Predict CLV
        predicted_clv = self.model.predict(features)[0]
        
        # Calculate confidence (simplified)
        confidence = 0.8 if customer.Customer_Tenure_Months > 6 else 0.6
        
        # Identify contributing factors
        factors = []
        if customer.Expansion_Flag:
            factors.append("Account expansion potential")
        if (customer.NPS_Score or 0) > 70:
            factors.append("High customer satisfaction")
        if (customer.Renewals_Count or 0) > 2:
            factors.append("Strong renewal history")
        if (customer.Logins_Per_Month or 0) > 20:
            factors.append("High product engagement")
            
        return CLVResult(
            estimated_value=predicted_clv,
            confidence=confidence,
            contributing_factors=factors
        )