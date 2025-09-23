"""
AI Agent for Resource Allocation and Delivery Planning

This agent analyzes qualified leads with technical solutions and generates resource allocation
recommendations including team composition, timeline planning, and delivery strategies.
"""

import os
import json
import re
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DeliveryPlanningAgent:
    """AI agent for generating delivery plans and resource allocation recommendations."""
    
    def __init__(self):
        """Initialize the Delivery Planning Agent with OpenAI client."""
        
        # OpenAI configuration
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.fallback_enabled = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Role definitions and skill requirements
        self.role_definitions = {
            'Project Manager': {
                'skills': ['Project Management', 'Agile/Scrum', 'Stakeholder Management'],
                'responsibilities': ['Planning', 'Coordination', 'Risk Management'],
                'allocation': 0.5  # 50% allocation for typical project
            },
            'Solution Architect': {
                'skills': ['System Design', 'Technology Strategy', 'Architecture Patterns'],
                'responsibilities': ['Technical Leadership', 'Architecture Design', 'Code Review'],
                'allocation': 0.3  # 30% allocation
            },
            'Senior Developer': {
                'skills': ['Full-stack Development', 'Code Quality', 'Mentoring'],
                'responsibilities': ['Core Development', 'Technical Decisions', 'Team Leadership'],
                'allocation': 1.0  # Full-time
            },
            'Frontend Developer': {
                'skills': ['React/Vue/Angular', 'HTML/CSS/JS', 'UI/UX Implementation'],
                'responsibilities': ['User Interface', 'Frontend Architecture', 'User Experience'],
                'allocation': 1.0
            },
            'Backend Developer': {
                'skills': ['API Development', 'Database Design', 'Server Architecture'],
                'responsibilities': ['API Development', 'Data Management', 'Integration'],
                'allocation': 1.0
            },
            'DevOps Engineer': {
                'skills': ['CI/CD', 'Cloud Platforms', 'Infrastructure Management'],
                'responsibilities': ['Deployment', 'Infrastructure', 'Monitoring'],
                'allocation': 0.3
            },
            'QA Engineer': {
                'skills': ['Test Automation', 'Manual Testing', 'Quality Assurance'],
                'responsibilities': ['Testing Strategy', 'Quality Control', 'Bug Tracking'],
                'allocation': 0.7
            },
            'UI/UX Designer': {
                'skills': ['User Research', 'Interface Design', 'Prototyping'],
                'responsibilities': ['Design System', 'User Experience', 'Visual Design'],
                'allocation': 0.4
            }
        }
        
        # Complexity multipliers for different project types
        self.complexity_factors = {
            'Web Application': 1.0,
            'Mobile Application': 1.3,
            'Data Analytics': 1.1,
            'CRM/ERP': 1.5,
            'E-commerce': 1.4,
            'Integration Platform': 1.2,
            'Custom Software': 1.3
        }

    def analyze_delivery_requirements(self, customer_data: Dict, conversation_data: Dict, solution_data: Dict = None) -> Dict[str, Any]:
        """
        Analyze delivery requirements and generate resource allocation plan.
        
        Args:
            customer_data: Basic customer information from CRM
            conversation_data: Conversation history and business requirements
            solution_data: Technical solution design from previous stage
            
        Returns:
            Dictionary with delivery plan and resource allocation recommendations
        """
        
        try:
            # Try AI analysis first
            return self._ai_analyze_delivery(customer_data, conversation_data, solution_data)
        except Exception as e:
            print(f"AI delivery analysis failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based delivery analysis")
                return self._fallback_analyze_delivery(customer_data, conversation_data, solution_data)
            else:
                raise e

    def _ai_analyze_delivery(self, customer_data: Dict, conversation_data: Dict, solution_data: Dict = None) -> Dict[str, Any]:
        """Use OpenAI to analyze requirements and generate delivery plan."""
        
        # Prepare the prompt with all available data
        prompt = self._build_delivery_prompt(customer_data, conversation_data, solution_data)
        
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
                temperature=0.3,  # Lower temperature for consistent planning
                max_tokens=3000   # More tokens for detailed delivery plans
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, customer_data, conversation_data, solution_data)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role and output format."""
        return """
You are an expert delivery manager and resource planning specialist. Your job is to analyze project requirements and technical solutions to create comprehensive delivery plans with optimal resource allocation.

You must ALWAYS respond with a valid JSON object containing exactly these fields:
{
    "delivery_score": <number 0-100>,
    "delivery_approach": "<string: recommended delivery methodology>",
    "team_composition": [
        {
            "role": "<string: role name>",
            "allocation": <number: percentage allocation 0-1>,
            "skills_required": [<array of required skills>],
            "responsibilities": [<array of key responsibilities>]
        }
    ],
    "project_phases": [
        {
            "phase": "<string: phase name>",
            "duration": "<string: estimated duration>",
            "deliverables": [<array of phase deliverables>],
            "resources": [<array of required roles>]
        }
    ],
    "resource_timeline": "<string: overall resource timeline>",
    "budget_estimate": {
        "development_cost": "<string: estimated development cost range>",
        "resource_cost": "<string: estimated resource cost>",
        "total_estimate": "<string: total project cost estimate>"
    },
    "risk_mitigation": [<array of delivery risk mitigation strategies>],
    "quality_assurance": [<array of QA and quality control measures>],
    "recommendations": [<array of delivery strategy recommendations>],
    "confidence": <number 0-100>,
    "reasoning": "<string explaining your delivery analysis>"
}

DELIVERY SCORING CRITERIA (0-100):
- Requirements Clarity (20%): How well-defined are the project requirements?
- Technical Complexity (25%): How complex is the technical implementation?
- Timeline Feasibility (20%): How realistic is the proposed timeline?
- Resource Availability (15%): How available are the required resources?
- Delivery Risk (20%): How risky is the delivery plan?

DELIVERY APPROACHES:
- Agile/Scrum: Iterative development with regular sprints and feedback
- Waterfall: Sequential phases with clear milestones and deliverables
- Hybrid: Combination of agile and waterfall based on project needs
- Lean Startup: MVP-focused with rapid iteration and customer feedback
- DevOps: Continuous integration and deployment with automation

TEAM ROLES TO CONSIDER:
- Project Manager: Planning, coordination, stakeholder management
- Solution Architect: Technical leadership and architecture design
- Senior Developer: Core development and technical decisions
- Frontend Developer: User interface and user experience
- Backend Developer: API development and data management
- DevOps Engineer: Infrastructure, deployment, and CI/CD
- QA Engineer: Testing strategy and quality assurance
- UI/UX Designer: User experience and interface design

PROJECT PHASES should be logical and sequential:
- Discovery & Planning: Requirements analysis and project setup
- Design & Architecture: Solution design and technical planning
- Development Sprints: Iterative development cycles
- Integration & Testing: System integration and comprehensive testing
- Deployment & Launch: Production deployment and go-live
- Support & Maintenance: Post-launch support and ongoing maintenance

BUDGET ESTIMATION FACTORS:
- Team size and seniority levels
- Project duration and complexity
- Technology and infrastructure costs
- Risk and contingency buffers
- Regional rate variations

Focus on practical, achievable delivery plans that balance quality, timeline, and cost constraints.
"""

    def _build_delivery_prompt(self, customer_data: Dict, conversation_data: Dict, solution_data: Dict = None) -> str:
        """Build the delivery analysis prompt with all available data."""
        
        prompt = "Analyze the following project requirements and create a comprehensive delivery plan:\n\n"
        
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
        
        # Technical Solution (if available)
        if solution_data:
            prompt += "\nTECHNICAL SOLUTION:\n"
            for key, value in solution_data.items():
                if value and key != 'deal_id':
                    if isinstance(value, dict):
                        prompt += f"- {key}:\n"
                        for sub_key, sub_value in value.items():
                            prompt += f"  * {sub_key}: {sub_value}\n"
                    elif isinstance(value, list):
                        prompt += f"- {key}: {', '.join(map(str, value))}\n"
                    else:
                        prompt += f"- {key}: {value}\n"
        
        prompt += "\nPlease provide a comprehensive delivery plan with resource allocation and timeline."
        
        return prompt

    def _parse_ai_response(self, ai_response: str, customer_data: Dict, conversation_data: Dict, solution_data: Dict = None) -> Dict[str, Any]:
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
                return self._fallback_analyze_delivery(customer_data, conversation_data, solution_data)
            else:
                raise e

    def _standardize_response(self, parsed_response: Dict) -> Dict[str, Any]:
        """Ensure the AI response matches our expected format exactly."""
        
        # Ensure all required fields are present with defaults
        standardized = {
            'delivery_score': float(parsed_response.get('delivery_score', 0)),
            'delivery_approach': parsed_response.get('delivery_approach', 'Agile/Scrum'),
            'team_composition': parsed_response.get('team_composition', []),
            'project_phases': parsed_response.get('project_phases', []),
            'resource_timeline': parsed_response.get('resource_timeline', '3-6 months'),
            'budget_estimate': parsed_response.get('budget_estimate', {}),
            'risk_mitigation': parsed_response.get('risk_mitigation', []),
            'quality_assurance': parsed_response.get('quality_assurance', []),
            'recommendations': parsed_response.get('recommendations', []),
            'confidence': float(parsed_response.get('confidence', 50)),
            'deal_id': parsed_response.get('deal_id'),  # This will be set by the API
        }
        
        # Ensure values are within valid ranges
        standardized['delivery_score'] = max(0, min(100, standardized['delivery_score']))
        standardized['confidence'] = max(0, min(100, standardized['confidence']))
        
        # Ensure budget_estimate has required structure
        if not isinstance(standardized['budget_estimate'], dict):
            standardized['budget_estimate'] = {}
        
        budget_defaults = {
            'development_cost': 'To be determined',
            'resource_cost': 'To be determined',
            'total_estimate': 'To be determined'
        }
        
        for key, default_value in budget_defaults.items():
            if key not in standardized['budget_estimate']:
                standardized['budget_estimate'][key] = default_value
        
        return standardized

    def _fallback_analyze_delivery(self, customer_data: Dict, conversation_data: Dict, solution_data: Dict = None) -> Dict[str, Any]:
        """Fallback rule-based delivery analysis when AI is unavailable."""
        
        # Determine solution type and complexity
        solution_type = solution_data.get('solution_type', 'Custom Software') if solution_data else 'Custom Software'
        
        # Calculate delivery score
        delivery_score = self._fallback_calculate_score(customer_data, conversation_data, solution_data)
        
        # Determine delivery approach
        delivery_approach = self._fallback_delivery_approach(delivery_score, solution_type)
        
        # Generate team composition
        team_composition = self._fallback_team_composition(solution_type, delivery_score)
        
        # Create project phases
        project_phases = self._fallback_project_phases(solution_type, delivery_approach)
        
        # Estimate timeline and budget
        timeline = self._fallback_estimate_timeline(solution_type, delivery_score)
        budget = self._fallback_budget_estimate(team_composition, timeline)
        
        return {
            'delivery_score': delivery_score,
            'delivery_approach': delivery_approach,
            'team_composition': team_composition,
            'project_phases': project_phases,
            'resource_timeline': timeline,
            'budget_estimate': budget,
            'risk_mitigation': self._fallback_risk_mitigation(solution_type),
            'quality_assurance': self._fallback_quality_assurance(delivery_approach),
            'recommendations': self._fallback_generate_recommendations(delivery_score, solution_type),
            'confidence': 70.0  # Fixed confidence for rule-based system
        }

    def _fallback_calculate_score(self, customer_data: Dict, conversation_data: Dict, solution_data: Dict = None) -> float:
        """Calculate delivery score based on project clarity and feasibility."""
        
        score = 0.0
        
        # Requirements clarity (30 points)
        if conversation_data.get('customer_requirements'):
            score += 15
        if conversation_data.get('business_goals'):
            score += 10
        if conversation_data.get('project_timeline'):
            score += 5
        
        # Technical solution clarity (25 points)
        if solution_data:
            if solution_data.get('technology_stack'):
                score += 10
            if solution_data.get('implementation_phases'):
                score += 10
            if solution_data.get('solution_score', 0) > 70:
                score += 5
        
        # Budget and resources (25 points)
        if customer_data.get('budget_range_min'):
            score += 15
        if conversation_data.get('decision_makers'):
            score += 10
        
        # Timeline feasibility (20 points)
        urgency = str(conversation_data.get('urgency_level', '')).lower()
        timeline = str(conversation_data.get('project_timeline', '')).lower()
        
        if urgency == 'low' or '6' in timeline or 'year' in timeline:
            score += 20  # Reasonable timeline
        elif urgency == 'medium':
            score += 15
        elif urgency == 'high':
            score += 5   # Tight timeline is risky
        
        return min(100.0, score)

    def _fallback_delivery_approach(self, score: float, solution_type: str) -> str:
        """Determine appropriate delivery approach."""
        
        if score >= 80:
            return 'Agile/Scrum'  # High confidence enables agile
        elif score >= 60:
            return 'Hybrid'       # Medium confidence needs structure
        elif solution_type in ['CRM/ERP', 'Data Analytics']:
            return 'Waterfall'    # Complex systems need more planning
        else:
            return 'Lean Startup' # Uncertain requirements need validation

    def _fallback_team_composition(self, solution_type: str, score: float) -> List[Dict[str, Any]]:
        """Generate team composition based on solution type and complexity."""
        
        team = []
        
        # Base team always needed
        team.append({
            'role': 'Project Manager',
            'allocation': 0.5,
            'skills_required': self.role_definitions['Project Manager']['skills'],
            'responsibilities': self.role_definitions['Project Manager']['responsibilities']
        })
        
        # Technical roles based on solution type
        if solution_type in ['Web Application', 'Custom Software']:
            team.extend([
                {
                    'role': 'Senior Developer',
                    'allocation': 1.0,
                    'skills_required': self.role_definitions['Senior Developer']['skills'],
                    'responsibilities': self.role_definitions['Senior Developer']['responsibilities']
                },
                {
                    'role': 'Frontend Developer',
                    'allocation': 1.0,
                    'skills_required': self.role_definitions['Frontend Developer']['skills'],
                    'responsibilities': self.role_definitions['Frontend Developer']['responsibilities']
                },
                {
                    'role': 'Backend Developer',
                    'allocation': 1.0,
                    'skills_required': self.role_definitions['Backend Developer']['skills'],
                    'responsibilities': self.role_definitions['Backend Developer']['responsibilities']
                }
            ])
        
        elif solution_type == 'Mobile Application':
            team.extend([
                {
                    'role': 'Senior Developer',
                    'allocation': 1.0,
                    'skills_required': ['Mobile Development', 'React Native/Flutter', 'API Integration'],
                    'responsibilities': ['Mobile App Development', 'Platform Optimization', 'Performance Tuning']
                },
                {
                    'role': 'Backend Developer',
                    'allocation': 1.0,
                    'skills_required': self.role_definitions['Backend Developer']['skills'],
                    'responsibilities': self.role_definitions['Backend Developer']['responsibilities']
                }
            ])
        
        elif solution_type == 'Data Analytics':
            team.extend([
                {
                    'role': 'Senior Developer',
                    'allocation': 1.0,
                    'skills_required': ['Python/R', 'Data Processing', 'Analytics Tools'],
                    'responsibilities': ['Data Pipeline Development', 'Analytics Implementation', 'Performance Optimization']
                },
                {
                    'role': 'Backend Developer',
                    'allocation': 0.7,
                    'skills_required': ['Database Design', 'API Development', 'Data Integration'],
                    'responsibilities': ['Data Management', 'API Development', 'Database Optimization']
                }
            ])
        
        # Additional roles for complex projects
        if score >= 70:
            team.append({
                'role': 'Solution Architect',
                'allocation': 0.3,
                'skills_required': self.role_definitions['Solution Architect']['skills'],
                'responsibilities': self.role_definitions['Solution Architect']['responsibilities']
            })
        
        # Quality assurance
        team.append({
            'role': 'QA Engineer',
            'allocation': 0.7,
            'skills_required': self.role_definitions['QA Engineer']['skills'],
            'responsibilities': self.role_definitions['QA Engineer']['responsibilities']
        })
        
        # DevOps for deployment
        team.append({
            'role': 'DevOps Engineer',
            'allocation': 0.3,
            'skills_required': self.role_definitions['DevOps Engineer']['skills'],
            'responsibilities': self.role_definitions['DevOps Engineer']['responsibilities']
        })
        
        # UI/UX for user-facing applications
        if solution_type in ['Web Application', 'Mobile Application', 'E-commerce']:
            team.append({
                'role': 'UI/UX Designer',
                'allocation': 0.4,
                'skills_required': self.role_definitions['UI/UX Designer']['skills'],
                'responsibilities': self.role_definitions['UI/UX Designer']['responsibilities']
            })
        
        return team

    def _fallback_project_phases(self, solution_type: str, delivery_approach: str) -> List[Dict[str, Any]]:
        """Generate project phases based on solution type and approach."""
        
        if delivery_approach == 'Waterfall':
            return [
                {
                    'phase': 'Discovery & Requirements',
                    'duration': '2-3 weeks',
                    'deliverables': ['Requirements Document', 'Technical Specifications'],
                    'resources': ['Project Manager', 'Solution Architect', 'Business Analyst']
                },
                {
                    'phase': 'Design & Architecture',
                    'duration': '2-4 weeks',
                    'deliverables': ['System Architecture', 'UI/UX Designs', 'Database Design'],
                    'resources': ['Solution Architect', 'UI/UX Designer', 'Senior Developer']
                },
                {
                    'phase': 'Development',
                    'duration': '8-16 weeks',
                    'deliverables': ['Core Application', 'API Implementation', 'Frontend Development'],
                    'resources': ['All Developers', 'QA Engineer']
                },
                {
                    'phase': 'Testing & Integration',
                    'duration': '2-4 weeks',
                    'deliverables': ['Test Results', 'Integration Testing', 'Performance Testing'],
                    'resources': ['QA Engineer', 'Senior Developer', 'DevOps Engineer']
                },
                {
                    'phase': 'Deployment & Launch',
                    'duration': '1-2 weeks',
                    'deliverables': ['Production Deployment', 'Documentation', 'Training'],
                    'resources': ['DevOps Engineer', 'Project Manager']
                }
            ]
        else:  # Agile/Scrum or Hybrid
            return [
                {
                    'phase': 'Sprint 0 - Setup',
                    'duration': '1-2 weeks',
                    'deliverables': ['Project Setup', 'Development Environment', 'Initial Backlog'],
                    'resources': ['Project Manager', 'Solution Architect', 'DevOps Engineer']
                },
                {
                    'phase': 'Sprint 1-2 - Core Features',
                    'duration': '4 weeks',
                    'deliverables': ['MVP Features', 'Basic UI', 'Core APIs'],
                    'resources': ['All Development Team']
                },
                {
                    'phase': 'Sprint 3-4 - Feature Development',
                    'duration': '4 weeks',
                    'deliverables': ['Advanced Features', 'Integrations', 'Testing Framework'],
                    'resources': ['All Development Team', 'QA Engineer']
                },
                {
                    'phase': 'Sprint 5-6 - Polish & Testing',
                    'duration': '4 weeks',
                    'deliverables': ['Bug Fixes', 'Performance Optimization', 'User Testing'],
                    'resources': ['Development Team', 'QA Engineer', 'UI/UX Designer']
                },
                {
                    'phase': 'Release & Launch',
                    'duration': '1-2 weeks',
                    'deliverables': ['Production Release', 'Documentation', 'Support Handover'],
                    'resources': ['DevOps Engineer', 'Project Manager']
                }
            ]

    def _fallback_estimate_timeline(self, solution_type: str, score: float) -> str:
        """Estimate overall project timeline."""
        
        base_timelines = {
            'Web Application': '3-5 months',
            'Mobile Application': '4-7 months',
            'Data Analytics': '2-4 months',
            'CRM/ERP': '6-12 months',
            'E-commerce': '4-8 months',
            'Integration Platform': '2-6 months',
            'Custom Software': '4-10 months'
        }
        
        timeline = base_timelines.get(solution_type, '4-8 months')
        
        # Adjust based on delivery score
        if score < 50:
            timeline += ' (extended due to complexity and risks)'
        elif score > 80:
            timeline += ' (optimized with clear requirements)'
        
        return timeline

    def _fallback_budget_estimate(self, team_composition: List[Dict], timeline: str) -> Dict[str, str]:
        """Estimate project budget based on team and timeline."""
        
        # Extract months from timeline
        import re
        months_match = re.search(r'(\d+)-(\d+)', timeline)
        avg_months = 4  # Default
        if months_match:
            min_months, max_months = map(int, months_match.groups())
            avg_months = (min_months + max_months) / 2
        
        # Calculate team cost (simplified)
        total_allocation = sum(member['allocation'] for member in team_composition)
        
        # Rough cost estimates (in thousands)
        monthly_rate = 8  # $8k per full-time developer per month
        development_cost = int(total_allocation * monthly_rate * avg_months)
        
        return {
            'development_cost': f'${development_cost}k - ${int(development_cost * 1.3)}k',
            'resource_cost': f'${int(development_cost * 0.2)}k (infrastructure and tools)',
            'total_estimate': f'${int(development_cost * 1.2)}k - ${int(development_cost * 1.5)}k'
        }

    def _fallback_risk_mitigation(self, solution_type: str) -> List[str]:
        """Generate risk mitigation strategies."""
        
        strategies = [
            "Regular sprint reviews and stakeholder feedback",
            "Continuous integration and automated testing",
            "Weekly progress reviews and risk assessment"
        ]
        
        if solution_type in ['CRM/ERP', 'Data Analytics']:
            strategies.append("Data backup and migration testing")
        
        if solution_type in ['Web Application', 'E-commerce']:
            strategies.append("Security testing and performance monitoring")
        
        return strategies

    def _fallback_quality_assurance(self, delivery_approach: str) -> List[str]:
        """Generate quality assurance measures."""
        
        qa_measures = [
            "Automated unit testing with minimum 80% coverage",
            "Code review process for all commits",
            "Integration testing for all major features"
        ]
        
        if delivery_approach == 'Agile/Scrum':
            qa_measures.extend([
                "Sprint retrospectives for continuous improvement",
                "Definition of Done criteria for each story"
            ])
        else:
            qa_measures.extend([
                "Comprehensive system testing phase",
                "User acceptance testing with stakeholders"
            ])
        
        return qa_measures

    def _fallback_generate_recommendations(self, score: float, solution_type: str) -> List[str]:
        """Generate delivery strategy recommendations."""
        
        recommendations = []
        
        if score < 60:
            recommendations.append("Conduct detailed requirements workshop before starting development")
            recommendations.append("Consider proof-of-concept phase to validate approach")
        else:
            recommendations.append("Leverage clear requirements for efficient delivery")
            recommendations.append("Implement continuous delivery for rapid feedback")
        
        recommendations.append(f"Follow {solution_type.lower()} development best practices")
        recommendations.append("Establish clear communication channels with stakeholders")
        recommendations.append("Plan for regular milestone reviews and course corrections")
        
        return recommendations[:5]  # Limit to 5 recommendations