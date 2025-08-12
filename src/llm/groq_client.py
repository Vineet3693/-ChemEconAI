
"""
Groq API integration for ChemEconAI
"""

import os
from groq import Groq
import streamlit as st
from typing import Dict, List, Optional
import json

class ProcessEconomicsGroq:
    """
    Groq AI client for chemical process economics insights
    """
    
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("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") or st.secrets.get("GROQ_API_KEY")
        )
        self.model = "llama3-8b-8192"  # Fast and capable model
        
    def get_process_advice(self, process_data: Dict, question: str) -> str:
        """
        Get AI advice on process economics
        
        Args:
            process_data: Dictionary with process parameters
            question: User's question
            
        Returns:
            AI response with advice
        """
        context = self._build_process_context(process_data)
        
        prompt = f"""
You are an expert Chemical Process Economics advisor with 20+ years of industry experience.

PROCESS DATA:
{context}

USER QUESTION: {question}

Please provide:
1. Direct answer to the question
2. Specific recommendations with numbers where possible
3. Key considerations and trade-offs
4. Industry benchmarks or typical ranges
5. Potential risks and opportunities

Be concise, practical, and data-driven. Use specific chemical engineering terminology.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert chemical process economics consultant with deep industry knowledge."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error getting AI advice: {str(e)}"
    
    def analyze_economics(self, calculations: Dict) -> str:
        """
        Analyze economic calculations and provide insights
        """
        prompt = f"""
Analyze these chemical process economics calculations:

NPV: ${calculations.get('npv', 0):,.2f}
IRR: {calculations.get('irr', 0):.2f}%
Payback Period: {calculations.get('payback', 0):.1f} years
ROI: {calculations.get('roi', 0):.2f}%
Capital Cost: ${calculations.get('capex', 0):,.2f}
Annual Operating Cost: ${calculations.get('opex', 0):,.2f}
Annual Revenue: ${calculations.get('revenue', 0):,.2f}

Provide:
1. Overall investment attractiveness (1-10 scale with reasoning)
2. Key financial strengths and weaknesses
3. Comparison to typical chemical industry standards
4. Top 3 specific improvement recommendations
5. Major risk factors to monitor

Be specific and actionable in your analysis.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are analyzing chemical process economics. Be specific about industry benchmarks and provide actionable insights."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error analyzing economics: {str(e)}"
    
    def optimize_costs(self, cost_breakdown: Dict) -> str:
        """
        Suggest cost optimization strategies
        """
        prompt = f"""
Cost breakdown for chemical process:
{json.dumps(cost_breakdown, indent=2)}

Identify the top 5 cost optimization opportunities with:
1. Specific cost category to target
2. Potential savings percentage (be realistic)
3. Implementation difficulty (Low/Medium/High)
4. Implementation timeline (weeks/months)
5. Required actions and investments

Focus on proven chemical industry strategies. Consider:
- Process intensification
- Heat integration
- Raw material substitution
- Yield improvements
- Utility optimization
- Automation opportunities
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a cost optimization expert for chemical processes with knowledge of proven industry strategies."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error optimizing costs: {str(e)}"
    
    def generate_executive_summary(self, project_data: Dict) -> str:
        """
        Generate executive summary for investment decision
        """
        prompt = f"""
Generate a professional executive summary for this chemical process investment:

Project: {project_data.get('name', 'Chemical Process Investment')}
Investment: ${project_data.get('investment', 0):,.2f}
NPV: ${project_data.get('npv', 0):,.2f}
IRR: {project_data.get('irr', 0):.1f}%
Payback: {project_data.get('payback', 0):.1f} years
Production: {project_data.get('production_rate', 0)} tons/year

Create a 200-300 word executive summary for C-suite decision makers covering:
1. Project overview and strategic fit
2. Financial highlights and value proposition
3. Clear investment recommendation (Approve/Reject/Modify)
4. Key risks and mitigation strategies
5. Next steps and timeline

Write professionally for executives making multi-million dollar decisions.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are writing for C-suite executives. Be professional, concise, and decisive."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=512
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error generating summary: {str(e)}"
    
    def compare_alternatives(self, alternatives: List[Dict]) -> str:
        """
        Compare multiple process alternatives
        """
        comparison_data = ""
        for i, alt in enumerate(alternatives):
            comparison_data += f"\nAlternative {i+1}: {alt.get('name', f'Option {i+1}')}\n"
            comparison_data += f"- NPV: ${alt.get('npv', 0):,.2f}\n"
            comparison_data += f"- IRR: {alt.get('irr', 0):.1f}%\n"
            comparison_data += f"- Payback: {alt.get('payback', 0):.1f} years\n"
            comparison_data += f"- CAPEX: ${alt.get('capex', 0):,.2f}\n"
        
        prompt = f"""
Compare these chemical process alternatives:
{comparison_data}

Provide:
1. Ranking with clear rationale
2. Trade-off analysis between options
3. Risk comparison
4. Recommendation for different scenarios (risk-averse vs aggressive growth)
5. Decision criteria that matter most

Consider both financial metrics and strategic factors.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are comparing investment alternatives. Consider both quantitative and qualitative factors."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error comparing alternatives: {str(e)}"
    
    def _build_process_context(self, data: Dict) -> str:
        """
        Build formatted context from process data
        """
        context = []
        
        if 'process_type' in data:
            context.append(f"Process Type: {data['process_type']}")
        if 'production_rate' in data:
            context.append(f"Production Rate: {data['production_rate']} tons/year")
        if 'raw_materials' in data:
            materials = [mat if isinstance(mat, str) else mat.get('name', 'Unknown') 
                        for mat in data['raw_materials']]
            context.append(f"Raw Materials: {', '.join(materials)}")
        if 'products' in data:
            context.append(f"Products: {', '.join(data['products'])}")
        if 'investment' in data:
            context.append(f"Total Investment: ${data['investment']:,.2f}")
        if 'operating_hours' in data:
            context.append(f"Operating Hours: {data['operating_hours']} hours/year")
        
        return '\n'.join(context) if context else "No specific process data provided"
