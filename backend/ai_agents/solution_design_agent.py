"""
AI Agent for Technical Solution Design

This agent analyzes qualified leads and generates technical solution recommendations
including architecture design, technology stack selection, and implementation approach.
"""

import os
import json
import re
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SolutionDesignAgent:
    """AI agent for generating technical solution designs and recommendations."""
    
    def __init__(self):
        """Initialize the Solution Design Agent with OpenAI client."""
        
        # OpenAI configuration
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.fallback_enabled = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Technology and solution patterns
        self.technology_stacks = {
            'Web Application': {
                'frontend': ['React', 'Vue.js', 'Angular', 'Next.js'],
                'backend': ['Node.js', 'Python/Django', 'Python/FastAPI', '.NET Core', 'Java/Spring'],
                'database': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis'],
                'deployment': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes']
            },
            'Mobile Application': {
                'native': ['Swift/iOS', 'Kotlin/Android'],
                'cross_platform': ['React Native', 'Flutter', 'Xamarin'],
                'backend': ['Node.js', 'Python/FastAPI', 'Firebase'],
                'database': ['Firebase', 'PostgreSQL', 'MongoDB']
            },
            'Data Analytics': {
                'processing': ['Python/Pandas', 'Apache Spark', 'Airflow'],
                'visualization': ['Tableau', 'Power BI', 'D3.js', 'Plotly'],
                'database': ['PostgreSQL', 'BigQuery', 'Snowflake', 'Redshift'],
                'ml_platform': ['TensorFlow', 'PyTorch', 'Scikit-learn']
            },
            'CRM/ERP': {
                'platform': ['Salesforce', 'Microsoft Dynamics', 'Custom Build'],
                'integration': ['REST APIs', 'GraphQL', 'Webhooks'],
                'database': ['PostgreSQL', 'SQL Server', 'Oracle'],
                'reporting': ['Power BI', 'Tableau', 'Custom Dashboards']
            }
        }
        
        self.integration_patterns = {
            'API Integration': ['REST API', 'GraphQL', 'Webhooks', 'Message Queues'],
            'Data Integration': ['ETL Pipelines', 'Real-time Sync', 'Batch Processing'],
            'Authentication': ['OAuth 2.0', 'SAML', 'SSO', 'JWT Tokens'],
            'Security': ['HTTPS/TLS', 'Data Encryption', 'Access Controls', 'Audit Logging']
        }

    def analyze_solution_requirements(self, customer_data: Dict, conversation_data: Dict, technical_data: Dict = None) -> Dict[str, Any]:
        """
        Analyze customer requirements and generate technical solution recommendations.
        
        Args:
            customer_data: Basic customer information from CRM
            conversation_data: Conversation history and business requirements  
            technical_data: Existing technical information if available
            
        Returns:
            Dictionary with technical solution design and recommendations
        """
        
        try:
            # Try AI analysis first
            return self._ai_analyze_solution(customer_data, conversation_data, technical_data)
        except Exception as e:
            print(f"AI solution analysis failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based solution analysis")
                return self._fallback_analyze_solution(customer_data, conversation_data, technical_data)
            else:
                raise e

    def _ai_analyze_solution(self, customer_data: Dict, conversation_data: Dict, technical_data: Dict = None) -> Dict[str, Any]:
        """Use OpenAI to analyze requirements and generate technical solution."""
        
        # Prepare the prompt with all available data
        prompt = self._build_solution_prompt(customer_data, conversation_data, technical_data)
        
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
                temperature=0.4,  # Slightly higher for creative solution design
                max_tokens=3000   # More tokens for detailed technical recommendations
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, customer_data, conversation_data, technical_data)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role and output format."""
        return """
You are an expert solution architect and technical consultant. Your job is to analyze business requirements and design comprehensive technical solutions that meet customer needs effectively.

You must ALWAYS respond with a valid JSON object containing exactly these fields:
{
    "solution_score": <number 0-100>,
    "solution_type": "<string: primary solution category>",
    "recommended_architecture": "<string: high-level architecture description>",
    "technology_stack": {
        "frontend": [<array of recommended frontend technologies>],
        "backend": [<array of recommended backend technologies>],
        "database": [<array of recommended database technologies>],
        "deployment": [<array of recommended deployment/hosting options>]
    },
    "integration_requirements": [<array of integration needs>],
    "implementation_phases": [<array of implementation phase descriptions>],
    "estimated_timeline": "<string: overall timeline estimate>",
    "complexity_factors": [<array of technical complexity considerations>],
    "risk_factors": [<array of technical and implementation risks>],
    "recommendations": [<array of strategic technical recommendations>],
    "confidence": <number 0-100>,
    "reasoning": "<string explaining your technical analysis>"
}

SOLUTION SCORING CRITERIA (0-100):
- Requirements Clarity (25%): How well-defined are the technical requirements?
- Technical Feasibility (25%): How achievable is the solution with current technology?
- Scalability Needs (20%): How well does the solution address growth requirements?
- Integration Complexity (15%): How complex are the required integrations?
- Implementation Risk (15%): How risky is the technical implementation?

SOLUTION TYPES:
- Web Application: Browser-based applications and portals
- Mobile Application: Native or cross-platform mobile apps
- Data Analytics: BI, reporting, and analytics platforms
- CRM/ERP: Customer or enterprise resource management systems
- E-commerce: Online selling and marketplace platforms
- Integration Platform: API and data integration solutions
- Custom Software: Bespoke software solutions

ARCHITECTURE PATTERNS:
- Monolithic: Single deployable unit, simpler to develop and deploy
- Microservices: Distributed services, better scalability and team independence
- Serverless: Event-driven, auto-scaling, pay-per-use
- Hybrid: Combination of patterns based on specific needs

TECHNOLOGY SELECTION FACTORS:
- Team expertise and learning curve
- Performance and scalability requirements
- Integration needs with existing systems
- Budget and licensing considerations
- Long-term maintenance and support

IMPLEMENTATION PHASES should be logical, sequential steps like:
- Discovery & Planning, Architecture Design, Core Development, Integration & Testing, Deployment & Launch

Focus on practical, implementable solutions that balance technical excellence with business constraints.
"""

    def _build_solution_prompt(self, customer_data: Dict, conversation_data: Dict, technical_data: Dict = None) -> str:
        """Build the solution analysis prompt with all available data."""
        
        prompt = "Analyze the following business requirements and design a comprehensive technical solution:\n\n"
        
        # Customer Information
        prompt += "CUSTOMER INFORMATION:\n"
        for key, value in customer_data.items():
            if value:
                prompt += f"- {key}: {value}\n"
        
        # Business Requirements from Conversation
        prompt += "\nBUSINESS REQUIREMENTS:\n"
        for key, value in conversation_data.items():
            if value:
                prompt += f"- {key}: {value}\n"
        
        # Technical Information (if available)
        if technical_data:
            prompt += "\nEXISTING TECHNICAL CONTEXT:\n"
            for key, value in technical_data.items():
                if value:
                    prompt += f"- {key}: {value}\n"
        
        prompt += "\nPlease provide a comprehensive technical solution design that addresses all requirements."
        
        return prompt

    def _parse_ai_response(self, ai_response: str, customer_data: Dict, conversation_data: Dict, technical_data: Dict = None) -> Dict[str, Any]:
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
                return self._fallback_analyze_solution(customer_data, conversation_data, technical_data)
            else:
                raise e

    def _standardize_response(self, parsed_response: Dict) -> Dict[str, Any]:
        """Ensure the AI response matches our expected format exactly."""
        
        # Ensure all required fields are present with defaults
        standardized = {
            'solution_score': float(parsed_response.get('solution_score', 0)),
            'solution_type': parsed_response.get('solution_type', 'Custom Software'),
            'recommended_architecture': parsed_response.get('recommended_architecture', 'Monolithic architecture'),
            'technology_stack': parsed_response.get('technology_stack', {}),
            'integration_requirements': parsed_response.get('integration_requirements', []),
            'implementation_phases': parsed_response.get('implementation_phases', []),
            'estimated_timeline': parsed_response.get('estimated_timeline', '3-6 months'),
            'complexity_factors': parsed_response.get('complexity_factors', []),
            'risk_factors': parsed_response.get('risk_factors', []),
            'recommendations': parsed_response.get('recommendations', []),
            'confidence': float(parsed_response.get('confidence', 50)),
            'deal_id': parsed_response.get('deal_id'),  # This will be set by the API
        }
        
        # Ensure values are within valid ranges
        standardized['solution_score'] = max(0, min(100, standardized['solution_score']))
        standardized['confidence'] = max(0, min(100, standardized['confidence']))
        
        # Ensure technology_stack has required structure
        if not isinstance(standardized['technology_stack'], dict):
            standardized['technology_stack'] = {}
        
        # Ensure required tech stack categories
        for category in ['frontend', 'backend', 'database', 'deployment']:
            if category not in standardized['technology_stack']:
                standardized['technology_stack'][category] = []
        
        return standardized

    def _fallback_analyze_solution(self, customer_data: Dict, conversation_data: Dict, technical_data: Dict = None) -> Dict[str, Any]:
        """Fallback rule-based solution analysis when AI is unavailable."""
        
        # Analyze requirements to determine solution type
        solution_type = self._determine_solution_type(conversation_data)
        
        # Calculate solution score based on requirement clarity
        solution_score = self._fallback_calculate_score(customer_data, conversation_data)
        
        # Get recommended technology stack
        tech_stack = self._fallback_recommend_tech_stack(solution_type, conversation_data)
        
        # Determine implementation phases
        phases = self._fallback_implementation_phases(solution_type, solution_score)
        
        # Estimate timeline
        timeline = self._fallback_estimate_timeline(solution_type, solution_score)
        
        # Identify complexity and risk factors
        complexity_factors = self._fallback_complexity_factors(conversation_data)
        risk_factors = self._fallback_risk_factors(solution_type, conversation_data)
        
        # Generate recommendations
        recommendations = self._fallback_generate_recommendations(solution_type, solution_score)
        
        return {
            'solution_score': solution_score,
            'solution_type': solution_type,
            'recommended_architecture': f"{solution_type} with modular design",
            'technology_stack': tech_stack,
            'integration_requirements': self._fallback_integration_requirements(conversation_data),
            'implementation_phases': phases,
            'estimated_timeline': timeline,
            'complexity_factors': complexity_factors,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'confidence': 70.0  # Fixed confidence for rule-based system
        }

    def _determine_solution_type(self, conversation_data: Dict) -> str:
        """Determine the primary solution type based on requirements."""
        
        requirements = str(conversation_data.get('customer_requirements', '')).lower()
        pain_points = str(conversation_data.get('pain_points', '')).lower()
        
        # Check for solution type indicators
        if any(word in requirements + pain_points for word in ['mobile', 'app', 'android', 'ios']):
            return 'Mobile Application'
        elif any(word in requirements + pain_points for word in ['web', 'portal', 'website', 'dashboard']):
            return 'Web Application'
        elif any(word in requirements + pain_points for word in ['crm', 'customer', 'sales', 'lead']):
            return 'CRM/ERP'
        elif any(word in requirements + pain_points for word in ['analytics', 'reporting', 'dashboard', 'bi']):
            return 'Data Analytics'
        elif any(word in requirements + pain_points for word in ['ecommerce', 'shop', 'marketplace', 'selling']):
            return 'E-commerce'
        elif any(word in requirements + pain_points for word in ['integration', 'api', 'connect', 'sync']):
            return 'Integration Platform'
        else:
            return 'Custom Software'

    def _fallback_calculate_score(self, customer_data: Dict, conversation_data: Dict) -> float:
        """Calculate solution score based on requirement clarity and feasibility."""
        
        score = 0.0
        
        # Requirements clarity (40 points)
        if conversation_data.get('customer_requirements'):
            score += 20
        if conversation_data.get('business_goals'):
            score += 10
        if conversation_data.get('tech_preferences'):
            score += 10
        
        # Budget and timeline clarity (30 points)
        if customer_data.get('budget_range_min'):
            score += 15
        if conversation_data.get('project_timeline'):
            score += 15
        
        # Technical feasibility (30 points)
        urgency = str(conversation_data.get('urgency_level', '')).lower()
        if urgency in ['low', 'medium']:
            score += 15  # More time = higher feasibility
        elif urgency == 'high':
            score += 10
        
        # Additional complexity factors
        if conversation_data.get('integration_needs'):
            score += 15
        else:
            score += 5  # Less integration = simpler
        
        return min(100.0, score)

    def _fallback_recommend_tech_stack(self, solution_type: str, conversation_data: Dict) -> Dict[str, List[str]]:
        """Recommend technology stack based on solution type."""
        
        # Get base stack for solution type
        if solution_type in self.technology_stacks:
            base_stack = self.technology_stacks[solution_type].copy()
        else:
            base_stack = self.technology_stacks['Web Application'].copy()
        
        # Adjust based on preferences
        tech_prefs = str(conversation_data.get('tech_preferences', '')).lower()
        
        # Frontend adjustments
        if 'react' in tech_prefs and 'frontend' in base_stack:
            base_stack['frontend'] = ['React', 'Next.js']
        elif 'vue' in tech_prefs and 'frontend' in base_stack:
            base_stack['frontend'] = ['Vue.js', 'Nuxt.js']
        
        # Backend adjustments
        if 'python' in tech_prefs and 'backend' in base_stack:
            base_stack['backend'] = ['Python/FastAPI', 'Python/Django']
        elif 'node' in tech_prefs and 'backend' in base_stack:
            base_stack['backend'] = ['Node.js', 'Express.js']
        
        # Cloud preferences
        if 'aws' in tech_prefs and 'deployment' in base_stack:
            base_stack['deployment'] = ['AWS', 'Docker', 'Kubernetes']
        elif 'azure' in tech_prefs and 'deployment' in base_stack:
            base_stack['deployment'] = ['Azure', 'Docker', 'Azure DevOps']
        
        return base_stack

    def _fallback_implementation_phases(self, solution_type: str, score: float) -> List[str]:
        """Generate implementation phases based on solution complexity."""
        
        phases = [
            "Discovery & Requirements Analysis",
            "Architecture Design & Planning"
        ]
        
        if score >= 60:
            phases.extend([
                "Core Development Sprint 1",
                "Core Development Sprint 2",
                "Integration & Testing",
                "Deployment & Launch"
            ])
        else:
            phases.extend([
                "Proof of Concept Development",
                "Core Development Phase 1",
                "Core Development Phase 2", 
                "Integration & Testing Phase",
                "User Acceptance Testing",
                "Production Deployment"
            ])
        
        return phases

    def _fallback_estimate_timeline(self, solution_type: str, score: float) -> str:
        """Estimate implementation timeline."""
        
        base_timelines = {
            'Web Application': '3-6 months',
            'Mobile Application': '4-8 months',
            'Data Analytics': '2-4 months',
            'CRM/ERP': '6-12 months',
            'E-commerce': '4-8 months',
            'Integration Platform': '2-6 months',
            'Custom Software': '4-10 months'
        }
        
        base_timeline = base_timelines.get(solution_type, '4-8 months')
        
        # Adjust based on complexity score
        if score < 40:
            return f"{base_timeline} (extended due to complexity)"
        elif score > 80:
            return f"{base_timeline} (optimized timeline)"
        else:
            return base_timeline

    def _fallback_complexity_factors(self, conversation_data: Dict) -> List[str]:
        """Identify technical complexity factors."""
        
        factors = []
        
        requirements = str(conversation_data.get('customer_requirements', '')).lower()
        tech_prefs = str(conversation_data.get('tech_preferences', '')).lower()
        
        if 'integration' in requirements or 'api' in requirements:
            factors.append("Third-party system integrations")
        
        if 'real-time' in requirements or 'live' in requirements:
            factors.append("Real-time data processing requirements")
        
        if 'mobile' in requirements and 'web' in requirements:
            factors.append("Multi-platform development")
        
        if 'security' in requirements or 'compliance' in requirements:
            factors.append("Security and compliance requirements")
        
        if 'scale' in requirements or 'growth' in requirements:
            factors.append("Scalability and performance optimization")
        
        if not factors:
            factors.append("Standard business application complexity")
        
        return factors

    def _fallback_risk_factors(self, solution_type: str, conversation_data: Dict) -> List[str]:
        """Identify potential implementation risks."""
        
        risks = []
        
        urgency = str(conversation_data.get('urgency_level', '')).lower()
        if urgency == 'high':
            risks.append("Tight timeline may impact quality")
        
        requirements = str(conversation_data.get('customer_requirements', '')).lower()
        if not conversation_data.get('customer_requirements') or len(requirements) < 50:
            risks.append("Requirements may need further clarification")
        
        if 'integration' in requirements:
            risks.append("Third-party integration dependencies")
        
        if solution_type in ['CRM/ERP', 'Data Analytics']:
            risks.append("Data migration and integrity challenges")
        
        if not conversation_data.get('tech_preferences'):
            risks.append("Technology stack assumptions need validation")
        
        if not risks:
            risks.append("Standard implementation risks")
        
        return risks

    def _fallback_integration_requirements(self, conversation_data: Dict) -> List[str]:
        """Identify integration requirements."""
        
        integrations = []
        
        requirements = str(conversation_data.get('customer_requirements', '')).lower()
        
        if 'crm' in requirements:
            integrations.append("CRM system integration")
        if 'email' in requirements:
            integrations.append("Email service integration")
        if 'payment' in requirements:
            integrations.append("Payment gateway integration")
        if 'api' in requirements:
            integrations.append("REST API integrations")
        if 'database' in requirements:
            integrations.append("Database connectivity")
        
        if not integrations:
            integrations.append("Standard system integrations")
        
        return integrations

    def _fallback_generate_recommendations(self, solution_type: str, score: float) -> List[str]:
        """Generate strategic technical recommendations."""
        
        recommendations = []
        
        if score < 50:
            recommendations.append("Conduct detailed requirements workshop before development")
            recommendations.append("Consider phased delivery approach to manage complexity")
        else:
            recommendations.append("Well-defined requirements enable efficient development")
            recommendations.append("Implement agile development methodology")
        
        recommendations.append(f"Focus on {solution_type.lower()} best practices and patterns")
        recommendations.append("Plan for scalability from the initial architecture")
        recommendations.append("Implement comprehensive testing strategy")
        
        return recommendations[:5]  # Limit to 5 recommendations