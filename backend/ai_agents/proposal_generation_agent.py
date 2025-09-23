"""
AI Agent for Proposal Generation and Commercial Strategy

This agent analyzes qualified leads with technical solutions and delivery plans to generate
comprehensive commercial proposals including pricing, terms, and strategic recommendations.
"""

import os
import json
import re
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProposalGenerationAgent:
    """AI agent for generating comprehensive commercial proposals and CSO recommendations."""
    
    def __init__(self):
        """Initialize the Proposal Generation Agent with OpenAI client."""
        
        # OpenAI configuration
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.fallback_enabled = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Pricing models and commercial frameworks
        self.pricing_models = {
            'Fixed Price': {
                'description': 'Total project cost with defined scope and deliverables',
                'risk': 'Low client risk, high vendor risk',
                'suitable_for': ['Well-defined requirements', 'Short-term projects']
            },
            'Time & Materials': {
                'description': 'Hourly/daily rates with estimated effort',
                'risk': 'Higher client risk, lower vendor risk',
                'suitable_for': ['Evolving requirements', 'Long-term partnerships']
            },
            'Milestone-based': {
                'description': 'Payments tied to delivery milestones',
                'risk': 'Balanced risk sharing',
                'suitable_for': ['Phased delivery', 'Complex projects']
            },
            'Retainer': {
                'description': 'Monthly fee for ongoing services',
                'risk': 'Predictable costs and revenue',
                'suitable_for': ['Maintenance', 'Support services']
            },
            'Revenue Share': {
                'description': 'Partnership model with shared success',
                'risk': 'High mutual risk and reward',
                'suitable_for': ['Startups', 'Innovative projects']
            }
        }
        
        # Contract terms and conditions
        self.standard_terms = {
            'payment_terms': ['30 days', '45 days', '60 days'],
            'milestone_payments': ['25% upfront', '50% midway', '25% completion'],
            'ip_ownership': ['Client owns', 'Shared IP', 'Vendor retains tools'],
            'support_period': ['3 months', '6 months', '12 months'],
            'warranty_period': ['90 days', '6 months', '12 months']
        }
        
        # Industry-specific considerations
        self.industry_factors = {
            'Startup': {
                'pricing_adjustment': 0.8,  # 20% discount
                'payment_terms': 'Milestone-based with shorter cycles',
                'special_considerations': ['Equity options', 'Growth-based pricing']
            },
            'Enterprise': {
                'pricing_adjustment': 1.2,  # 20% premium
                'payment_terms': 'Standard enterprise terms',
                'special_considerations': ['Compliance requirements', 'SLA agreements']
            },
            'SME': {
                'pricing_adjustment': 1.0,  # Standard pricing
                'payment_terms': 'Flexible payment options',
                'special_considerations': ['Cost-conscious', 'Quick decision making']
            }
        }

    def analyze_proposal_requirements(self, customer_data: Dict, conversation_data: Dict, 
                                    solution_data: Dict = None, delivery_data: Dict = None) -> Dict[str, Any]:
        """
        Analyze all project data and generate comprehensive commercial proposal.
        
        Args:
            customer_data: Basic customer information from CRM
            conversation_data: Conversation history and business requirements
            solution_data: Technical solution design from solution stage
            delivery_data: Delivery plan and resource allocation from delivery stage
            
        Returns:
            Dictionary with commercial proposal and CSO recommendations
        """
        
        try:
            # Try AI analysis first
            return self._ai_analyze_proposal(customer_data, conversation_data, solution_data, delivery_data)
        except Exception as e:
            print(f"AI proposal analysis failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based proposal analysis")
                return self._fallback_analyze_proposal(customer_data, conversation_data, solution_data, delivery_data)
            else:
                raise e

    def _ai_analyze_proposal(self, customer_data: Dict, conversation_data: Dict, 
                           solution_data: Dict = None, delivery_data: Dict = None) -> Dict[str, Any]:
        """Use OpenAI to analyze requirements and generate commercial proposal."""
        
        # Prepare the prompt with all available data
        prompt = self._build_proposal_prompt(customer_data, conversation_data, solution_data, delivery_data)
        
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
                temperature=0.2,  # Low temperature for consistent business proposals
                max_tokens=3500   # More tokens for comprehensive proposals
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, customer_data, conversation_data, solution_data, delivery_data)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role and output format."""
        return """
You are an expert commercial strategist and proposal specialist. Your job is to analyze technical solutions and delivery plans to create compelling commercial proposals that win deals while maintaining profitability.

You must ALWAYS respond with a valid JSON object containing exactly these fields:
{
    "proposal_score": <number 0-100>,
    "pricing_model": "<string: recommended pricing approach>",
    "commercial_terms": {
        "total_investment": "<string: total project investment>",
        "payment_structure": [<array of payment milestone descriptions>],
        "payment_terms": "<string: payment terms>",
        "contract_duration": "<string: contract duration>",
        "support_included": "<string: included support description>"
    },
    "value_proposition": [<array of key value propositions>],
    "competitive_advantages": [<array of competitive differentiators>],
    "risk_assessment": {
        "client_risks": [<array of risks to client>],
        "vendor_risks": [<array of risks to vendor>],
        "mitigation_strategies": [<array of risk mitigation approaches>]
    },
    "proposal_sections": [
        {
            "section": "<string: section name>",
            "content": "<string: section content summary>",
            "priority": "<string: High/Medium/Low>"
        }
    ],
    "negotiation_strategy": [<array of negotiation recommendations>],
    "success_metrics": [<array of project success measurements>],
    "recommendations": [<array of strategic commercial recommendations>],
    "confidence": <number 0-100>,
    "reasoning": "<string explaining your commercial analysis>"
}

PROPOSAL SCORING CRITERIA (0-100):
- Deal Attractiveness (25%): How valuable is this deal for the business?
- Win Probability (25%): How likely are we to win this proposal?
- Profitability Potential (20%): How profitable is this engagement?
- Strategic Value (15%): How well does this align with business strategy?
- Risk Assessment (15%): How manageable are the associated risks?

PRICING MODELS:
- Fixed Price: Total project cost with defined scope (best for clear requirements)
- Time & Materials: Hourly/daily rates with estimated effort (best for evolving scope)
- Milestone-based: Payments tied to delivery milestones (balanced risk sharing)
- Retainer: Monthly fee for ongoing services (predictable recurring revenue)
- Revenue Share: Partnership model with shared success (startup/innovation projects)

VALUE PROPOSITION ELEMENTS:
- Business impact and ROI
- Technical expertise and innovation
- Delivery speed and efficiency
- Risk mitigation and reliability
- Long-term partnership value
- Industry-specific experience

COMPETITIVE ADVANTAGES:
- Technical capabilities and expertise
- Industry experience and case studies
- Delivery methodology and track record
- Team composition and seniority
- Technology partnerships and certifications
- Cost-effectiveness and value

PROPOSAL SECTIONS (prioritize based on client needs):
- Executive Summary: High-level overview and value proposition
- Understanding: Demonstration of requirements comprehension
- Solution Approach: Technical solution and methodology
- Team & Experience: Team composition and relevant experience
- Timeline & Milestones: Delivery plan and key milestones
- Investment & Terms: Commercial proposal and contract terms
- Case Studies: Relevant project examples and testimonials
- Appendices: Technical details and supporting documentation

NEGOTIATION STRATEGY should include:
- Key negotiation points and flexibility areas
- Minimum acceptable terms and walk-away points
- Value-add options and upselling opportunities
- Relationship building and long-term partnership elements

Focus on creating win-win proposals that demonstrate clear value while maintaining healthy margins.
"""

    def _build_proposal_prompt(self, customer_data: Dict, conversation_data: Dict, 
                             solution_data: Dict = None, delivery_data: Dict = None) -> str:
        """Build the proposal analysis prompt with all available project data."""
        
        prompt = "Create a comprehensive commercial proposal based on the following project information:\n\n"
        
        # Customer Information
        prompt += "CUSTOMER INFORMATION:\n"
        for key, value in customer_data.items():
            if value:
                prompt += f"- {key}: {value}\n"
        
        # Business Requirements
        prompt += "\nBUSINESS REQUIREMENTS:\n"
        for key, value in conversation_data.items():
            if value:
                prompt += f"- {key}: {value}\n"
        
        # Technical Solution
        if solution_data:
            prompt += "\nTECHNICAL SOLUTION:\n"
            for key, value in solution_data.items():
                if value and key != 'deal_id':
                    if isinstance(value, dict):
                        prompt += f"- {key}:\n"
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, list):
                                prompt += f"  * {sub_key}: {', '.join(map(str, sub_value))}\n"
                            else:
                                prompt += f"  * {sub_key}: {sub_value}\n"
                    elif isinstance(value, list):
                        prompt += f"- {key}: {', '.join(map(str, value))}\n"
                    else:
                        prompt += f"- {key}: {value}\n"
        
        # Delivery Plan
        if delivery_data:
            prompt += "\nDELIVERY PLAN:\n"
            for key, value in delivery_data.items():
                if value and key != 'deal_id':
                    if key == 'team_composition':
                        prompt += f"- {key}:\n"
                        for member in value:
                            prompt += f"  * {member.get('role', 'Unknown')}: {member.get('allocation', 0)*100}% allocation\n"
                    elif key == 'budget_estimate':
                        prompt += f"- {key}:\n"
                        for budget_key, budget_value in value.items():
                            prompt += f"  * {budget_key}: {budget_value}\n"
                    elif isinstance(value, list):
                        prompt += f"- {key}: {', '.join(map(str, value))}\n"
                    else:
                        prompt += f"- {key}: {value}\n"
        
        prompt += "\nPlease provide a comprehensive commercial proposal that maximizes win probability while maintaining profitability."
        
        return prompt

    def _parse_ai_response(self, ai_response: str, customer_data: Dict, conversation_data: Dict, 
                         solution_data: Dict = None, delivery_data: Dict = None) -> Dict[str, Any]:
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
                return self._fallback_analyze_proposal(customer_data, conversation_data, solution_data, delivery_data)
            else:
                raise e

    def _standardize_response(self, parsed_response: Dict) -> Dict[str, Any]:
        """Ensure the AI response matches our expected format exactly."""
        
        # Ensure all required fields are present with defaults
        standardized = {
            'proposal_score': float(parsed_response.get('proposal_score', 0)),
            'pricing_model': parsed_response.get('pricing_model', 'Fixed Price'),
            'commercial_terms': parsed_response.get('commercial_terms', {}),
            'value_proposition': parsed_response.get('value_proposition', []),
            'competitive_advantages': parsed_response.get('competitive_advantages', []),
            'risk_assessment': parsed_response.get('risk_assessment', {}),
            'proposal_sections': parsed_response.get('proposal_sections', []),
            'negotiation_strategy': parsed_response.get('negotiation_strategy', []),
            'success_metrics': parsed_response.get('success_metrics', []),
            'recommendations': parsed_response.get('recommendations', []),
            'confidence': float(parsed_response.get('confidence', 50)),
            'deal_id': parsed_response.get('deal_id'),  # This will be set by the API
        }
        
        # Ensure values are within valid ranges
        standardized['proposal_score'] = max(0, min(100, standardized['proposal_score']))
        standardized['confidence'] = max(0, min(100, standardized['confidence']))
        
        # Ensure commercial_terms has required structure
        if not isinstance(standardized['commercial_terms'], dict):
            standardized['commercial_terms'] = {}
        
        terms_defaults = {
            'total_investment': 'To be determined',
            'payment_structure': ['To be defined'],
            'payment_terms': '30 days',
            'contract_duration': '6-12 months',
            'support_included': '3 months post-launch support'
        }
        
        for key, default_value in terms_defaults.items():
            if key not in standardized['commercial_terms']:
                standardized['commercial_terms'][key] = default_value
        
        # Ensure risk_assessment has required structure
        if not isinstance(standardized['risk_assessment'], dict):
            standardized['risk_assessment'] = {}
        
        risk_defaults = {
            'client_risks': ['Standard project risks'],
            'vendor_risks': ['Standard delivery risks'],
            'mitigation_strategies': ['Regular communication and monitoring']
        }
        
        for key, default_value in risk_defaults.items():
            if key not in standardized['risk_assessment']:
                standardized['risk_assessment'][key] = default_value
        
        return standardized

    def _fallback_analyze_proposal(self, customer_data: Dict, conversation_data: Dict, 
                                 solution_data: Dict = None, delivery_data: Dict = None) -> Dict[str, Any]:
        """Fallback rule-based proposal analysis when AI is unavailable."""
        
        # Calculate proposal score
        proposal_score = self._fallback_calculate_score(customer_data, conversation_data, solution_data, delivery_data)
        
        # Determine pricing model
        pricing_model = self._fallback_pricing_model(customer_data, conversation_data, delivery_data)
        
        # Generate commercial terms
        commercial_terms = self._fallback_commercial_terms(customer_data, delivery_data, pricing_model)
        
        # Create value proposition
        value_proposition = self._fallback_value_proposition(solution_data, delivery_data)
        
        # Identify competitive advantages
        competitive_advantages = self._fallback_competitive_advantages(solution_data)
        
        # Assess risks
        risk_assessment = self._fallback_risk_assessment(customer_data, conversation_data, delivery_data)
        
        # Define proposal sections
        proposal_sections = self._fallback_proposal_sections(proposal_score)
        
        return {
            'proposal_score': proposal_score,
            'pricing_model': pricing_model,
            'commercial_terms': commercial_terms,
            'value_proposition': value_proposition,
            'competitive_advantages': competitive_advantages,
            'risk_assessment': risk_assessment,
            'proposal_sections': proposal_sections,
            'negotiation_strategy': self._fallback_negotiation_strategy(proposal_score),
            'success_metrics': self._fallback_success_metrics(conversation_data),
            'recommendations': self._fallback_generate_recommendations(proposal_score, pricing_model),
            'confidence': 70.0  # Fixed confidence for rule-based system
        }

    def _fallback_calculate_score(self, customer_data: Dict, conversation_data: Dict, 
                                solution_data: Dict = None, delivery_data: Dict = None) -> float:
        """Calculate proposal score based on deal attractiveness and win probability."""
        
        score = 0.0
        
        # Deal attractiveness (40 points)
        budget_min = customer_data.get('budget_range_min', 0)
        if budget_min > 100000:
            score += 20  # Large deal
        elif budget_min > 50000:
            score += 15  # Medium deal
        elif budget_min > 10000:
            score += 10  # Small deal
        else:
            score += 5   # Very small deal
        
        # Add points for urgency (higher urgency = more likely to buy)
        urgency = str(conversation_data.get('urgency_level', '')).lower()
        if urgency == 'high':
            score += 15
        elif urgency == 'medium':
            score += 10
        else:
            score += 5
        
        # Decision maker involvement
        if conversation_data.get('decision_makers'):
            score += 5
        
        # Win probability (35 points)
        # Requirements clarity
        if conversation_data.get('customer_requirements') and len(str(conversation_data.get('customer_requirements', ''))) > 100:
            score += 10
        elif conversation_data.get('customer_requirements'):
            score += 5
        
        # Technical solution fit
        if solution_data and solution_data.get('solution_score', 0) > 70:
            score += 15
        elif solution_data and solution_data.get('solution_score', 0) > 50:
            score += 10
        else:
            score += 5
        
        # Delivery feasibility
        if delivery_data and delivery_data.get('delivery_score', 0) > 70:
            score += 10
        elif delivery_data:
            score += 5
        
        # Strategic value (15 points)
        industry = customer_data.get('Industry', '').lower()
        if any(keyword in industry for keyword in ['tech', 'software', 'saas']):
            score += 10  # Strategic industry alignment
        else:
            score += 5
        
        # Relationship potential
        if conversation_data.get('business_goals'):
            score += 5
        
        # Risk assessment (10 points)
        timeline = str(conversation_data.get('project_timeline', '')).lower()
        if any(word in timeline for word in ['month', 'quarter', 'year']):
            score += 10  # Reasonable timeline
        else:
            score += 5
        
        return min(100.0, score)

    def _fallback_pricing_model(self, customer_data: Dict, conversation_data: Dict, delivery_data: Dict = None) -> str:
        """Determine appropriate pricing model."""
        
        # Check budget size
        budget_min = customer_data.get('budget_range_min', 0)
        
        # Check requirements clarity
        requirements = str(conversation_data.get('customer_requirements', ''))
        
        # Check timeline
        urgency = str(conversation_data.get('urgency_level', '')).lower()
        
        if len(requirements) > 200 and budget_min > 50000:
            return 'Fixed Price'  # Well-defined, substantial project
        elif urgency == 'high' or 'asap' in requirements.lower():
            return 'Time & Materials'  # Fast delivery needed
        elif delivery_data and len(delivery_data.get('project_phases', [])) > 3:
            return 'Milestone-based'  # Complex multi-phase project
        elif 'ongoing' in requirements.lower() or 'maintenance' in requirements.lower():
            return 'Retainer'  # Ongoing services
        else:
            return 'Fixed Price'  # Default safe option

    def _fallback_commercial_terms(self, customer_data: Dict, delivery_data: Dict = None, pricing_model: str = None) -> Dict[str, Any]:
        """Generate commercial terms based on budget and delivery plan."""
        
        budget_min = customer_data.get('budget_range_min', 0)
        budget_max = customer_data.get('budget_range_max', 0)
        
        # Estimate total investment
        if delivery_data and delivery_data.get('budget_estimate'):
            total_investment = delivery_data['budget_estimate'].get('total_estimate', 'To be determined')
        elif budget_min and budget_max:
            total_investment = f"${budget_min:,} - ${budget_max:,}"
        elif budget_min:
            total_investment = f"${budget_min:,} - ${int(budget_min * 1.5):,}"
        else:
            total_investment = "To be determined based on final scope"
        
        # Payment structure based on pricing model
        if pricing_model == 'Milestone-based':
            payment_structure = [
                "25% upon contract signing",
                "50% upon completion of development milestones",
                "25% upon project completion and acceptance"
            ]
        elif pricing_model == 'Time & Materials':
            payment_structure = [
                "Monthly billing based on actual hours worked",
                "2-week payment terms",
                "Monthly expense reimbursement"
            ]
        elif pricing_model == 'Retainer':
            payment_structure = [
                "Monthly retainer fee in advance",
                "Quarterly true-up based on usage",
                "Annual contract with monthly billing"
            ]
        else:  # Fixed Price
            payment_structure = [
                "30% upon contract signing",
                "40% at project milestone completion",
                "30% upon final delivery and acceptance"
            ]
        
        # Timeline-based terms
        timeline = delivery_data.get('resource_timeline', '3-6 months') if delivery_data else '3-6 months'
        
        return {
            'total_investment': total_investment,
            'payment_structure': payment_structure,
            'payment_terms': '30 days',
            'contract_duration': timeline,
            'support_included': '3 months post-launch support included'
        }

    def _fallback_value_proposition(self, solution_data: Dict = None, delivery_data: Dict = None) -> List[str]:
        """Generate value propositions based on solution and delivery."""
        
        value_props = [
            "Experienced team with proven track record in similar projects",
            "Comprehensive solution addressing all identified business needs"
        ]
        
        if solution_data:
            solution_type = solution_data.get('solution_type', 'Custom Software')
            value_props.append(f"Specialized expertise in {solution_type.lower()} development")
            
            if solution_data.get('technology_stack'):
                value_props.append("Modern, scalable technology stack ensuring long-term viability")
        
        if delivery_data:
            approach = delivery_data.get('delivery_approach', 'Agile')
            value_props.append(f"{approach} methodology ensuring transparency and flexibility")
            
            if delivery_data.get('quality_assurance'):
                value_props.append("Comprehensive quality assurance and testing procedures")
        
        value_props.extend([
            "Fixed timeline and budget with clear milestones",
            "Post-launch support and maintenance included",
            "Ongoing partnership for future enhancements and scaling"
        ])
        
        return value_props[:6]  # Limit to 6 key value propositions

    def _fallback_competitive_advantages(self, solution_data: Dict = None) -> List[str]:
        """Identify competitive advantages based on solution approach."""
        
        advantages = [
            "Deep technical expertise and industry experience",
            "Proven delivery methodology with risk mitigation",
            "Competitive pricing with transparent cost structure"
        ]
        
        if solution_data:
            if solution_data.get('solution_score', 0) > 70:
                advantages.append("Comprehensive solution addressing all technical requirements")
            
            tech_stack = solution_data.get('technology_stack', {})
            if tech_stack:
                advantages.append("Modern technology stack with future-proofing considerations")
        
        advantages.extend([
            "Flexible engagement model with scalable team",
            "Local team with direct communication and collaboration",
            "Long-term partnership approach beyond project completion"
        ])
        
        return advantages[:5]  # Limit to 5 key advantages

    def _fallback_risk_assessment(self, customer_data: Dict, conversation_data: Dict, delivery_data: Dict = None) -> Dict[str, List[str]]:
        """Assess commercial and delivery risks."""
        
        client_risks = ["Standard project execution risks"]
        vendor_risks = ["Scope creep and requirement changes"]
        mitigation_strategies = ["Regular communication and progress reviews"]
        
        # Budget-related risks
        budget_min = customer_data.get('budget_range_min', 0)
        if budget_min < 25000:
            client_risks.append("Limited budget may impact scope or quality")
            mitigation_strategies.append("Phased delivery approach to manage costs")
        
        # Timeline risks
        urgency = str(conversation_data.get('urgency_level', '')).lower()
        if urgency == 'high':
            client_risks.append("Tight timeline may increase project risk")
            vendor_risks.append("Compressed schedule may impact resource allocation")
            mitigation_strategies.append("Dedicated team assignment and clear priorities")
        
        # Requirements risks
        requirements = str(conversation_data.get('customer_requirements', ''))
        if len(requirements) < 100:
            client_risks.append("Unclear requirements may lead to scope changes")
            vendor_risks.append("Requirement clarification may impact timeline")
            mitigation_strategies.append("Detailed requirements workshop before development")
        
        # Delivery complexity risks
        if delivery_data and delivery_data.get('delivery_score', 0) < 60:
            vendor_risks.append("Complex delivery requirements increase execution risk")
            mitigation_strategies.append("Proof of concept phase to validate approach")
        
        return {
            'client_risks': client_risks,
            'vendor_risks': vendor_risks,
            'mitigation_strategies': mitigation_strategies
        }

    def _fallback_proposal_sections(self, score: float) -> List[Dict[str, str]]:
        """Define proposal sections based on deal complexity."""
        
        sections = [
            {
                'section': 'Executive Summary',
                'content': 'High-level overview of solution and value proposition',
                'priority': 'High'
            },
            {
                'section': 'Understanding & Approach',
                'content': 'Demonstration of requirements understanding and solution approach',
                'priority': 'High'
            },
            {
                'section': 'Technical Solution',
                'content': 'Detailed technical architecture and implementation plan',
                'priority': 'High'
            },
            {
                'section': 'Team & Experience',
                'content': 'Team composition and relevant project experience',
                'priority': 'Medium'
            },
            {
                'section': 'Timeline & Deliverables',
                'content': 'Project timeline with key milestones and deliverables',
                'priority': 'High'
            },
            {
                'section': 'Investment & Terms',
                'content': 'Commercial proposal with pricing and contract terms',
                'priority': 'High'
            }
        ]
        
        # Add optional sections for high-value deals
        if score > 70:
            sections.extend([
                {
                    'section': 'Case Studies',
                    'content': 'Relevant project examples and client testimonials',
                    'priority': 'Medium'
                },
                {
                    'section': 'Risk Management',
                    'content': 'Risk assessment and mitigation strategies',
                    'priority': 'Medium'
                }
            ])
        
        return sections

    def _fallback_negotiation_strategy(self, score: float) -> List[str]:
        """Generate negotiation strategy recommendations."""
        
        strategies = [
            "Lead with value proposition and business impact",
            "Be flexible on payment terms while maintaining total value"
        ]
        
        if score > 80:
            strategies.extend([
                "Confident pricing with minimal discounting",
                "Focus on long-term partnership opportunities",
                "Upsell additional services and future phases"
            ])
        elif score > 60:
            strategies.extend([
                "Moderate flexibility on pricing (up to 10% discount)",
                "Emphasize competitive advantages and unique value",
                "Consider milestone-based pricing for risk mitigation"
            ])
        else:
            strategies.extend([
                "Competitive pricing with value justification",
                "Consider phased approach to reduce initial investment",
                "Focus on building relationship for future opportunities"
            ])
        
        return strategies

    def _fallback_success_metrics(self, conversation_data: Dict) -> List[str]:
        """Define success metrics based on business goals."""
        
        metrics = [
            "On-time delivery within agreed timeline",
            "Budget adherence with no cost overruns",
            "Quality delivery meeting all acceptance criteria"
        ]
        
        goals = str(conversation_data.get('business_goals', '')).lower()
        
        if 'efficiency' in goals:
            metrics.append("Process efficiency improvements measured")
        if 'revenue' in goals or 'sales' in goals:
            metrics.append("Revenue impact tracking and measurement")
        if 'cost' in goals:
            metrics.append("Cost reduction achievements quantified")
        if 'customer' in goals:
            metrics.append("Customer satisfaction and user adoption metrics")
        
        metrics.append("Post-launch support and stability metrics")
        
        return metrics[:6]  # Limit to 6 metrics

    def _fallback_generate_recommendations(self, score: float, pricing_model: str) -> List[str]:
        """Generate strategic commercial recommendations."""
        
        recommendations = []
        
        if score > 80:
            recommendations.append("High-confidence deal - pursue aggressively with premium positioning")
            recommendations.append("Focus on long-term relationship and future expansion opportunities")
        elif score > 60:
            recommendations.append("Solid opportunity - balance competitive pricing with value demonstration")
            recommendations.append("Consider flexible terms to improve win probability")
        else:
            recommendations.append("Cautious approach - ensure clear requirements and manageable scope")
            recommendations.append("Consider pilot project or phased delivery to reduce risk")
        
        if pricing_model == 'Time & Materials':
            recommendations.append("Establish clear effort estimates and regular review cycles")
        elif pricing_model == 'Fixed Price':
            recommendations.append("Ensure comprehensive scope definition and change control process")
        
        recommendations.append("Plan for post-project relationship and ongoing support opportunities")
        
        return recommendations[:5]  # Limit to 5 recommendations