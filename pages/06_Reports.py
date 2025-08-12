import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

st.set_page_config(
    page_title="Reports - ChemEconAI",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Executive Reports & Documentation")
st.markdown("Generate comprehensive reports for your chemical process economics analysis.")

# Check for required data
required_data = {
    'Process Design': 'process_data',
    'Capital Costs': 'capital_costs', 
    'Operating Costs': 'operating_costs',
    'Profitability Analysis': 'calculations'
}

missing_data = []
available_data = {}

for report_section, session_key in required_data.items():
    if session_key in st.session_state and st.session_state[session_key]:
        available_data[report_section] = st.session_state[session_key]
    else:
        missing_data.append(report_section)

if missing_data:
    st.warning(f"⚠️ **Missing data for complete report:** {', '.join(missing_data)}")
    st.info("Complete the previous analysis steps for a comprehensive report.")

# Report Configuration
st.header("⚙️ Report Configuration")

col1, col2 = st.columns(2)

with col1:
    report_title = st.text_input(
        "Report Title",
        value="Chemical Process Economics Analysis Report"
    )
    
    project_name = st.text_input(
        "Project Name",
        value=st.session_state.get('process_data', {}).get('name', 'Chemical Process Project')
    )
    
    author_name = st.text_input(
        "Author/Company",
        value="ChemEconAI Analysis"
    )

with col2:
    report_date = st.date_input(
        "Report Date",
        value=datetime.now().date()
    )
    
    report_type = st.selectbox(
        "Report Type",
        ["Executive Summary", "Detailed Technical Report", "Investment Proposal", "Feasibility Study"]
    )
    
    include_charts = st.checkbox(
        "Include Charts and Visualizations",
        value=True
    )

# Report Sections Selection
st.header("📑 Report Sections")

report_sections = st.multiselect(
    "Select sections to include in the report",
    [
        "Executive Summary",
        "Process Overview",
        "Capital Cost Analysis", 
        "Operating Cost Analysis",
        "Profitability Analysis",
        "Risk Assessment",
        "Sensitivity Analysis",
        "Recommendations",
        "Technical Appendix"
    ],
    default=["Executive Summary", "Process Overview", "Capital Cost Analysis", 
             "Operating Cost Analysis", "Profitability Analysis", "Recommendations"]
)

# Report Preview
if st.button("🔍 Generate Report Preview", type="primary"):
    
    # Create report content
    report_content = {}
    
    # Executive Summary
    if "Executive Summary" in report_sections and 'calculations' in available_data:
        calculations = available_data['Profitability Analysis']
        
        executive_summary = f"""
        ## Executive Summary
        
        **Project:** {project_name}
        **Analysis Date:** {report_date}
        **Analyst:** {author_name}
        
        ### Key Financial Metrics
        - **Net Present Value (NPV):** ${calculations.get('npv', 0):,.2f}
        - **Internal Rate of Return (IRR):** {calculations.get('irr', 0):.1f}%
        - **Payback Period:** {calculations.get('payback_period', 0):.1f} years
        - **Return on Investment (ROI):** {calculations.get('roi', 0):.1f}%
        
        ### Investment Recommendation
        """
        
        if calculations.get('npv', 0) > 0 and calculations.get('irr', 0) > 12:
            executive_summary += "✅ **RECOMMENDATION: APPROVE** - The project shows strong financial returns with positive NPV and acceptable IRR."
        elif calculations.get('npv', 0) > 0:
            executive_summary += "🟡 **CONDITIONAL APPROVAL** - Positive NPV but consider risk factors."
        else:
            executive_summary += "❌ **NOT RECOMMENDED** - Negative NPV indicates poor financial returns."
        
        report_content['Executive Summary'] = executive_summary
    
    # Process Overview
    if "Process Overview" in report_sections and 'Process Design' in available_data:
        process_data = available_data['Process Design']
        
        process_overview = f"""
        ## Process Overview
        
        **Process Type:** {process_data.get('type', 'Not specified')}
        **Production Capacity:** {process_data.get('production_rate', 0):,.0f} tons/year
        **Operating Hours:** {process_data.get('operating_hours', 0):,.0f} hours/year
        **Plant Location:** {process_data.get('location', 'Not specified')}
        
        ### Raw Materials
        """
        
        if 'raw_materials' in process_data:
            for material in process_data['raw_materials']:
                process_overview += f"- **{material['name']}:** ${material['price']:.2f}/kg, {material['consumption_rate']} kg/ton product\n"
        
        process_overview += "\n### Products\n"
        if 'products' in process_data:
            for product in process_data['products']:
                process_overview += f"- **{product['name']}:** ${product['price']:.2f}/kg, {product['yield']}% yield\n"
        
        report_content['Process Overview'] = process_overview
    
    # Capital Cost Analysis
    if "Capital Cost Analysis" in report_sections and 'Capital Costs' in available_data:
        capital_data = available_data['Capital Costs']
        
        capital_analysis = f"""
        ## Capital Cost Analysis
        
        ### Total Capital Investment: ${capital_data.get('total_capital_investment', 0):,.2f}
        
        **Cost Breakdown:**
        - **Installed Equipment Cost:** ${capital_data.get('installed_equipment_cost', 0):,.2f}
        - **Engineering & Design:** ${capital_data.get('engineering_cost', 0):,.2f}
        - **Construction:** ${capital_data.get('construction_cost', 0):,.2f}
        - **Contingency:** ${capital_data.get('contingency', 0):,.2f}
        - **Working Capital:** ${capital_data.get('working_capital', 0):,.2f}
        
        ### Key Metrics
        - **CAPEX per Annual Ton:** ${(capital_data.get('total_capital_investment', 0) / st.session_state.get('process_data', {}).get('production_rate', 1)):,.2f}
        - **Fixed Capital Investment:** ${capital_data.get('fixed_capital_investment', 0):,.2f}
        """
        
        report_content['Capital Cost Analysis'] = capital_analysis
    
    # Operating Cost Analysis
    if "Operating Cost Analysis" in report_sections and 'Operating Costs' in available_data:
        operating_data = available_data['Operating Costs']
        
        operating_analysis = f"""
        ## Operating Cost Analysis
        
        ### Total Annual Operating Cost: ${operating_data.get('total_annual_operating_cost', 0):,.2f}
        
        **Cost Breakdown:**
        - **Raw Materials:** ${operating_data.get('total_raw_material_cost', 0):,.2f}
        - **Utilities:** ${operating_data.get('total_utility_cost', 0):,.2f}
        - **Labor:** ${operating_data.get('total_labor_cost', 0):,.2f}
        - **Maintenance:** ${operating_data.get('maintenance_cost', 0):,.2f}
        - **Overhead:** ${operating_data.get('total_overhead_cost', 0):,.2f}
        
        ### Operating Cost per Ton Product
        ${(operating_data.get('total_annual_operating_cost', 0) / st.session_state.get('process_data', {}).get('production_rate', 1)):,.2f} per ton
        """
        
        report_content['Operating Cost Analysis'] = operating_analysis
    
    # Profitability Analysis
    if "Profitability Analysis" in report_sections and 'Profitability Analysis' in available_data:
        prof_data = available_data['Profitability Analysis']
        
        profitability_analysis = f"""
        ## Profitability Analysis
        
        ### Financial Metrics
        - **Net Present Value:** ${prof_data.get('npv', 0):,.2f}
        - **Internal Rate of Return:** {prof_data.get('irr', 0):.1f}%
        - **Payback Period:** {prof_data.get('payback_period', 0):.1f} years
        - **Profitability Index:** {prof_data.get('profitability_index', 0):.2f}
        - **Return on Investment:** {prof_data.get('roi', 0):.1f}%
        
        ### Annual Cash Flow
        **Average Annual Cash Flow:** ${prof_data.get('annual_cash_flow', 0):,.2f}
        
        ### Project Economics Summary
        - **Total Project Revenue:** ${prof_data.get('total_revenue', 0):,.2f}
        - **Total Project Costs:** ${prof_data.get('total_costs', 0):,.2f}
        - **Net Project Value:** ${(prof_data.get('total_revenue', 0) - prof_data.get('total_costs', 0)):,.2f}
        """
        
        report_content['Profitability Analysis'] = profitability_analysis
    
    # Recommendations
    if "Recommendations" in report_sections:
        recommendations = """
        ## Recommendations
        
        ### Strategic Recommendations
        1. **Process Optimization:** Focus on improving yield and reducing raw material consumption
        2. **Cost Control:** Implement cost monitoring systems for key expense categories
        3. **Risk Management:** Develop contingency plans for market volatility
        4. **Technology:** Consider process intensification opportunities
        
        ### Next Steps
        1. Detailed engineering design
        2. Vendor quotations for major equipment
        3. Environmental and safety assessments
        4. Financing arrangements
        5. Project implementation planning
        
        ### Risk Mitigation
        - Secure long-term supply contracts for key raw materials
        - Consider product price hedging strategies
        - Plan for regulatory compliance requirements
        - Implement robust process control systems
        """
        
        report_content['Recommendations'] = recommendations
    
    # Display Report Preview
    st.header("📄 Report Preview")
    
    for section_name in report_sections:
        if section_name in report_content:
            with st.expander(f"📑 {section_name}", expanded=True):
                st.markdown(report_content[section_name])
    
    # Export Options
    st.header("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # PDF Export
        if st.button("📄 Export as PDF"):
            try:
                # Create PDF
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#1f77b4'),
                    spaceAfter=30
                )
                story.append(Paragraph(report_title, title_style))
                story.append(Spacer(1, 12))
                
                # Add content
                for section_name in report_sections:
                    if section_name in report_content:
                        # Section header
                        story.append(Paragraph(section_name, styles['Heading2']))
                        story.append(Spacer(1, 12))
                        
                        # Section content (simplified for PDF)
                        content = report_content[section_name].replace('#', '').replace('*', '')
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip():
                                story.append(Paragraph(line.strip(), styles['Normal']))
                        story.````````append(Spacer(1, 6))
                
                # Build PDF
                doc.build(story)
                
                # Download button
                pdf_data = buffer.getvalue()
                buffer.close()
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name=f"{project_name.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"PDF generation error: {str(e)}")
    
    with col2:
        # Excel Export
        if st.button("📊 Export as Excel"):
            try:
                # Create Excel workbook with multiple sheets
                with pd.ExcelWriter(f"{project_name}_Analysis.xlsx", engine='openpyxl') as writer:
                    
                    # Summary sheet
                    if 'calculations' in available_data:
                        summary_data = {
                            'Metric': ['NPV', 'IRR (%)', 'Payback (years)', 'ROI (%)', 'Prof. Index'],
                            'Value': [
                                available_data['Profitability Analysis']['npv'],
                                available_data['Profitability Analysis']['irr'],
                                available_data['Profitability Analysis']['payback_period'],
                                available_data['Profitability Analysis']['roi'],
                                available_data['Profitability Analysis']['profitability_index']
                            ]
                        }
                        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Capital costs sheet
                    if 'Capital Costs' in available_data:
                        capital_data = available_data['Capital Costs']
                        capital_df = pd.DataFrame([
                            ['Equipment Cost', capital_data.get('installed_equipment_cost', 0)],
                            ['Engineering', capital_data.get('engineering_cost', 0)],
                            ['Construction', capital_data.get('construction_cost', 0)],
                            ['Contingency', capital_data.get('contingency', 0)],
                            ['Working Capital', capital_data.get('working_capital', 0)],
                            ['Total CAPEX', capital_data.get('total_capital_investment', 0)]
                        ], columns=['Item', 'Cost ($)'])
                        capital_df.to_excel(writer, sheet_name='Capital Costs', index=False)
                    
                    # Operating costs sheet
                    if 'Operating Costs' in available_data:
                        opex_data = available_data['Operating Costs']
                        opex_df = pd.DataFrame([
                            ['Raw Materials', opex_data.get('total_raw_material_cost', 0)],
                            ['Utilities', opex_data.get('total_utility_cost', 0)],
                            ['Labor', opex_data.get('total_labor_cost', 0)],
                            ['Maintenance', opex_data.get('maintenance_cost', 0)],
                            ['Overhead', opex_data.get('total_overhead_cost', 0)],
                            ['Total OPEX', opex_data.get('total_annual_operating_cost', 0)]
                        ], columns=['Item', 'Annual Cost ($)'])
                        opex_df.to_excel(writer, sheet_name='Operating Costs', index=False)
                
                st.success("✅ Excel file created successfully!")
                
            except Exception as e:
                st.error(f"Excel generation error: {str(e)}")
    
    with col3:
        # JSON Export
        if st.button("📋 Export as JSON"):
            try:
                # Compile all data
                export_data = {
                    'report_metadata': {
                        'title': report_title,
                        'project_name': project_name,
                        'author': author_name,
                        'date': report_date.isoformat(),
                        'generated_timestamp': datetime.now().isoformat()
                    },
                    'analysis_data': available_data
                }
                
                json_data = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download JSON Data",
                    data=json_data,
                    file_name=f"{project_name.replace(' ', '_')}_Data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"JSON export error: {str(e)}")

# Report Templates
st.header("📋 Report Templates")

template_col1, template_col2 = st.columns(2)

with template_col1:
    if st.button("🏭 Industrial Feasibility Template"):
        st.session_state.report_template = 'industrial'
        st.info("Industrial feasibility template loaded")

with template_col2:
    if st.button("💼 Investment Proposal Template"):
        st.session_state.report_template = 'investment'
        st.info("Investment proposal template loaded")

# Charts and Visualizations Section
if include_charts and available_data:
    st.header("📊 Report Visualizations")
    
    if 'Profitability Analysis' in available_data:
        calc_data = available_data['Profitability Analysis']
        
        # Financial metrics comparison
        metrics_data = {
            'Metric': ['NPV ($M)', 'IRR (%)', 'Payback (years)', 'ROI (%)'],
            'Value': [
                calc_data.get('npv', 0) / 1e6,
                calc_data.get('irr', 0),
                calc_data.get('payback_period', 0),
                calc_data.get('roi', 0)
            ],
            'Benchmark': [5, 15, 5, 20]  # Industry benchmarks
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Project',
            x=metrics_data['Metric'],
            y=metrics_data['Value'],
            marker_color='#1f77b4'
        ))
        fig.add_trace(go.Bar(
            name='Industry Benchmark',
            x=metrics_data['Metric'],
            y=metrics_data['Benchmark'],
            marker_color='#ff7f0e',
            opacity=0.7
        ))
        
        fig.update_layout(
            title='Financial Metrics vs Industry Benchmarks',
            barmode='group',
            yaxis_title='Value'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost breakdown pie chart
    if 'Capital Costs' in available_data:
        capital_data = available_data['Capital Costs']
        
        cost_categories = {
            'Equipment': capital_data.get('installed_equipment_cost', 0),
            'Engineering': capital_data.get('engineering_cost', 0),
            'Construction': capital_data.get('construction_cost', 0),
            'Contingency': capital_data.get('contingency', 0),
            'Working Capital': capital_data.get('working_capital', 0)
        }
        
        fig_pie = px.pie(
            values=list(cost_categories.values()),
            names=list(cost_categories.keys()),
            title='Capital Cost Breakdown'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*Report generated by ChemEconAI - Chemical Process Economics Analysis Tool*")
