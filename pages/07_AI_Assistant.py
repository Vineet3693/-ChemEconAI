
import streamlit as st
import os
from src.llm.groq_client import ProcessEconomicsGroq
import json

st.set_page_config(
    page_title="AI Assistant - ChemEconAI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Process Economics Assistant")
st.markdown("Get expert insights and recommendations for your chemical process economics!")

# Check for API key
if not (st.secrets.get("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") or os.getenv("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")):
    st.error("⚠️ **Groq API key not found!**")
    st.markdown("""
    To use the AI Assistant, please add your Groq API key:
    
    **For local development:**
    1. Create a `.env` file in the project root
    2. Add: `GROQ_API_KEY=your_api_key_here`
    
    **For Streamlit Cloud:**
    1. Go to your app settings
    2. Add `GROQ_API_KEY` to secrets
    
    Get your free API key at: https://console.groq.com
    """)
    st.stop()

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    return ProcessEconomicsGroq()

try:
    groq_client = get_groq_client()
except Exception as e:
    st.error(f"Failed to initialize AI client: {str(e)}")
    st.stop()

# Sidebar with process context
st.sidebar.header("📊 Process Context")
process_data = {}

with st.sidebar:
    st.markdown("*Current process information for AI context:*")
    
    # Get process data from session state if available
    if 'process_data' in st.session_state:
        process_info = st.session_state.process_data
        st.success("✅ Process data loaded from your design")
        
        process_data.update({
            'process_type': process_info.get('type', 'Not specified'),
            'production_rate': process_info.get('production_rate', 0),
            'raw_materials': [mat.get('name', 'Unknown') for mat in process_info.get('raw_materials', [])],
            'products': [prod.get('name', 'Unknown') for prod in process_info.get('products', [])],
            'investment': st.session_state.get('capital_costs', {}).get('total_capital_investment', 0)
        })
        
        # Display current process info
        st.write(f"**Process:** {process_data['process_type']}")
        st.write(f"**Production:** {process_data['production_rate']:,.0f} tons/year")
        if process_data['raw_materials']:
            st.write(f"**Materials:** {', '.join(process_data['raw_materials'][:3])}")
        if process_data['products']:
            st.write(f"**Products:** {', '.join(process_data['products'])}")
    else:
        st.warning("⚠️ No process data found")
        st.info("💡 Complete the Process Design step first for better AI insights")
        
        # Manual input if no process data
        process_data['process_type'] = st.selectbox(
            "Process Type",
            ["Batch", "Continuous", "Semi-batch"]
        )
        
        process_data['production_rate'] = st.number_input(
            "Production Rate (tons/year)",
            min_value=0.0,
            value=1000.0
        )
        
        process_data['investment'] = st.number_input(
            "Investment ($)",
            min_value=0.0,
            value=1000000.0
        )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "👋 Hi! I'm your AI Process Economics Assistant. I can help you with:\n\n• Process optimization strategies\n• Cost analysis and reduction\n• Economic evaluation insights\n• Industry benchmarks\n• Risk assessment\n\nWhat would you like to know about your chemical process?"
        }
    ]

# Quick action buttons
st.markdown("### 🚀 Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💰 Analyze Economics", help="Get insights on your economic calculations"):
        if 'calculations' in st.session_state and st.session_state.calculations:
            with st.spinner("🧠 Analyzing your economics..."):
                response = groq_client.analyze_economics(st.session_state.calculations)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"## 💰 Economic Analysis\n\n{response}"
                })
                st.rerun()
        else:
            st.warning("Complete the Profitability analysis first!")

with col2:
    if st.button("🔧 Optimize Costs", help="Get cost optimization suggestions"):
        if 'cost_breakdown' in st.session_state and st.session_state.cost_breakdown:
            with st.spinner("🔍 Finding optimization opportunities..."):
                response = groq_client.optimize_costs(st.session_state.cost_breakdown)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"## 🔧 Cost Optimization\n\n{response}"
                })
                st.rerun()
        else:
            st.warning("Complete the Operating Costs analysis first!")

with col3:
    if st.button("📋 Executive Summary", help="Generate executive summary"):
        with st.spinner("📝 Generating executive summary..."):
            summary_data = {
                'name': process_data.get('process_type', 'Chemical Process'),
                'investment': process_data.get('investment', 0),
                'npv': st.session_state.get('calculations', {}).get('npv', 0),
                'irr': st.session_state.get('calculations', {}).get('irr', 0),
                'payback': st.session_state.get('calculations', {}).get('payback_period', 0),
                'production_rate': process_data.get('production_rate', 0)
            }
            response = groq_client.generate_executive_summary(summary_data)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"## 📋 Executive Summary\n\n{response}"
            })
            st.rerun()

with col4:
    if st.button("🎯 Industry Benchmarks", help="Compare with industry standards"):
        question = f"What are the typical industry benchmarks for a {process_data.get('process_type', 'chemical')} process producing {process_data.get('production_rate', 1000)} tons/year? Compare my process economics with industry standards."
        with st.spinner("📊 Comparing with industry benchmarks..."):
            response = groq_client.get_process_advice(process_data, question)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"## 🎯 Industry Benchmarks\n\n{response}"
            })
            st.rerun()

# Display chat messages
st.markdown("### 💬 Chat with AI Assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about your process economics..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = groq_client.get_process_advice(process_data, prompt)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
            except Exception as e:
                error_msg = f"⚠️ Sorry, I encountered an error: {str(e)}"
                st.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

# Sidebar chat controls
with st.sidebar:
    st.markdown("---")
    st.markdown("### 💬 Chat Controls")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
        st.rerun()
    
    if st.button("💾 Export Chat"):
        chat_export = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="📁 Download Chat",
            data=chat_export,
            file_name=f"chemai_chat_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
    
    # Example questions
    st.markdown("### 💡 Example Questions")
    example_questions = [
        "How can I reduce my operating costs?",
        "Is my IRR acceptable for this industry?",
        "What are the main risks for my process?",
        "How does my payback period compare to industry standards?",
        "What process improvements should I consider?",
        "How sensitive is my NPV to raw material price changes?"
    ]
    
    for question in example_questions:
        if st.button(f"💬 {question}", key=f"example_{hash(question)}"):
            # Add to chat
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("🤔 Thinking..."):
                response = groq_client.get_process_advice(process_data, question)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Footer
st.markdown("---")
st.markdown("*💡 **Pro Tip:** The AI assistant works best when you've completed the Process Design and economic calculations first. This provides context for more accurate insights.*")
