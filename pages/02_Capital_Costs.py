
import streamlit as st
import pandas as pd
import plotly.express as px
from src.economics.capital_cost import CapitalCostEstimator
from src.utils.formatters import format_currency
import json

st.set_page_config(
    page_title="Capital Costs - ChemEconAI",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Capital Cost Estimation")
st.markdown("Size and cost your process equipment to estimate total capital investment.")

# Initialize capital cost estimator
estimator = CapitalCostEstimator()

# Check if process data exists
if 'process_data' not in st.session_state or not st.session_state.process_data:
    st.warning("⚠️ **Process data not found!**")
    st.info("👈 Please complete the **Process Design** step first.")
    st.stop()

process_data = st.session_state.process_data

# Display process summary
with st.expander("📋 Process Summary", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Process Type", process_data.get('type', 'Unknown'))
        st.metric("Production Rate", f"{process_data.get('production_rate', 0):,.0f} tons/year")
    with col2:
        st.metric("Operating Hours", f"{process_data.get('operating_hours', 0):,.0f} hours/year")
        st.metric("Location", process_data.get('location', 'Not specified'))
    with col3:
        st.metric("Raw Materials", len(process_data.get('raw_materials', [])))
        st.metric("Products", len(process_data.get('products', [])))

# Equipment Selection and Sizing
st.header("⚙️ Equipment Selection & Sizing")

# Initialize equipment list in session state
if 'equipment_list' not in st.session_state:
    st.session_state.equipment_list = []

# Equipment input form
with st.expander("➕ Add Equipment", expanded=len(st.session_state.equipment_list) == 0):
    col1, col2 = st.columns(2)
    
    with col1:
        equipment_type = st.selectbox(
            "Equipment Type",
            ["reactor", "distillation_column", "heat_exchanger", "pump", "tank", "compressor", "mixer", "crystallizer", "dryer", "filter"],
            help="Select the type of equipment"
        )
        
        capacity = st.number_input(
            "Capacity",
            min_value=0.1,
            value=100.0,
            step=10.0,
            help="Equipment capacity (units depend on equipment type)"
        )
        
        equipment_material = st.selectbox(
            "Material of Construction",
            ["carbon_steel", "stainless_steel", "hastelloy"],
            help="Material affects cost and corrosion resistance"
        )
    
    with col2:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=20,
            value=1,
            help="Number of identical units"
        )
        
        equipment_id = st.text_input(
            "Equipment ID",
            value=f"{equipment_type.upper()}-001",
            help="Unique identifier for this equipment"
        )
        
        description = st.text_area(
            "Description",
            value="",
            help="Optional description of the equipment"
        )
    
    # Capacity units information
    capacity_units = {
        "reactor": "L (liters)",
        "distillation_column": "theoretical plates",
        "heat_exchanger": "m² (square meters)",
        "pump": "L/min (liters per minute)",
        "tank": "L (liters)",
        "compressor": "m³/h (cubic meters per hour)",
        "mixer": "L (liters)",
        "crystallizer": "L (liters)",
        "dryer": "kg/h (kilograms per hour)",
        "filter": "m² (square meters)"
    }
    
    st.info(f"💡 **Capacity units for {equipment_type}:** {capacity_units.get(equipment_type, 'Check documentation')}")
    
    if st.button("Add Equipment", type="primary"):
        if equipment_id and capacity > 0:
            # Check if ID already exists
            existing_ids = [eq.get('id', '') for eq in st.session_state.equipment_list]
            if equipment_id in existing_ids:
                st.error(f"Equipment ID '{equipment_id}' already exists!")
            else:
                st.session_state.equipment_list.append({
                    'type': equipment_type,
                    'capacity': capacity,
                    'material': equipment_material,
                    'quantity': quantity,
                    'id': equipment_id,
                    'description': description
                })
                st.success(f"✅ Added {equipment_id}")
                st.rerun()
        else:
            st.error("Please provide equipment ID and valid capacity!")

# Display current equipment list
if st.session_state.equipment_list:
    st.subheader("📋 Current Equipment List")
    
    # Create equipment dataframe for display
    equipment_df_data = []
    for i, eq in enumerate(st.session_state.equipment_list):
        equipment_df_data.append({
            'ID': eq['id'],
            'Type': eq['type'].replace('_', ' ').title(),
            'Capacity': eq['capacity'],
            'Material': eq['material'].replace('_', ' ').title(),
            'Quantity': eq['quantity'],
            'Description': eq.get('description', '')[:50] + ('...' if len(eq.get('description', '')) > 50 else '')
        })
    
    equipment_display_df = pd.DataFrame(equipment_df_data)
    st.dataframe(equipment_display_df, use_container_width=True, hide_index=True)
    
    # Equipment management buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear All Equipment"):
            st.session_state.equipment_list = []
            st.rerun()
    
    with col2:
        if st.button("📁 Load Template"):
            # Load equipment from process template
            template_file = f"data/templates/{process_data.get('type', 'batch').lower()}_process.json"
            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    st.session_state.equipment_list = template.get('equipment', [])
                    st.success("Template loaded successfully!")
                    st.rerun()
            except FileNotFoundError:
                st.warning("Template file not found")
    
    with col3:
        # Export equipment list
        equipment_json = json.dumps(st.session_state.equipment_list, indent=2)
        st.download_button(
            "📥 Export Equipment List",
            equipment_json,
            file_name="equipment_list.json",
            mime="application/json"
        )

# Cost Calculation Section
if st.session_state.equipment_list:
    st.header("💰 Cost Calculation")
    
    # Calculate equipment costs
    try:
        equipment_costs = estimator.calculate_total_equipment_cost(st.session_state.equipment_list)
        installed_costs = estimator.calculate_installed_cost(equipment_costs)
        
        # Plant type selection for capital estimation
        plant_type = st.selectbox(
            "Plant Type",
            ["chemical", "pharmaceutical"],
            help="Plant type affects indirect cost factors"
        )
        
        total_installed_cost = installed_costs['total_installed_cost']
        capital_breakdown = estimator.estimate_total_capital_investment(total_installed_cost, plant_type)
        
        # Display cost breakdown
        st.subheader("📊 Cost Breakdown")
        
        # Equipment costs table
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Equipment Costs**")
            equipment_cost_data = []
            for eq_id, cost_data in equipment_costs.items():
                if eq_id != 'total_equipment_cost':
                    if isinstance(cost_data, dict):
                        equipment_cost_data.append({
                            'Equipment': eq_id.replace('_', ' ').title(),
                            'Unit Cost': format_currency(cost_data['unit_cost']),
                            'Quantity': cost_data['quantity'],
                            'Total Cost': format_currency(cost_data['total_cost'])
                        })
            
            if equipment_cost_data:
                eq_cost_df = pd.DataFrame(equipment_cost_data)
                st.dataframe(eq_cost_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Capital Investment Summary**")
            capital_summary = pd.DataFrame([
                ['Installed Equipment Cost', format_currency(capital_breakdown['installed_equipment_cost'])],
                ['Engineering & Design', format_currency(capital_breakdown['engineering_cost'])],
                ['Construction & Installation', format_currency(capital_breakdown['construction_cost'])],
                ['Contingency', format_currency(capital_breakdown['contingency'])],
                ['Fixed Capital Investment', format_currency(capital_breakdown['fixed_capital_investment'])],
                ['Working Capital', format_currency(capital_breakdown['working_capital'])],
                ['**Total Capital Investment**', f"**{format_currency(capital_breakdown['total_capital_investment'])}**"]
            ], columns=['Component', 'Cost'])
            
            st.dataframe(capital_summary, use_container_width=True, hide_index=True)
        
        # Capital cost metrics
        st.subheader("📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Capital Investment",
                format_currency(capital_breakdown['total_capital_investment'])
            )
        
        with col2:
            capex_per_ton = capital_breakdown['total_capital_investment'] / process_data.get('production_rate', 1)
            st.metric(
                "CAPEX per Annual Ton",
                format_currency(capex_per_ton)
            )
        
        with col3:
            equipment_fraction = (equipment_costs['total_equipment_cost'] / capital_breakdown['total_capital_investment']) * 100
            st.metric(
                "Equipment Cost Fraction",
                f"{equipment_fraction:.1f}%"
            )
        
        with col4:
            installed_factor = total_installed_cost / equipment_costs['total_equipment_cost']
            st.metric(
                "Installation Factor",
                f"{installed_factor:.1f}x"
            )
        
        # Capital cost visualization
        st.subheader("📊 Cost Visualization")
        
        # Pie chart of capital cost breakdown
        cost_breakdown_data = {
            'Equipment': equipment_costs['total_equipment_cost'],
            'Installation': total_installed_cost - equipment_costs['total_equipment_cost'],
            'Engineering': capital_breakdown['engineering_cost'],
            'Construction': capital_breakdown['construction_cost'],
            'Contingency': capital_breakdown['contingency'],
            'Working Capital': capital_breakdown['working_capital']
        }
        
        fig = px.pie(
            values=list(cost_breakdown_data.values()),
            names=list(cost_breakdown_data.keys()),
            title="Capital Cost Breakdown"
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        # Equipment cost comparison
        if len(st.session_state.equipment_list) > 1:
            equipment_comparison_data = []
            for eq_id, cost_data in equipment_costs.items():
                if eq_id != 'total_equipment_cost' and isinstance(cost_data, dict):
                    equipment_comparison_data.append({
                        'Equipment': eq_id.replace('_', ' ').title(),
                        'Total Cost': cost_data['total_cost']
                    })
            
            if equipment_comparison_data:
                eq_comp_df = pd.DataFrame(equipment_comparison_data)
                fig2 = px.bar(
                    eq_comp_df,
                    x='Equipment',
                    y='Total Cost',
                    title='Equipment Cost Comparison'
                )
                fig2.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
        
        # Save capital costs to session state
        st.session_state.capital_costs = capital_breakdown
        st.session_state.equipment_costs = equipment_costs
        
        # Success message
        if st.button("💾 Save Capital Cost Data", type="primary"):
            st.success("✅ Capital cost data saved successfully!")
            st.info("👉 Go to **Operating Costs** to continue with operating expense analysis.")
        
    except Exception as e:
        st.error(f"❌ Error calculating costs: {str(e)}")

else:
    st.info("➕ Add equipment to calculate capital costs")

# Cost estimation tips
with st.expander("💡 Cost Estimation Tips"):
    st.markdown("""
    **Equipment Sizing Guidelines:**
    - **Reactors**: Size based on residence time and production rate
    - **Distillation**: Number of theoretical plates affects separation efficiency
    - **Heat Exchangers**: Size based on heat duty and temperature differences
    - **Pumps**: Size based on flow rate and pressure requirements
    - **Tanks**: Size for storage time (typically 1-7 days of production)
    
    **Material Selection:**
    - **Carbon Steel**: Lowest cost, suitable for non-corrosive services
    - **Stainless Steel**: Higher cost, good corrosion resistance
    - **Hastelloy**: Highest cost, excellent corrosion resistance
    
    **Cost Factors:**
    - Equipment costs scale with capacity using power law (typically 0.6-0.8)
    - Installation factors vary by equipment complexity (2-5x equipment cost)
    - Location factors affect construction costs (Gulf Coast = 1.0 baseline)
    """)
