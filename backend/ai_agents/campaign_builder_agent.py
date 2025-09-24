"""
AI Campaign Builder Agent

This agent analyzes historical lead generation data and provides intelligent campaign recommendations
using OpenAI to generate data-driven marketing strategies.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI


class CampaignBuilderAgent:
    """
    AI agent that analyzes historical campaign data and generates intelligent campaign recommendations.
    """
    
    def __init__(self):
        """Initialize the Campaign Builder Agent with OpenAI client."""
        
        # OpenAI configuration
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.fallback_enabled = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Campaign templates and patterns
        self.lead_sources = [
            "SEO", "Networking Event", "Summit Event", "Cold Outreach", "Referral",
            "Social Media", "Website Form", "Trade Show", "Partner Referral", "Content Marketing"
        ]
        
        self.solution_types = [
            "Web Application", "Mobile Application", "E-commerce Platform", "CRM System",
            "Data Analytics Platform", "AI/ML Platform", "Enterprise Software", "Cybersecurity",
            "Cloud Infrastructure", "Custom Integration"
        ]
        
        self.campaign_types = [
            "Lead Generation", "Brand Awareness", "Product Launch", "Customer Retention",
            "Market Expansion", "Thought Leadership", "Event Marketing", "Content Marketing"
        ]

    def analyze_historical_data(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze historical campaign and contact data to identify patterns and insights.
        
        Args:
            historical_data: Dictionary containing source metrics, solution metrics, trends, and summary data
            
        Returns:
            Dictionary with historical analysis insights
        """
        
        try:
            # Try AI analysis first
            return self._ai_analyze_historical_data(historical_data)
        except Exception as e:
            print(f"AI historical analysis failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based historical analysis")
                return self._fallback_analyze_historical_data(historical_data)
            else:
                raise e

    def generate_campaign_recommendations(self, campaign_goals: Dict[str, Any], 
                                        historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered campaign recommendations based on goals and historical data.
        
        Args:
            campaign_goals: User-specified campaign objectives and constraints
            historical_analysis: Results from historical data analysis
            
        Returns:
            Dictionary with comprehensive campaign recommendations
        """
        
        try:
            # Try AI recommendations first
            return self._ai_generate_campaign_recommendations(campaign_goals, historical_analysis)
        except Exception as e:
            print(f"AI campaign recommendations failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based campaign recommendations")
                return self._fallback_generate_campaign_recommendations(campaign_goals, historical_analysis)
            else:
                raise e

    def create_campaign_template(self, recommendations: Dict[str, Any], 
                               campaign_goals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive campaign template with specific activities and timelines.
        
        Args:
            recommendations: AI-generated campaign recommendations
            campaign_goals: User-specified campaign objectives
            
        Returns:
            Dictionary with detailed campaign template
        """
        
        try:
            # Try AI template generation first
            return self._ai_create_campaign_template(recommendations, campaign_goals)
        except Exception as e:
            print(f"AI template generation failed: {e}")
            if self.fallback_enabled:
                print("Falling back to rule-based template generation")
                return self._fallback_create_campaign_template(recommendations, campaign_goals)
            else:
                raise e

    def _ai_analyze_historical_data(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to analyze historical campaign data and identify patterns."""
        
        # Prepare the prompt with historical data
        prompt = self._build_historical_analysis_prompt(historical_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_historical_analysis_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=2500
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_historical_analysis_response(ai_response, historical_data)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _ai_generate_campaign_recommendations(self, campaign_goals: Dict[str, Any], 
                                            historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to generate intelligent campaign recommendations."""
        
        # Prepare the prompt with goals and analysis
        prompt = self._build_campaign_recommendations_prompt(campaign_goals, historical_analysis)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_campaign_recommendations_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,  # Slightly higher for creative recommendations
                max_tokens=3000
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_campaign_recommendations_response(ai_response, campaign_goals, historical_analysis)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _ai_create_campaign_template(self, recommendations: Dict[str, Any], 
                                   campaign_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to create a detailed campaign template."""
        
        # Prepare the prompt with recommendations and goals
        prompt = self._build_campaign_template_prompt(recommendations, campaign_goals)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_campaign_template_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for structured templates
                max_tokens=3500
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_campaign_template_response(ai_response, recommendations, campaign_goals)
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e

    def _get_historical_analysis_system_prompt(self) -> str:
        """Get the system prompt for historical data analysis."""
        return """You are an expert marketing data analyst specializing in B2B lead generation and campaign performance analysis. 

Your task is to analyze historical campaign data and identify key patterns, trends, and insights that can inform future campaign strategies.

Focus on:
1. Lead source performance patterns and conversion rates
2. Solution interest trends and market demand
3. Seasonal patterns and timing insights
4. Revenue and deal size patterns
5. Customer segment preferences
6. Channel effectiveness and ROI indicators

Provide actionable insights that can guide campaign planning and budget allocation decisions.

Return your analysis in a structured JSON format with clear categories and specific insights."""

    def _get_campaign_recommendations_system_prompt(self) -> str:
        """Get the system prompt for campaign recommendations."""
        return """You are an expert marketing strategist specializing in B2B campaign planning and lead generation optimization.

Your task is to generate intelligent, data-driven campaign recommendations based on historical performance data and specific campaign goals.

Focus on:
1. Target audience identification and segmentation
2. Optimal channel mix and budget allocation
3. Messaging strategies and content themes
4. Timeline and activity sequencing
5. Success metrics and KPIs
6. Risk mitigation and contingency planning

Provide specific, actionable recommendations that align with the campaign goals and leverage historical performance insights.

Return your recommendations in a structured JSON format with clear categories and specific guidance."""

    def _get_campaign_template_system_prompt(self) -> str:
        """Get the system prompt for campaign template creation."""
        return """You are an expert marketing operations specialist who creates comprehensive, executable campaign templates.

Your task is to transform campaign recommendations into a detailed, actionable campaign plan with specific activities, timelines, and deliverables.

Focus on:
1. Detailed activity breakdown with specific tasks
2. Timeline with milestones and deadlines
3. Resource requirements and team assignments
4. Budget allocation and cost estimates
5. Success metrics and measurement framework
6. Risk management and quality assurance

Create a comprehensive template that a marketing team can immediately execute.

Return your template in a structured JSON format with clear phases, activities, and specifications."""

    def _build_historical_analysis_prompt(self, historical_data: Dict[str, Any]) -> str:
        """Build the prompt for historical data analysis."""

        source_metrics = historical_data.get('source_metrics', [])
        solution_metrics = historical_data.get('solution_metrics', [])
        trend_data = historical_data.get('trend_data', [])
        summary = historical_data.get('summary', {})

        prompt = f"""
Analyze the following historical campaign and lead generation data:

SUMMARY METRICS:
- Total Leads: {summary.get('total_leads', 0)}
- Total Revenue: ${summary.get('total_revenue', 0):,.2f}
- Average Conversion Rate: {summary.get('avg_conversion_rate', 0):.1f}%
- Top Performing Source: {summary.get('top_source', 'N/A')}
- Date Range: {summary.get('date_range', 'N/A')}

LEAD SOURCE PERFORMANCE:
"""

        for source in source_metrics[:10]:  # Top 10 sources
            prompt += f"""
- {source.get('source', 'Unknown')}:
  * Total Leads: {source.get('total_leads', 0)}
  * Qualified Leads: {source.get('qualified_leads', 0)}
  * Deals: {source.get('deals', 0)}
  * Conversion Rate: {source.get('conversion_rate', 0):.1f}%
  * Total Revenue: ${source.get('total_revenue', 0):,.2f}
  * Avg Deal Size: ${source.get('avg_deal_size', 0):,.2f}
"""

        prompt += "\nSOLUTION INTEREST DISTRIBUTION:\n"
        for solution in solution_metrics[:10]:  # Top 10 solutions
            prompt += f"""
- {solution.get('solution', 'Unknown')}: {solution.get('leads', 0)} leads ({solution.get('percentage', 0):.1f}%)
"""

        prompt += "\nTREND DATA (Last 6 Months):\n"
        for trend in trend_data[-6:]:  # Last 6 months
            prompt += f"""
- {trend.get('month', 'Unknown')}: {trend.get('leads', 0)} leads, {trend.get('qualified', 0)} qualified, {trend.get('deals', 0)} deals, ${trend.get('revenue', 0):,.0f} revenue
"""

        prompt += """

Please analyze this data and provide insights on:
1. Top performing lead sources and why they work
2. Solution interest trends and market demand patterns
3. Seasonal patterns and optimal timing
4. Conversion rate patterns and optimization opportunities
5. Revenue patterns and deal size trends
6. Recommendations for future campaign focus

Format your response as a JSON object with structured insights."""

        return prompt

    def _build_campaign_recommendations_prompt(self, campaign_goals: Dict[str, Any],
                                             historical_analysis: Dict[str, Any]) -> str:
        """Build the prompt for campaign recommendations."""

        prompt = f"""
Based on the following campaign goals and historical analysis, generate intelligent campaign recommendations:

CAMPAIGN GOALS:
- Campaign Type: {campaign_goals.get('campaign_type', 'Lead Generation')}
- Target Solution: {campaign_goals.get('target_solution', 'Any')}
- Budget Range: ${campaign_goals.get('budget_min', 0):,.0f} - ${campaign_goals.get('budget_max', 0):,.0f}
- Timeline: {campaign_goals.get('timeline', 'Not specified')}
- Lead Target: {campaign_goals.get('lead_target', 0)} leads
- Revenue Target: ${campaign_goals.get('revenue_target', 0):,.0f}
- Geographic Focus: {campaign_goals.get('geographic_focus', 'Global')}
- Target Audience: {campaign_goals.get('target_audience', 'General B2B')}

HISTORICAL ANALYSIS INSIGHTS:
{json.dumps(historical_analysis, indent=2)}

Please provide specific recommendations for:
1. Target customer profiles and segmentation strategy
2. Optimal lead source mix and budget allocation
3. Messaging themes and content strategy
4. Channel strategy and activity mix
5. Timeline and campaign phases
6. Success metrics and KPIs
7. Risk factors and mitigation strategies

Format your response as a JSON object with actionable recommendations."""

        return prompt

    def _build_campaign_template_prompt(self, recommendations: Dict[str, Any],
                                      campaign_goals: Dict[str, Any]) -> str:
        """Build the prompt for campaign template creation."""

        prompt = f"""
Create a comprehensive campaign template based on these recommendations and goals:

CAMPAIGN GOALS:
{json.dumps(campaign_goals, indent=2)}

RECOMMENDATIONS:
{json.dumps(recommendations, indent=2)}

Please create a detailed campaign template with:
1. Campaign overview and objectives
2. Phase-by-phase breakdown with specific activities
3. Timeline with milestones and deadlines
4. Resource requirements and team assignments
5. Budget allocation by activity and channel
6. Content and creative requirements
7. Success metrics and measurement framework
8. Risk management and contingency plans
9. Quality assurance and approval processes
10. Post-campaign analysis and optimization

Format your response as a JSON object with a complete, executable campaign plan."""

        return prompt

    def _parse_historical_analysis_response(self, ai_response: str, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response for historical analysis."""

        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())

                # Add metadata
                parsed_response['analysis_timestamp'] = datetime.now().isoformat()
                parsed_response['data_period'] = historical_data.get('summary', {}).get('date_range', 'Unknown')
                parsed_response['confidence'] = 85.0  # AI confidence score

                return parsed_response
            else:
                raise ValueError("No JSON found in AI response")

        except Exception as e:
            print(f"Failed to parse AI historical analysis response: {e}")
            # Return structured fallback
            return self._fallback_analyze_historical_data(historical_data)

    def _parse_campaign_recommendations_response(self, ai_response: str, campaign_goals: Dict[str, Any],
                                               historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response for campaign recommendations."""

        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())

                # Add metadata
                parsed_response['recommendations_timestamp'] = datetime.now().isoformat()
                parsed_response['campaign_goals'] = campaign_goals
                parsed_response['confidence'] = 88.0  # AI confidence score

                return parsed_response
            else:
                raise ValueError("No JSON found in AI response")

        except Exception as e:
            print(f"Failed to parse AI recommendations response: {e}")
            # Return structured fallback
            return self._fallback_generate_campaign_recommendations(campaign_goals, historical_analysis)

    def _parse_campaign_template_response(self, ai_response: str, recommendations: Dict[str, Any],
                                        campaign_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response for campaign template."""

        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())

                # Add metadata
                parsed_response['template_timestamp'] = datetime.now().isoformat()
                parsed_response['template_version'] = '1.0'
                parsed_response['confidence'] = 90.0  # AI confidence score

                return parsed_response
            else:
                raise ValueError("No JSON found in AI response")

        except Exception as e:
            print(f"Failed to parse AI template response: {e}")
            # Return structured fallback
            return self._fallback_create_campaign_template(recommendations, campaign_goals)

    def _fallback_analyze_historical_data(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based historical data analysis."""

        source_metrics = historical_data.get('source_metrics', [])
        solution_metrics = historical_data.get('solution_metrics', [])
        summary = historical_data.get('summary', {})

        # Analyze top performing sources
        top_sources = sorted(source_metrics, key=lambda x: x.get('conversion_rate', 0), reverse=True)[:3]

        # Analyze solution demand
        top_solutions = sorted(solution_metrics, key=lambda x: x.get('leads', 0), reverse=True)[:3]

        # Calculate performance insights
        avg_conversion = summary.get('avg_conversion_rate', 0)
        total_revenue = summary.get('total_revenue', 0)

        return {
            'top_performing_sources': [
                {
                    'source': source.get('source', 'Unknown'),
                    'conversion_rate': source.get('conversion_rate', 0),
                    'total_leads': source.get('total_leads', 0),
                    'avg_deal_size': source.get('avg_deal_size', 0),
                    'performance_rating': 'High' if source.get('conversion_rate', 0) > avg_conversion else 'Medium'
                }
                for source in top_sources
            ],
            'solution_demand_trends': [
                {
                    'solution': solution.get('solution', 'Unknown'),
                    'leads': solution.get('leads', 0),
                    'percentage': solution.get('percentage', 0),
                    'market_demand': 'High' if solution.get('percentage', 0) > 15 else 'Medium'
                }
                for solution in top_solutions
            ],
            'key_insights': [
                f"Top performing source: {top_sources[0].get('source', 'Unknown')} with {top_sources[0].get('conversion_rate', 0):.1f}% conversion rate",
                f"Most demanded solution: {top_solutions[0].get('solution', 'Unknown')} with {top_solutions[0].get('percentage', 0):.1f}% of leads",
                f"Average conversion rate: {avg_conversion:.1f}%",
                f"Total revenue generated: ${total_revenue:,.2f}"
            ],
            'recommendations': [
                "Focus budget on top-performing lead sources",
                "Develop content targeting high-demand solutions",
                "Optimize conversion processes for underperforming sources",
                "Consider seasonal timing based on trend patterns"
            ],
            'analysis_timestamp': datetime.now().isoformat(),
            'confidence': 75.0
        }

    def _fallback_generate_campaign_recommendations(self, campaign_goals: Dict[str, Any],
                                                  historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based campaign recommendations."""

        campaign_type = campaign_goals.get('campaign_type', 'Lead Generation')
        target_solution = campaign_goals.get('target_solution', 'Any')
        budget_max = campaign_goals.get('budget_max', 50000)
        lead_target = campaign_goals.get('lead_target', 100)

        # Get top sources from historical analysis
        top_sources = historical_analysis.get('top_performing_sources', [])

        # Budget allocation based on performance
        budget_allocation = {}
        if top_sources:
            total_weight = sum(source.get('conversion_rate', 0) for source in top_sources[:5])
            for i, source in enumerate(top_sources[:5]):
                weight = source.get('conversion_rate', 0) / total_weight if total_weight > 0 else 0.2
                budget_allocation[source.get('source', f'Source_{i}')] = {
                    'percentage': weight * 100,
                    'budget': budget_max * weight,
                    'expected_leads': int(lead_target * weight)
                }

        return {
            'target_audience': {
                'primary_segment': 'B2B Decision Makers',
                'company_size': '50-500 employees',
                'industries': ['Technology', 'Manufacturing', 'Professional Services'],
                'job_titles': ['CEO', 'CTO', 'VP of Operations', 'Director']
            },
            'channel_strategy': {
                'primary_channels': [source.get('source', 'Unknown') for source in top_sources[:3]],
                'budget_allocation': budget_allocation,
                'channel_mix': 'Multi-channel approach focusing on proven performers'
            },
            'messaging_strategy': {
                'primary_theme': f'Innovative {target_solution} Solutions',
                'value_propositions': [
                    'Proven ROI and business impact',
                    'Expert implementation and support',
                    'Scalable and future-ready technology'
                ],
                'content_themes': [
                    'Case studies and success stories',
                    'Industry insights and trends',
                    'Technical thought leadership'
                ]
            },
            'timeline_recommendations': {
                'campaign_duration': '3 months',
                'phases': [
                    {'phase': 'Launch', 'duration': '2 weeks', 'focus': 'Setup and initial outreach'},
                    {'phase': 'Optimization', 'duration': '6 weeks', 'focus': 'Performance monitoring and adjustment'},
                    {'phase': 'Scale', 'duration': '4 weeks', 'focus': 'Scaling successful activities'}
                ]
            },
            'success_metrics': {
                'primary_kpis': [
                    f'Generate {lead_target} qualified leads',
                    f'Achieve {budget_max * 0.0001:.1f}% conversion rate',
                    f'Generate ${campaign_goals.get("revenue_target", budget_max * 5):,.0f} in pipeline'
                ],
                'tracking_metrics': [
                    'Cost per lead by channel',
                    'Lead quality scores',
                    'Conversion rates by source',
                    'Time to qualification'
                ]
            },
            'risk_mitigation': [
                'Diversify across multiple proven channels',
                'Monitor performance weekly and adjust quickly',
                'Maintain backup content and messaging options',
                'Set clear quality thresholds for lead acceptance'
            ],
            'recommendations_timestamp': datetime.now().isoformat(),
            'confidence': 78.0
        }

    def _fallback_create_campaign_template(self, recommendations: Dict[str, Any],
                                         campaign_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based campaign template creation."""

        timeline = recommendations.get('timeline_recommendations', {})
        budget_max = campaign_goals.get('budget_max', 50000)

        return {
            'campaign_overview': {
                'name': f"{campaign_goals.get('campaign_type', 'Lead Generation')} Campaign",
                'objective': f"Generate {campaign_goals.get('lead_target', 100)} qualified leads",
                'duration': timeline.get('campaign_duration', '3 months'),
                'budget': budget_max,
                'target_solution': campaign_goals.get('target_solution', 'Any')
            },
            'campaign_phases': [
                {
                    'phase_name': 'Planning & Setup',
                    'duration': '1 week',
                    'activities': [
                        'Finalize campaign messaging and creative assets',
                        'Set up tracking and analytics systems',
                        'Configure lead capture and nurturing workflows',
                        'Brief team members and assign responsibilities'
                    ],
                    'deliverables': ['Campaign brief', 'Creative assets', 'Tracking setup'],
                    'budget_allocation': budget_max * 0.1
                },
                {
                    'phase_name': 'Launch',
                    'duration': '2 weeks',
                    'activities': [
                        'Launch primary channel campaigns',
                        'Begin content distribution and outreach',
                        'Monitor initial performance metrics',
                        'Conduct daily performance reviews'
                    ],
                    'deliverables': ['Campaign launch', 'Initial performance report'],
                    'budget_allocation': budget_max * 0.3
                },
                {
                    'phase_name': 'Optimization',
                    'duration': '6 weeks',
                    'activities': [
                        'Analyze performance data and optimize campaigns',
                        'A/B test messaging and creative variations',
                        'Scale successful activities and pause underperformers',
                        'Conduct weekly performance reviews and adjustments'
                    ],
                    'deliverables': ['Weekly optimization reports', 'Performance analysis'],
                    'budget_allocation': budget_max * 0.5
                },
                {
                    'phase_name': 'Scale & Close',
                    'duration': '3 weeks',
                    'activities': [
                        'Scale top-performing campaigns and channels',
                        'Conduct final push for lead generation',
                        'Compile final campaign performance report',
                        'Document lessons learned and best practices'
                    ],
                    'deliverables': ['Final campaign report', 'Best practices documentation'],
                    'budget_allocation': budget_max * 0.1
                }
            ],
            'success_metrics': recommendations.get('success_metrics', {}),
            'team_requirements': [
                {'role': 'Campaign Manager', 'allocation': '100%'},
                {'role': 'Content Creator', 'allocation': '50%'},
                {'role': 'Data Analyst', 'allocation': '25%'},
                {'role': 'Sales Coordinator', 'allocation': '25%'}
            ],
            'template_timestamp': datetime.now().isoformat(),
            'template_version': '1.0',
            'confidence': 80.0
        }
