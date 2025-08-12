
"""
Output formatting functions for ChemEconAI
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Format currency with proper thousands separators
    """
    try:
        if abs(amount) >= 1e9:
            return f"{currency_symbol}{amount/1e9:.2f}B"
        elif abs(amount) >= 1e6:
            return f"{currency_symbol}{amount/1e6:.2f}M"
        elif abs(amount) >= 1e3:
            return f"{currency_symbol}{amount/1e3:.2f}K"
        else:
            return f"{currency_symbol}{amount:,.2f}"
    except:
        return f"{currency_symbol}0.00"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format percentage with specified decimal places
    """
    try:
        return f"{value:.{decimal_places}f}%"
    except:
        return "0.00%"

def format_technical_units(value: float, unit: str) -> str:
    """
    Format technical values with appropriate units
    """
    try:
        if unit.lower() in ['kg/h', 'tons/year', 'tons/day']:
            return f"{value:,.1f} {unit}"
        elif unit.lower() in ['kw', 'mw']:
            return f"{value:,.0f} {unit}"
        else:
            return f"{value:.2f} {unit}"
    except:
        return f"0 {unit}"

def create_summary_table(data: Dict[str, Any], title: str = "Summary") -> pd.DataFrame:
    """
    Create a formatted summary table
    """
    try:
        summary_data = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                if 'cost' in key.lower() or 'investment' in key.lower():
                    formatted_value = format_currency(value)
                elif 'rate' in key.lower() or 'roi' in key.lower():
                    formatted_value = format_percentage(value)
                else:
                    formatted_value = f"{value:,.2f}"
            else:
                formatted_value = str(value)
            
            summary_data.append({
                'Parameter': key.replace('_', ' ').title(),
                'Value': formatted_value
            })
        
        return pd.DataFrame(summary_data)
    except Exception as e:
        return pd.DataFrame({'Error': [f"Could not create summary: {str(e)}"]}
