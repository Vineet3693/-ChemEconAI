
import streamlit as st
import pandas as pd
import json
from src.utils.validators import validate_process_parameters, ValidationError
from src.process.mass_balance import MaterialBalanceCalculator
from src.utils.formatters import format_technical_units

st.set_page_config(
    page_title="Process Design - ChemEconAI",
    page_icon="⚗️",
    layout="wide"
)

st.title("⚗️ Process Design & Material Balance")
st.markdown("Define your chemical process parameters and calculate material balances.")

# Initialize session state
if 'process_data' not in st.session_state:
    st.session_state.process_data = {}

# Main input form
with st.container():
    st.header("🏗️ Process Definition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Parameters")
        
        process_name = st.text_input("Process Name", value="My Chemical Process")
        
        process_type = st.selectbox(
            "Process Type",
            ["Batch", "Continuous", "Semi-batch"],
            help="Select the type of chemical process"
        )
        
        production_rate = st.number_input(
            "Production Rate (tons/year)",
            min_value=0.1,
            value=1000.0,
            step=100.0,
            help="Annual production capacity"
        )
        
        operating_hours = st.number_input(
            "Operating Hours (hours/year)",
            min_value=1000,
            max_value=8760,
            value=8000,
            step=100,
            help="Annual operating hours"
        )
        
        plant_location = st.selectbox(
            "Plant Location",
            ["USA - Gulf Coast", "USA - Northeast", "Europe - Germany", 
             "Asia - Singapore", "Asia - China", "Other"],
            help="Plant location affects utility costs and labor rates"
        )
    
    with col2:
        st.subheader("Process Conditions")
        
        operating_temperature = st.number_input(
            "Operating Temperature (°C)",
            min_value=-50.0,
            max_value=500.0,
            value=25.0,
            help="Main process operating temperature"
        )
        
        operating_pressure = st.number_input(
            "Operating Pressure (bar)",
            min_value=0.1,
            max_value=100.0,
            value=1.0,
            help="Main process operating pressure"
        )
        
        process_complexity = st.select_slider(
            "Process Complexity",
            options=["Simple", "Moderate", "Complex", "Very Complex"],
            value="Moderate",
            help="Complexity affects capital and operating costs"
        )

# Raw Materials Section
st.header("🧪 Raw Materials")

# Initialize raw materials in session state
if 'raw_materials' not in st.session_state:
    st.session_state.raw_materials = []

col1, col2 = st.columns([3, 1])

with col1:
    with st.expander("Add Raw Material", expanded=len(st.session_state.raw_materials) == 0):
        material_name = st.text_input("Material Name")
        material_price = st.number_input("Price ($/kg)", min_value=0.0, value=1.0, step=0.1)
        consumption_rate = st.number_input("Consumption Rate (kg/ton product)", min_value=0.0, value=100.0)
        
        if st.button("Add Material"):
            if material_name:
                st.session_state.raw_materials.append({
                    'name': material_name,
                    'price': material_price,
                    'consumption_rate': consumption_rate
                })
                st.success(f"Added {material_name}")
                st.rerun()

with col2:
    if st.session_state.raw_materials and st.button("🗑️ Clear All Materials"):
        st.session_state.raw_materials = []
        st.rerun()

# Display current materials
if st.session_state.raw_materials:
    materials_df = pd.DataFrame(st.session_state.raw_materials)
    materials_df['Annual Cost ($)'] = (materials_df['price'] * 
                                     materials_df['consumption_rate'] * 
                                     production_rate)
    
    st.dataframe(
        materials_df,
        use_container_width=True,
        hide_index=True
    )
    
    total_material_cost = materials_df['Annual Cost ($)'].sum()
    st.metric("Total Raw Material Cost", f"${total_material_cost:,.2f}/year")

# Products Section
st.header("📦 Products")

if 'products' not in st.session_state:
    st.session_state.products = []

col1, col2 = st.columns([3, 1])

with col1:
    with st.expander("Add Product", expanded=len(st.session_state.products) == 0):
        product_name = st.text_input("Product Name")
        product_price = st.number_input("Selling Price ($/kg)", min_value=0.0, value=5.0, step=0.1)
        yield_percentage = st.number_input("Yield (%)", min_value=1.0, max_value=100.0, value=90.0)
        
        if st.button("Add Product"):
            if product_name:
                st.session_state.products.append({
                    'name': product_name,
                    'price': product_price,
                    'yield': yield_percentage
                })
                st.success(f"Added {product_name}")
                st.rerun()

with col2:
    if st.session_state.products and st.button("🗑️ Clear All Products"):
        st.session_state.products = []
        st.rerun()

# Display current products
if st.session_state.products:
    products_df = pd.DataFrame(st.session_state.products)
    products_df['Production Rate (tons/year)'] = production_rate * products_df['yield'] / 100
    products_df['Annual Revenue ($)'] = (products_df['Production Rate (tons/year)'] * 
                                       products_df['price'] * 1000)  # Convert tons to kg
    
    st.dataframe(
        products_df,
        use_container_width=True,
        hide_index=True
    )
    
    total_revenue = products_df['Annual Revenue ($)'].sum()
    st.metric("Total Annual Revenue", f"${total_revenue:,.2f}/year")

# Process Summary
st.header("📊 Process Summary")

if st.session_state.raw_materials and st.session_state.products:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Production Rate", 
            format_technical_units(production_rate, "tons/year")
        )
    
    with col2:
        st.metric(
            "Raw Material Cost", 
            f"${total_material_cost:,.0f}/year"
        )
    
    with col3:
        st.metric(
            "Revenue", 
            f"${total_revenue:,.0f}/year"
        )
    
    with col4:
        gross_margin = ((total_revenue - total_material_cost) / total_revenue * 100) if total_revenue > 0 else 0
        st.metric(
            "Gross Margin", 
            f"{gross_margin:.1f}%"
        )

# Save process data
if st.button("💾 Save Process Data", type="primary"):
    try:
        # Validate inputs
        process_params = {
            'process_type': process_type.lower(),
            'production_rate': production_rate,
            'operating_hours': operating_hours
        }
        
        validated_params = validate_process_parameters(process_params)
        
        # Store in session state
        st.session_state.process_data = {
            'name': process_name,
            'type': process_type,
            'production_rate': production_rate,
            'operating_hours': operating_hours,
            'location': plant_location,
            'temperature': operating_temperature,
            'pressure': operating_pressure,
            'complexity': process_complexity,
            'raw_materials': st.session_state.raw_materials,
            'products': st.session_state.products
        }
        
        st.success("✅ Process data saved successfully!")
        st.info("👉 Go to **Capital Costs** to continue with equipment sizing and costing.")
        
    except ValidationError as e:
        st.error(f"❌ Validation Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error saving process data: {str(e)}")

# Load template option
st.header("📋 Process Templates")
col1, col2 = st.columns(2)

with col1:
    if st.button("🧪 Load Batch Reactor Template"):
        # Load predefined template
        st.session_state.raw_materials = [
            {'name': 'Reactant A', 'price': 2.50, 'consumption_rate': 800},
            {'name': 'Reactant B', 'price': 1.80, 'consumption_rate': 200},
            {'name': 'Catalyst', 'price': 50.0, 'consumption_rate': 5}
        ]
        st.session_state.products = [
            {'name': 'Product X', 'price': 8.50, 'yield': 85}
        ]
        st.success("Batch reactor template loaded!")
        st.rerun()

with col2:
    if st.button("🏭 Load Continuous Process Template"):
        st.session_state.raw_materials = [
            {'name': 'Feedstock', 'price': 1.20, 'consumption_rate': 1050},
            {'name': 'Solvent', 'price': 3.00, 'consumption_rate': 150}
        ]
        st.session_state.products = [
            {'name': 'Main Product', 'price': 6.20, 'yield': 92},
            {'name': 'By-product', 'price': 2.10, 'yield': 8}
        ]
        st.success("Continuous process template loaded!")
        st.rerun()
