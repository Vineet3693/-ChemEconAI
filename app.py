
import streamlit as st
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="ChemEconAI - Chemical Process Economics Calculator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path("assets/styles/custom.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Main page
st.title("🏭 ChemEconAI - Chemical Process Economics Calculator")
st.markdown("""
### Welcome to the AI-Powered Process Economics Platform

This comprehensive tool helps you analyze the economic viability of chemical processes with:

- **📊 Process Design & Material Balance**
- **💰 Capital & Operating Cost Analysis** 
- **🤖 AI-Powered Insights & Recommendations**
- **📈 Profitability & Sensitivity Analysis**
- **📋 Executive Report Generation**
""")

# Quick overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Process Types", "15+", "Batch & Continuous")
with col2:
    st.metric("Equipment Database", "500+", "Cost Correlations")
with col3:
    st.metric("AI Models", "3", "Groq-Powered")
with col4:
    st.metric("Industries", "10+", "Chemical Sectors")

# Getting started section
st.markdown("---")
st.markdown("### 🚀 Getting Started")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 1. Define Your Process
    - Input raw materials and products
    - Set production capacity
    - Choose process type (batch/continuous)
    
    #### 2. Calculate Costs
    - Equipment sizing and costing
    - Utility and labor requirements
    - Operating expense breakdown
    """)

with col2:
    st.markdown("""
    #### 3. Analyze Economics
    - NPV, IRR, and ROI calculations
    - Sensitivity analysis
    - Risk assessment
    
    #### 4. Get AI Insights
    - Process optimization suggestions
    - Cost reduction opportunities
    - Market analysis and benchmarks
    """)

# Navigation guide
st.markdown("---")
st.markdown("### 📱 Navigation")
st.info("Use the sidebar to navigate between different modules. Start with **Process Design** to input your process parameters.")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and powered by Groq AI | ChemEconAI v1.0*")
