
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from src.economics.profitability import ProfitabilityAnalyzer
from src.utils.formatters import format_currency, format_percentage
from src.utils.validators import validate_economic_inputs, ValidationError

st.set_page_config(
    page_title="Profitability Analysis - ChemEconAI",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Profitability Analysis")
st.markdown("Evaluate the financial viability of your chemical process investment.")

# Check prerequisites
missing_data = []
if 'process_data' not in st.session_state or not st.session_state.process_data:
    missing_data.append("Process Design")
if 'capital_costs' not in st.session_state or not st.session_state.capital_costs:
    missing_data.append("Capital Costs")
if 'operating_costs' not in st.session_state or not st.session_state.operating_costs:
    missing_data.append("Operating Costs")

if missing_data:
    st.warning(f"⚠️ **Missing Required Data:** {', '.join(missing_data)}")
    st.info("👈 Please complete the previous steps first.")
    
    # Allow manual input for testing
    st.markdown("---")
    st.markdown("### 🧪 Manual Input (for testing)")
    with st.expander("Enter Manual Data"):
        manual_revenue = st.number_input("Annual Revenue ($)", value=5000000.0)
        manual_opex = st.number_input("Annual Operating Costs ($)", value=3000000.0)
        manual_capex = st.number_input("Capital Investment ($)", value=10000000.0)
        
        if st.button("Use Manual Data"):
            st.session_state.manual_data = {
                'revenue': manual_revenue,
                'opex': manual_opex,
                'capex': manual_capex
            }

# Get data from previous steps or manual input
if 'manual_data' in st.session_state:
    annual_revenue = st.session_state.manual_data['revenue']
    annual_operating_costs = st.session_state.manual_data['opex']
    capital_investment = st.session_state.manual_data['capex']
    st.info("📝 Using manual input data")
else:
    if missing_data:
        st.stop()
    
    # Calculate revenue from process data
    process_data = st.session_state.process_data
    products = process_data.get('products', [])
    production_rate = process_data.get('production_rate', 1000)
    
    annual_revenue = 0
    for product in products:
        product_rate = production_rate * product['yield'] / 100  # tons/year
        product_revenue = product_rate * product['price'] * 1000  # Convert tons to kg
        annual_revenue += product_revenue
    
    # Get costs from previous calculations
    annual_operating_costs = st.session_state.operating_costs.get('total_annual_operating_cost', 0)
    capital_investment = st.session_state.capital_costs.get('total_capital_investment', 0)

# Initialize profitability analyzer
analyzer = ProfitabilityAnalyzer()

# Financial Parameters Input
st.header("💼 Financial Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Project Parameters")
    project_lifetime = st.number_input(
        "Project Lifetime (years)",
        min_value=5,
        max_value=50,
        value=20,
        help="Economic life of the project"
    )
    
    discount_rate = st.number_input(
        "Discount Rate (%)",
        min_value=5.0,
        max_value=25.0,
        value=12.0,
        step=0.5,
        help="Required rate of return (WACC)"
    ) / 100
    
    tax_rate = st.number_input(
        "Tax Rate (%)",
        min_value=0.0,
        max_value=50.0,
        value=30.0,
        step=1.0,
        help="Corporate tax rate"
    ) / 100

with col2:
    st.subheader("Current Values")
    st.metric("Annual Revenue", format_currency(annual_revenue))
    st.metric("Annual Operating Costs", format_currency(annual_operating_costs))
    st.metric("Capital Investment", format_currency(capital_investment))
    
    gross_profit = annual_revenue - annual_operating_costs
    st.metric("Gross Annual Profit", format_currency(gross_profit))

with col3:
    st.subheader("Additional Parameters")
    salvage_value_percent = st.number_input(
        "Salvage Value (% of CAPEX)",
        min_value=0.0,
        max_value=20.0,
        value=10.0,
        help="Equipment value at end of project life"
    )
    
    salvage_value = capital_investment * (salvage_value_percent / 100)
    
    working_capital_recovery = st.checkbox(
        "Recover Working Capital",
        value=True,
        help="Recover working capital at end of project"
    )
    
    inflation_rate = st.number_input(
        "Inflation Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        help="Annual inflation rate for costs/revenues"
    ) / 100

# Calculate Profitability
if st.button("🚀 Calculate Profitability", type="primary"):
    try:
        # Validate inputs
        economic_inputs = {
            'discount_rate': discount_rate * 100,
            'project_lifetime': project_lifetime,
            'capital_investment': capital_investment
        }
        
        validated_inputs = validate_economic_inputs(economic_inputs)
        
        # Perform profitability analysis
        results = analyzer.analyze_profitability(
            capital_investment=capital_investment,
            annual_revenue=annual_revenue,
            annual_operating_costs=annual_operating_costs,
            project_lifetime=project_lifetime,
            discount_rate=discount_rate,
            tax_rate=tax_rate,
            salvage_value=salvage_value
        )
        
        # Store results in session state
        st.session_state.calculations = results
        
        # Display Results
        st.header("📊 Profitability Results")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            npv_color = "normal" if results['npv'] > 0 else "inverse"
            st.metric(
                "Net Present Value",
                format_currency(results['npv']),
                help="NPV > 0 indicates profitable project"
            )
        
        with col2:
            irr_color = "normal" if results['irr'] > discount_rate * 100 else "inverse"
            st.metric(
                "Internal Rate of Return",
                format_percentage(results['irr']),
                help=f"IRR > {discount_rate*100:.1f}% indicates acceptable return"
            )
        
        with col3:
            st.metric(
                "Payback Period",
                f"{results['payback_period']:.1f} years",
                help="Time to recover initial investment"
            )
        
        with col4:
            st.metric(
                "Return on Investment",
                format_percentage(results['roi']),
                help="Annual return on investment"
            )
        
        # Additional metrics
        st.subheader("📋 Additional Financial Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Profitability Index",
                f"{results['profitability_index']:.2f}",
                help="NPV per dollar invested (>1.0 is good)"
            )
        
        with col2:
            st.metric(
                "Annual Cash Flow",
                format_currency(results['annual_cash_flow']),
                help="Average annual cash flow"
            )
        
        with col3:
            break_even_years = capital_investment / results['annual_cash_flow'] if results['annual_cash_flow'] > 0 else float('inf')
            st.metric(
                "Simple Payback",
                f"{break_even_years:.1f} years",
                help="Simple payback period (undiscounted)"
            )
        
        # Investment Decision
        st.subheader("🎯 Investment Decision")
        
        decision_score = 0
        decision_factors = []
        
        if results['npv'] > 0:
            decision_score += 3
            decision_factors.append("✅ Positive NPV")
        else:
            decision_factors.append("❌ Negative NPV")
        
        if results['irr'] > discount_rate * 100:
            decision_score += 3
            decision_factors.append(f"✅ IRR ({results['irr']:.1f}%) > Required Return ({discount_rate*100:.1f}%)")
        else:
            decision_factors.append(f"❌ IRR ({results['irr']:.1f}%) < Required Return ({discount_rate*100:.1f}%)")
        
        if results['payback_period'] < project_lifetime / 2:
            decision_score += 2
            decision_factors.append(f"✅ Reasonable Payback Period ({results['payback_period']:.1f} years)")
        else:
            decision_factors.append(f"⚠️ Long Payback Period ({results['payback_period']:.1f} years)")
        
        if results['profitability_index'] > 1.2:
            decision_score += 2
            decision_factors.append(f"✅ Strong Profitability Index ({results['profitability_index']:.2f})")
        elif results['profitability_index'] > 1.0:
            decision_score += 1
            decision_factors.append(f"✅ Acceptable Profitability Index ({results['profitability_index']:.2f})")
        else:
            decision_factors.append(f"❌ Poor Profitability Index ({results['profitability_index']:.2f})")
        
        # Decision recommendation
        if decision_score >= 8:
            decision = "🟢 **STRONG RECOMMENDATION: APPROVE**"
            decision_color = "normal"
        elif decision_score >= 5:
            decision = "🟡 **CONDITIONAL APPROVAL** (with risk mitigation)"
            decision_color = "normal"
        else:
            decision = "🔴 **RECOMMENDATION: REJECT**"
            decision_color = "inverse"
        
        st.markdown(f"### {decision}")
        
        for factor in decision_factors:
            st.markdown(f"- {factor}")
        
        # Cash Flow Analysis
        st.subheader("💰 Cash Flow Analysis")
        
        # Create cash flow projection
        years = list(range(0, project_lifetime + 1))
        cash_flows = [-capital_investment]  # Initial investment
        
        for year in range(1, project_lifetime + 1):
            # Apply inflation
            inflated_revenue = annual_revenue * (1 + inflation_rate) ** (year - 1)
            inflated_costs = annual_operating_costs * (1 + inflation_rate) ** (year - 1)
            
            annual_cf = results['annual_cash_flow']
            if year == project_lifetime and working_capital_recovery:
                annual_cf += st.session_state.capital_costs.get('working_capital', 0)
            
            cash_flows.append(annual_cf)
        
        # Create cash flow dataframe
        cf_df = pd.DataFrame({
            'Year': years,
            'Cash Flow': cash_flows,
            'Cumulative Cash Flow': np.cumsum(cash_flows)
        })
        
        # Cash flow chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=cf_df['Year'],
            y=cf_df['Cash Flow'],
            name='Annual Cash Flow',
            marker_color=['red' if x < 0 else 'green' for x in cf_df['Cash Flow']]
        ))
        
        fig.add_trace(go.Scatter(
            x=cf_df['Year'],
            y=cf_df['Cumulative Cash Flow'],
            mode='lines+markers',
            name='Cumulative Cash Flow',
            line=dict(color='blue', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Project Cash Flow Analysis',
            xaxis_title='Year',
            yaxis_title='Annual Cash Flow ($)',
            yaxis2=dict(
                title='Cumulative Cash Flow ($)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cash flow table
        cf_df['Cash Flow ($M)'] = cf_df['Cash Flow'] / 1e6
        cf_df['Cumulative CF ($M)'] = cf_df['Cumulative Cash Flow'] / 1e6
        
        st.dataframe(
            cf_df[['Year', 'Cash Flow ($M)', 'Cumulative CF ($M)']].round(2),
            use_container_width=True,
            hide_index=True
        )
        
        # Sensitivity Analysis Section
        st.subheader("📊 Sensitivity Analysis")
        
        sensitivity_params = st.multiselect(
            "Select Parameters for Sensitivity Analysis",
            ['annual_revenue', 'annual_operating_costs', 'capital_investment', 'discount_rate'],
            default=['annual_revenue', 'annual_operating_costs']
        )
        
        if sensitivity_params and st.button("Run Sensitivity Analysis"):
            sensitivity_ranges = {}
            for param in sensitivity_params:
                sensitivity_ranges[param] = [-20, -10, -5, 0, 5, 10, 20]
            
            base_parameters = {
                'capital_investment': capital_investment,
                'annual_revenue': annual_revenue,
                'annual_operating_costs': annual_operating_costs,
                'project_lifetime': project_lifetime,
                'discount_rate': discount_rate,
                'tax_rate': tax_rate,
                'salvage_value': salvage_value
            }
            
            sensitivity_results = analyzer.sensitivity_analysis(base_parameters, sensitivity_ranges)
            
            # Plot sensitivity results
            fig_sens = px.line(
                sensitivity_results,
                x='change_percent',
                y='npv',
                color='parameter',
                title='NPV Sensitivity Analysis',
                labels={'change_percent': 'Parameter Change (%)', 'npv': 'NPV ($)'}
            )
            
            fig_sens.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig_sens, use_container_width=True)
            
            # Sensitivity table
            pivot_table = sensitivity_results.pivot(index='change_percent', columns='parameter', values='npv')
            st.dataframe(pivot_table.round(0), use_container_width=True)
        
        # Success message
        st.success("✅ Profitability analysis completed successfully!")
        st.info("👉 Go to **AI Assistant** for insights on your results, or **Reports** to generate documentation.")
        
    except ValidationError as e:
        st.error(f"❌ Validation Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error in profitability analysis: {str(e)}")

# Industry Benchmarks
with st.expander("📊 Industry Benchmarks"):
    st.markdown("""
    **Typical Chemical Industry Benchmarks:**
    
    | Metric | Good | Acceptable | Poor |
    |--------|------|------------|------|
    | IRR | >20% | 15-20% | <15% |
    | Payback Period | <3 years | 3-5 years | >5 years |
    | NPV/Investment | >50% | 20-50% | <20% |
    | Profitability Index | >1.5 | 1.2-1.5 | <1.2 |
    
    **Factors affecting profitability:**
    - Market volatility and competition
    - Raw material price fluctuations
    - Regulatory changes
    - Technology obsolescence
    - Economic cycles
    """)

# Risk Assessment
with st.expander("⚠️ Risk Assessment"):
    st.markdown("""
    **Key Financial Risks:**
    
    1. **Market Risk**: Product price volatility
    2. **Cost Risk**: Raw material and utility cost increases
    3. **Volume Risk**: Lower than expected production/sales
    4. **Technology Risk**: Process performance issues
    5. **Regulatory Risk**: Environmental or safety regulations
    6. **Economic Risk**: Interest rate and inflation changes
    
    **Risk Mitigation Strategies:**
    - Long-term supply contracts
    - Product diversification
    - Flexible plant design
    - Insurance coverage
    - Scenario planning
    """)
