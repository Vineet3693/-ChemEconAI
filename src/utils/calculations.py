
"""
Common calculation functions for chemical process economics
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional

def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
    """
    Calculate Net Present Value (NPV)
    
    Args:
        cash_flows: List of annual cash flows (negative for investments, positive for profits)
        discount_rate: Discount rate as decimal (e.g., 0.12 for 12%)
    
    Returns:
        NPV value
    """
    try:
        npv = 0
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** i)
        return npv
    except Exception as e:
        raise ValueError(f"Error calculating NPV: {str(e)}")

def calculate_irr(cash_flows: List[float], max_iterations: int = 1000, tolerance: float = 1e-6) -> float:
    """
    Calculate Internal Rate of Return (IRR) using Newton-Raphson method
    
    Args:
        cash_flows: List of annual cash flows
        max_iterations: Maximum number of iterations
        tolerance: Convergence tolerance
    
    Returns:
        IRR as decimal
    """
    try:
        if len(cash_flows) < 2:
            raise ValueError("Need at least 2 cash flows")
        
        # Initial guess
        rate = 0.1
        
        for _ in range(max_iterations):
            # Calculate NPV and its derivative
            npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
            dnpv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows) if i > 0)
            
            if abs(npv) < tolerance:
                return rate
            
            if abs(dnpv) < tolerance:
                break
                
            # Newton-Raphson step
            rate = rate - npv / dnpv
            
            if rate < -0.99:  # Avoid negative rates close to -100%
                rate = -0.99
        
        return rate
    except Exception as e:
        raise ValueError(f"Error calculating IRR: {str(e)}")

def calculate_payback_period(initial_investment: float, annual_cash_flows: List[float]) -> float:
    """
    Calculate payback period
    
    Args:
        initial_investment: Initial capital investment (positive value)
        annual_cash_flows: List of annual cash flows
    
    Returns:
        Payback period in years
    """
    try:
        cumulative_cash_flow = 0
        
        for year, cash_flow in enumerate(annual_cash_flows):
            cumulative_cash_flow += cash_flow
            
            if cumulative_cash_flow >= initial_investment:
                # Linear interpolation for fractional year
                excess = cumulative_cash_flow - initial_investment
                fraction = excess / cash_flow
                return year + 1 - fraction
        
        # Investment not recovered within given period
        return len(annual_cash_flows) + (initial_investment - cumulative_cash_flow) / annual_cash_flows[-1]
    
    except Exception as e:
        raise ValueError(f"Error calculating payback period: {str(e)}")

def calculate_roi(profit: float, investment: float) -> float:
    """
    Calculate Return on Investment (ROI)
    
    Args:
        profit: Annual profit
        investment: Initial investment
    
    Returns:
        ROI as percentage
    """
    try:
        if investment == 0:
            raise ValueError("Investment cannot be zero")
        return (profit / investment) * 100
    except Exception as e:
        raise ValueError(f"Error calculating ROI: {str(e)}")

def equipment_cost_scaling(base_cost: float, base_capacity: float, new_capacity: float, scaling_factor: float = 0.6) -> float:
    """
    Scale equipment cost based on capacity using power law
    
    Args:
        base_cost: Known cost at base capacity
        base_capacity: Base capacity
        new_capacity: New capacity to scale to
        scaling_factor: Scaling exponent (typically 0.6 for most equipment)
    
    Returns:
        Scaled equipment cost
    """
    try:
        if base_capacity <= 0 or new_capacity <= 0:
            raise ValueError("Capacities must be positive")
        
        return base_cost * (new_capacity / base_capacity) ** scaling_factor
    except Exception as e:
        raise ValueError(f"Error scaling equipment cost: {str(e)}")

def cepci_cost_update(base_cost: float, base_year_index: float, current_year_index: float) -> float:
    """
    Update cost using Chemical Engineering Plant Cost Index (CEPCI)
    
    Args:
        base_cost: Cost in base year
        base_year_index: CEPCI for base year
        current_year_index: CEPCI for current year
    
    Returns:
        Updated cost
    """
    try:
        if base_year_index <= 0 or current_year_index <= 0:
            raise ValueError("CEPCI indices must be positive")
        
        return base_cost * (current_year_index / base_year_index)
    except Exception as e:
        raise ValueError(f"Error updating cost with CEPCI: {str(e)}")

def sensitivity_analysis(base_value: float, parameter_changes: List[float], 
                        calculation_function, **kwargs) -> Dict[float, float]:
    """
    Perform sensitivity analysis on a parameter
    
    Args:
        base_value: Base value of parameter
        parameter_changes: List of percentage changes (e.g., [-20, -10, 10, 20])
        calculation_function: Function to recalculate result
        **kwargs: Additional arguments for calculation function
    
    Returns:
        Dictionary mapping parameter change to result change
    """
    try:
        base_result = calculation_function(base_value, **kwargs)
        sensitivity_results = {}
        
        for change_percent in parameter_changes:
            new_value = base_value * (1 + change_percent / 100)
            new_result = calculation_function(new_value, **kwargs)
            result_change = ((new_result - base_result) / base_result) * 100
            sensitivity_results[change_percent] = result_change
        
        return sensitivity_results
    except Exception as e:
        raise ValueError(f"Error in sensitivity analysis: {str(e)}")
