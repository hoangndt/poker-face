import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LeadQualificationAgent:
    """
    Real AI Agent for analyzing leads using OpenAI LLM.
    Provides intelligent qualification recommendations while maintaining
    the same output structure as the previous rule-based system.
    """
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.fallback_enabled = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Fallback rule-based system for when AI is unavailable
        self.fallback_criteria = {
            'budget': {
                'weight': 0.25,
                'indicators': ['budget_range', 'estimated_value', 'financial_authority'],
                'questions': [
                    "What budget range have you allocated for this project?",
                    "Who has the authority to approve this investment?",
                    "When do you plan to make this investment?"
                ]
            },
            'authority': {
                'weight': 0.20,
                'indicators': ['decision_makers', 'decision_maker_role', 'stakeholders'],
                'questions': [
                    "Who else will be involved in the decision-making process?",
                    "What is your role in the purchasing decision?",
                    "Who would need to sign off on this project?"
                ]
            },
            'need': {
                'weight': 0.25,
                'indicators': ['pain_points', 'business_goals', 'current_solutions'],
                'questions': [
                    "What specific challenges are you trying to solve?",
                    "How are you currently handling this process?",
                    "What would success look like for your organization?"
                ]
            },
            'timeline': {
                'weight': 0.15,
                'indicators': ['project_timeline', 'urgency_level', 'expected_close_date'],
                'questions': [
                    "When do you need this solution implemented?",
                    "What's driving the timeline for this project?",
                    "Are there any specific deadlines we should be aware of?"
                ]
            },
            'fit': {
                'weight': 0.15,
                'indicators': ['tech_preferences', 'team_size', 'compliance_requirements'],
                'questions': [
                    "Do you have any specific technology preferences?",
                    "What compliance requirements do we need to consider?",
                    "How large is your team that would use this solution?"
                ]
            }
        }

    def analyze_lead(self, customer_data: Dict, conversation_data: Dict) -> Dict[str, Any]:
        """
        Analyze a lead using AI and provide qualification insights.
        Falls back to rule-based system if AI is unavailable.
        
        Args:
            customer_data: Basic customer information from CRM
            conversation_data: Conversation history and requirements
            
        Returns:
            Dictionary with qualification score, missing information, and recommendations
        """
        
        try:
            # Try AI analysis first
            return self._ai_analyze_lead(customer_data, conversation_data)
        except Exception as e:
            print(f"AI analysis failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based analysis")
                return self._fallback_analyze_lead(customer_data, conversation_data)
            else:
                raise e

    def _ai_analyze_lead(self, customer_data: Dict, conversation_data: Dict) -> Dict[str, Any]:
        """Use OpenAI to analyze the lead and generate insights."""
        
        # Prepare the prompt with customer and conversation data
        prompt = self._build_analysis_prompt(customer_data, conversation_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, customer_data, conversation_data)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role and output format."""
        return """
You are an expert B2B sales qualification analyst. Your job is to analyze lead data and provide structured insights to help sales teams qualify prospects effectively.

You must ALWAYS respond with a valid JSON object containing exactly these fields:
{
    "qualification_score": <number 0-100>,
    "qualification_level": "<string: 'Cold', 'Warm', 'Hot', or 'Qualified'>",
    "missing_information": [<array of strings>],
    "suggested_questions": [<array of strings>],
    "next_steps": [<array of strings>],
    "recommendations": [<array of strings>],
    "confidence": <number 0-100>,
    "reasoning": "<string explaining your analysis>"
}

QUALIFICATION CRITERIA (use these to calculate the score):
- Budget (25%): Do they have budget allocated and financial authority?
- Authority (20%): Are we talking to decision makers or influencers?
- Need (25%): Do they have clear business pain points and requirements?
- Timeline (15%): Is there urgency and a clear implementation timeline?
- Fit (15%): Does their technical/business context fit our solutions?

QUALIFICATION LEVELS:
- Cold (0-25%): Very early stage, minimal information
- Warm (26-50%): Some qualification criteria met, needs more discovery
- Hot (51-75%): Most criteria met, ready for proposal discussion
- Qualified (76-100%): All criteria met, ready to close

MISSING INFORMATION should be simple labels like: "budget", "authority", "timeline", "need", "fit"

SUGGESTED QUESTIONS should be specific, actionable questions the sales team can ask.

NEXT STEPS should be concrete actions like "Budget Discussion", "Stakeholder Meeting", "Technical Demo", etc.

RECOMMENDATIONS should be strategic advice and high-level recommendations for this lead.

Be concise but insightful. Focus on actionable sales advice.
"""

    def _build_analysis_prompt(self, customer_data: Dict, conversation_data: Dict) -> str:
        """Build the analysis prompt with customer and conversation data."""
        
        prompt = "Analyze this B2B sales lead and provide qualification insights:\n\n"
        
        # Customer Information
        prompt += "CUSTOMER DATA:\n"
        for key, value in customer_data.items():
            if value:
                prompt += f"- {key}: {value}\n"
        
        # Conversation Information
        prompt += "\nCONVERSATION DATA:\n"
        for key, value in conversation_data.items():
            if value:
                prompt += f"- {key}: {value}\n"
        
        prompt += "\nProvide your analysis as a JSON object following the exact format specified in the system prompt."
        
        return prompt

    def _parse_ai_response(self, ai_response: str, customer_data: Dict, conversation_data: Dict) -> Dict[str, Any]:
        """Parse the AI response and ensure it matches our expected format."""
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_response = json.loads(json_str)
            else:
                # If no JSON found, try parsing the entire response
                parsed_response = json.loads(ai_response)
            
            # Validate and standardize the response format
            return self._standardize_response(parsed_response)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"AI Response: {ai_response}")
            # Fall back to rule-based analysis if JSON parsing fails
            if self.fallback_enabled:
                return self._fallback_analyze_lead(customer_data, conversation_data)
            else:
                raise e

    def _standardize_response(self, parsed_response: Dict) -> Dict[str, Any]:
        """Ensure the AI response matches our expected format exactly."""
        
        # Ensure all required fields are present with defaults
        standardized = {
            'qualification_score': float(parsed_response.get('qualification_score', 0)),
            'qualification_level': parsed_response.get('qualification_level', 'Cold'),
            'missing_information': parsed_response.get('missing_information', []),
            'suggested_questions': parsed_response.get('suggested_questions', []),
            'next_steps': parsed_response.get('next_steps', []),
            'recommendations': parsed_response.get('recommendations', []),
            'confidence': float(parsed_response.get('confidence', 50)),
            'deal_id': parsed_response.get('deal_id'),  # This will be set by the API
        }
        
        # Ensure values are within valid ranges
        standardized['qualification_score'] = max(0, min(100, standardized['qualification_score']))
        standardized['confidence'] = max(0, min(100, standardized['confidence']))
        
        # Ensure qualification level is valid
        valid_levels = ['Cold', 'Warm', 'Hot', 'Qualified']
        if standardized['qualification_level'] not in valid_levels:
            # Map score to level if invalid
            score = standardized['qualification_score']
            if score >= 76:
                standardized['qualification_level'] = 'Qualified'
            elif score >= 51:
                standardized['qualification_level'] = 'Hot'
            elif score >= 26:
                standardized['qualification_level'] = 'Warm'
            else:
                standardized['qualification_level'] = 'Cold'
        return standardized

    def _fallback_analyze_lead(self, customer_data: Dict, conversation_data: Dict) -> Dict[str, Any]:
        """Fallback rule-based analysis when AI is unavailable."""
        
        # Calculate qualification score using simple rules
        qualification_score = self._fallback_calculate_score(customer_data, conversation_data)
        
        # Identify missing information
        missing_info = self._fallback_identify_missing(customer_data, conversation_data)
        
        # Generate basic questions
        suggested_questions = self._fallback_generate_questions(missing_info)
        
        # Determine next steps
        next_steps = self._fallback_next_steps(qualification_score, missing_info)
        
        # Generate basic recommendations
        recommendations = self._fallback_generate_recommendations(qualification_score, missing_info)
        
        # Map score to qualification level
        if qualification_score >= 76:
            qualification_level = 'Qualified'
        elif qualification_score >= 51:
            qualification_level = 'Hot'
        elif qualification_score >= 26:
            qualification_level = 'Warm'
        else:
            qualification_level = 'Cold'
        
        return {
            'qualification_score': qualification_score,
            'qualification_level': qualification_level,
            'missing_information': missing_info,
            'suggested_questions': suggested_questions,
            'next_steps': next_steps,
            'recommendations': recommendations,
            'confidence': 70.0  # Fixed confidence for rule-based system
        }

    def _fallback_calculate_score(self, customer_data: Dict, conversation_data: Dict) -> float:
        """Simple rule-based scoring for fallback."""
        score = 0.0
        
        # Check budget information (25 points)
        if (customer_data.get('budget_range_min') and customer_data.get('budget_range_max')) or customer_data.get('estimated_value'):
            score += 25
        
        # Check authority/decision makers (20 points)
        if conversation_data.get('decision_makers') or customer_data.get('Decision_Maker_Role'):
            score += 20
        
        # Check need/requirements (25 points)
        if conversation_data.get('business_goals') or conversation_data.get('pain_points') or conversation_data.get('customer_requirements'):
            score += 25
        
        # Check timeline (15 points)
        if conversation_data.get('project_timeline') or conversation_data.get('urgency_level'):
            score += 15
        
        # Check fit/tech preferences (15 points)
        if conversation_data.get('tech_preferences') or conversation_data.get('team_size'):
            score += 15
        
        return float(score)

    def _fallback_identify_missing(self, customer_data: Dict, conversation_data: Dict) -> List[str]:
        """Identify missing information using simple rules."""
        missing = []
        
        # Check for missing budget info
        if not ((customer_data.get('budget_range_min') and customer_data.get('budget_range_max')) or customer_data.get('estimated_value')):
            missing.append('budget')
        
        # Check for missing authority info
        if not (conversation_data.get('decision_makers') or customer_data.get('Decision_Maker_Role')):
            missing.append('authority')
        
        # Check for missing need info
        if not (conversation_data.get('business_goals') or conversation_data.get('pain_points')):
            missing.append('need')
        
        # Check for missing timeline
        if not (conversation_data.get('project_timeline') or conversation_data.get('urgency_level')):
            missing.append('timeline')
        
        # Check for missing fit info
        if not (conversation_data.get('tech_preferences') or conversation_data.get('team_size')):
            missing.append('fit')
        
        return missing

    def _fallback_generate_questions(self, missing_info: List[str]) -> List[str]:
        """Generate basic questions for missing information."""
        questions = []
        
        question_map = {
            'budget': "What budget range have you allocated for this project?",
            'authority': "Who has the authority to approve this investment?",
            'need': "What specific challenges are you trying to solve?",
            'timeline': "When do you need this solution implemented?",
            'fit': "Do you have any specific technology preferences?"
        }
        
        for missing in missing_info[:3]:  # Limit to top 3
            if missing in question_map:
                questions.append(question_map[missing])
        
        return questions

    def _fallback_next_steps(self, score: float, missing_info: List[str]) -> List[str]:
        """Determine next steps based on score and missing info."""
        steps = []
        
        if 'budget' in missing_info:
            steps.append('Budget Discussion')
        
        if 'authority' in missing_info:
            steps.append('Stakeholder Meeting')
        
        if score >= 50:
            steps.append('Technical Demo')
        
        if score >= 75:
            steps.append('Proposal Preparation')
        
        return steps[:3]  # Limit to 3 steps
    
    def _fallback_generate_recommendations(self, score: float, missing_info: List[str]) -> List[str]:
        """Generate basic recommendations for fallback rule-based system."""
        recommendations = []
        
        if score < 40:
            recommendations.append("Focus on discovery and qualification before moving forward")
            recommendations.append("Schedule comprehensive discovery call")
        elif score >= 60:
            recommendations.append("Well-qualified lead - move to solution presentation")
            recommendations.append("Prepare customized demo")
        else:
            recommendations.append("Continue qualification process")
            recommendations.append("Address missing information areas")
        
        # Add specific recommendations based on missing info
        if 'budget' in missing_info:
            recommendations.append("Priority: Establish budget and financial authority")
        if 'authority' in missing_info:
            recommendations.append("Priority: Identify key decision-makers")
        if 'need' in missing_info:
            recommendations.append("Priority: Understand business requirements")
            
        return recommendations[:4]  # Limit to 4 recommendations

    def _has_information(self, indicator: str, customer_data: Dict, conversation_data: Dict) -> bool:
        """Check if we have meaningful information for a specific indicator."""
        
        # Check customer data
        if indicator in customer_data and customer_data[indicator]:
            if isinstance(customer_data[indicator], str) and len(customer_data[indicator].strip()) > 0:
                return True
            elif isinstance(customer_data[indicator], (int, float)) and customer_data[indicator] > 0:
                return True
        
        # Check conversation data
        if indicator in conversation_data and conversation_data[indicator]:
            if isinstance(conversation_data[indicator], str) and len(conversation_data[indicator].strip()) > 0:
                return True
        
        # Check for related fields
        related_fields = {
            'budget_range': ['budget_range_min', 'budget_range_max', 'estimated_value'],
            'decision_makers': ['decision_makers', 'Decision_Maker_Role'],
            'pain_points': ['pain_points', 'business_goals', 'customer_requirements'],
            'timeline': ['project_timeline', 'expected_close_date', 'urgency_level'],
            'tech_preferences': ['tech_preferences', 'integration_needs']
        }
        
        if indicator in related_fields:
            for field in related_fields[indicator]:
                if self._has_information(field, customer_data, conversation_data):
                    return True
        
        return False

    def _identify_missing_information(self, customer_data: Dict, conversation_data: Dict) -> List[Dict[str, str]]:
        """Identify critical missing information for qualification."""
        missing_info = []
        
        for criteria, config in self.qualification_criteria.items():
            missing_indicators = []
            
            for indicator in config['indicators']:
                if not self._has_information(indicator, customer_data, conversation_data):
                    missing_indicators.append(indicator)
            
            if missing_indicators:
                missing_info.append({
                    'category': criteria,
                    'missing_fields': missing_indicators,
                    'importance': config['weight'],
                    'description': self._get_category_description(criteria)
                })
        
        # Sort by importance
        missing_info.sort(key=lambda x: x['importance'], reverse=True)
        
        return missing_info

    def _get_category_description(self, category: str) -> str:
        """Get human-readable description for qualification categories."""
        descriptions = {
            'budget': 'Financial capacity and budget allocation',
            'authority': 'Decision-making power and stakeholder identification',
            'need': 'Business requirements and pain points',
            'timeline': 'Project timeline and urgency',
            'fit': 'Technical fit and requirements compatibility'
        }
        return descriptions.get(category, category)

    def _generate_suggested_questions(self, missing_info: List[Dict], customer_data: Dict) -> List[Dict[str, str]]:
        """Generate specific questions to address missing information."""
        questions = []
        
        for missing_category in missing_info[:3]:  # Focus on top 3 missing areas
            category = missing_category['category']
            if category in self.qualification_criteria:
                category_questions = self.qualification_criteria[category]['questions']
                
                for question in category_questions:
                    questions.append({
                        'category': category,
                        'question': question,
                        'purpose': f"To better understand {self._get_category_description(category)}",
                        'priority': 'high' if missing_category['importance'] > 0.2 else 'medium'
                    })
        
        # Add industry-specific questions
        industry = customer_data.get('Industry')
        if industry and industry in self.industry_insights:
            industry_questions = self._get_industry_specific_questions(industry)
            questions.extend(industry_questions)
        
        return questions

    def _get_industry_specific_questions(self, industry: str) -> List[Dict[str, str]]:
        """Generate industry-specific qualification questions."""
        industry_data = self.industry_insights.get(industry, {})
        questions = []
        
        if 'common_pain_points' in industry_data:
            questions.append({
                'category': 'industry_specific',
                'question': f"Are you experiencing challenges with {', '.join(industry_data['common_pain_points'][:2])}?",
                'purpose': f"To identify common {industry} industry pain points",
                'priority': 'medium'
            })
        
        if 'compliance_focus' in industry_data:
            questions.append({
                'category': 'compliance',
                'question': f"What {industry_data['compliance_focus'][0]} requirements do we need to consider?",
                'purpose': f"To understand {industry} compliance needs",
                'priority': 'high'
            })
        
        return questions

    def _recommend_next_steps(self, qualification_score: float, missing_info: List[Dict], customer_data: Dict) -> List[Dict[str, str]]:
        """Recommend specific next steps based on qualification analysis."""
        next_steps = []
        
        if qualification_score < 30:
            next_steps.append({
                'action': 'Discovery Call',
                'description': 'Schedule a comprehensive discovery call to gather basic qualification information',
                'priority': 'high',
                'timeline': 'Within 1-2 days'
            })
        elif qualification_score < 60:
            next_steps.append({
                'action': 'Stakeholder Meeting',
                'description': 'Arrange a meeting with key stakeholders to address missing qualification criteria',
                'priority': 'high',
                'timeline': 'Within 1 week'
            })
        else:
            next_steps.append({
                'action': 'Technical Demo',
                'description': 'Prepare and schedule a technical demonstration focusing on their specific needs',
                'priority': 'medium',
                'timeline': 'Within 2 weeks'
            })
        
        # Add specific actions based on missing information
        for missing in missing_info[:2]:
            if missing['category'] == 'budget':
                next_steps.append({
                    'action': 'Budget Discussion',
                    'description': 'Have a direct conversation about budget range and financial authority',
                    'priority': 'high',
                    'timeline': 'Next conversation'
                })
            elif missing['category'] == 'authority':
                next_steps.append({
                    'action': 'Stakeholder Mapping',
                    'description': 'Identify and connect with all decision-makers and influencers',
                    'priority': 'high',
                    'timeline': 'Within 1 week'
                })
        
        return next_steps

    def _get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """Get industry-specific insights and recommendations."""
        if not industry or industry not in self.industry_insights:
            return {}
        
        industry_data = self.industry_insights[industry]
        return {
            'industry': industry,
            'common_challenges': industry_data.get('common_pain_points', []),
            'key_stakeholders': industry_data.get('key_stakeholders', []),
            'budget_timing': industry_data.get('budget_cycles', 'Unknown'),
            'compliance_considerations': industry_data.get('compliance_focus', []),
            'sales_strategy': self._get_industry_sales_strategy(industry)
        }

    def _get_industry_sales_strategy(self, industry: str) -> str:
        """Get recommended sales strategy for specific industry."""
        strategies = {
            'Manufacturing': 'Focus on operational efficiency, ROI, and compliance. Involve operations and quality teams early.',
            'Retail': 'Emphasize customer experience improvements and multi-location capabilities. Consider seasonal timing.',
            'Tech': 'Lead with technical capabilities, scalability, and integration ease. Involve engineering teams.',
            'Healthcare': 'Prioritize compliance, security, and workflow efficiency. Long sales cycles expected.'
        }
        return strategies.get(industry, 'Tailor approach based on specific industry needs and stakeholders.')

    def _assess_risks(self, customer_data: Dict, conversation_data: Dict) -> List[Dict[str, str]]:
        """Assess potential risks in the sales process."""
        risks = []
        
        # Budget risk
        if not self._has_information('budget_range', customer_data, conversation_data):
            risks.append({
                'type': 'Budget Risk',
                'description': 'No budget information available - may not be a qualified opportunity',
                'severity': 'high',
                'mitigation': 'Prioritize budget discovery in next conversation'
            })
        
        # Authority risk
        if not self._has_information('decision_makers', customer_data, conversation_data):
            risks.append({
                'type': 'Authority Risk',
                'description': 'Decision-makers not identified - may be speaking to wrong person',
                'severity': 'medium',
                'mitigation': 'Map out decision-making process and stakeholders'
            })
        
        # Timeline risk
        urgency = conversation_data.get('urgency_level', '').lower()
        if urgency in ['low', 'no urgency']:
            risks.append({
                'type': 'Timeline Risk',
                'description': 'Low urgency may indicate this is not a current priority',
                'severity': 'medium',
                'mitigation': 'Understand what would create urgency or timeline pressure'
            })
        
        # Competition risk
        current_solutions = conversation_data.get('current_solutions', '')
        if 'competitor' in current_solutions.lower() or 'vendor' in current_solutions.lower():
            risks.append({
                'type': 'Competition Risk',
                'description': 'May be evaluating multiple vendors',
                'severity': 'medium',
                'mitigation': 'Understand evaluation criteria and differentiate clearly'
            })
        
        return risks

    def _calculate_confidence(self, customer_data: Dict, conversation_data: Dict) -> float:
        """Calculate confidence level in the qualification assessment."""
        
        # Count available data points
        available_fields = 0
        total_fields = 0
        
        important_fields = [
            'customer_requirements', 'budget_range_min', 'decision_makers',
            'project_timeline', 'pain_points', 'business_goals'
        ]
        
        for field in important_fields:
            total_fields += 1
            if self._has_information(field, customer_data, conversation_data):
                available_fields += 1
        
        # Base confidence on data availability
        base_confidence = (available_fields / total_fields) * 100 if total_fields > 0 else 0
        
        # Adjust based on conversation quality
        conversation_quality = self._assess_conversation_quality(conversation_data)
        
        # Final confidence score
        confidence = (base_confidence * 0.7) + (conversation_quality * 0.3)
        
        return min(100, max(0, confidence))

    def _assess_conversation_quality(self, conversation_data: Dict) -> float:
        """Assess the quality and depth of conversation data."""
        quality_score = 0.0
        
        # Check for detailed responses
        text_fields = ['customer_requirements', 'pain_points', 'business_goals', 'sales_notes']
        for field in text_fields:
            value = conversation_data.get(field, '')
            if isinstance(value, str):
                # Score based on length and detail
                if len(value) > 100:
                    quality_score += 25
                elif len(value) > 50:
                    quality_score += 15
                elif len(value) > 10:
                    quality_score += 5
        
        return min(100, quality_score)

    def _get_qualification_level(self, score: float) -> str:
        """Convert qualification score to qualification level."""
        if score >= 80:
            return 'Highly Qualified'
        elif score >= 60:
            return 'Qualified'
        elif score >= 40:
            return 'Partially Qualified'
        elif score >= 20:
            return 'Low Qualification'
        else:
            return 'Unqualified'

    def _generate_recommendations(self, qualification_score: float, missing_info: List[Dict], customer_data: Dict) -> List[str]:
        """Generate actionable recommendations for the sales team."""
        recommendations = []
        
        if qualification_score < 40:
            recommendations.append("Focus on discovery - this lead needs more qualification before moving forward")
            recommendations.append("Schedule a dedicated discovery call to gather missing information")
        
        if qualification_score >= 60:
            recommendations.append("This is a well-qualified lead - consider moving to solution presentation phase")
            recommendations.append("Prepare a customized demo focusing on their specific requirements")
        
        # Specific recommendations based on missing info
        for missing in missing_info[:2]:
            category = missing['category']
            if category == 'budget':
                recommendations.append("Priority: Establish budget range and financial decision-making process")
            elif category == 'authority':
                recommendations.append("Priority: Identify and engage with key decision-makers")
            elif category == 'need':
                recommendations.append("Priority: Deepen understanding of business requirements and pain points")
        
        return recommendations