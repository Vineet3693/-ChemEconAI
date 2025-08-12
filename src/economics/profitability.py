
"""
Profitability analysis functions for chemical processes
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from ..utils.calculations import calculate_npv, calculate_irr, calculate_payback_period, calculate_roi

class ProfitabilityAnalyzer:
    """
    Class for analyzing chemical process profitability
    """
    
    def __init__(self):
        self.results = {}
    
    def calculate_annual_cash_flow(self, revenue: float, operating_costs: float, 
                                 taxes: float = 0, depreciation: float = 0) -> float:
        """
        Calculate annual cash flow
        
        Args:
            revenue: Annual revenue
            operating_costs: Annual operating costs
            taxes: Annual taxes
            depreciation: Annual depreciation
        
        Returns:
            Annual cash flow
        """
        gross_profit = revenue - operating_costs
        taxable_income = gross_profit - depreciation
        after_tax_income = taxable_income - taxes
        cash_flow = after_tax_income + depreciation  # Add back non-cash depreciation
        
        return cash_flow
    
    def analyze_profitability(self, capital_investment: float, annual_revenue: float,
                            annual_operating_costs: float, project_lifetime: int,
                            discount_rate: float, tax_rate: float = 0.3,
                            salvage_value: float = 0) -> Dict[str, float]:
        """
        Comprehensive profitability analysis
        
        Args:
            capital_investment: Initial capital investment
            annual_revenue: Annual revenue
            annual_operating_costs: Annual operating costs
            project_lifetime: Project lifetime in years
            discount_rate: Discount rate (decimal)
            tax_rate: Tax rate (decimal)
            salvage_value: Equipment salvage value at end of project
        
        Returns:
            Dictionary with profitability metrics
        """
        try:
            # Calculate annual depreciation (straight-line)
            annual_depreciation = (capital_investment - salvage_value) / project_lifetime
            
            # Calculate annual cash flows
            cash_flows = [-capital_investment]  # Initial investment (negative)
            
            for year in range(1, project_lifetime + 1):
                gross_profit = annual_revenue - annual_operating_costs
                taxable_income = gross_profit - annual_depreciation
                taxes = max(0, taxable_income * tax_rate)
                
                # Cash flow = After-tax income + depreciation (non-cash)
                after_tax_income = taxable_income - taxes
                annual_cash_flow = after_tax_income + annual_depreciation
                
                # Add salvage value in final year
                if year == project_lifetime:
                    annual_cash_flow += salvage_value
                
                cash_flows.append(annual_cash_flow)
            
            # Calculate profitability metrics
            npv = calculate_npv(cash_flows, discount_rate)
            irr = calculate_irr(cash_flows)
            payback_period = calculate_payback_period(capital_investment, cash_flows[1:])
            roi = calculate_roi(annual_revenue - annual_operating_costs, capital_investment)
            
            # Additional metrics
            profitability_index = (npv + capital_investment) / capital_investment
            break_even_price = annual_operating_costs / (annual_revenue / 
                                                       (annual_revenue - annual_operating_costs)) if annual_revenue > annual_operating_costs else 0
            
            self.results = {
                'npv': npv,
                'irr': irr * 100,  # Convert to percentage
                'payback_period': payback_period,
                'roi': roi,
                'profitability_index': profitability_index,
                'annual_cash_flow': cash_flows[1] if len(cash_flows) > 1 else 0,
                'total_revenue': annual_revenue * project_lifetime,
                'total_costs': annual_operating_costs * project_lifetime,
                'break_even_price': break_even_price
            }
            
            return self.results
            
        except Exception as e:
            raise ValueError(f"Error in profitability analysis: {str(e)}")
    
    def sensitivity_analysis(self, base_parameters: Dict[str, float], 
                           sensitivity_ranges: Dict[str, List[float]]) -> pd.DataFrame:
        """
        Perform sensitivity analysis on key parameters
        
        Args:
            base_parameters: Base case parameters
            sensitivity_ranges: Dictionary with parameter names and percentage changes
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        sensitivity_results = []
        
        for param_name, changes in sensitivity_ranges.items():
            if param_name not in base_parameters:
                continue
                
            base_value = base_parameters[param_name]
            
            for change_percent in changes:
                new_value = base_value * (1 + change_percent / 100)
                modified_params = base_parameters.copy()
                modified_params[param_name] = new_value
                
                # Recalculate profitability
                results = self.analyze_profitability(**modified_params)
                
                sensitivity_results.append({
                    'parameter': param_name,
                    'change_percent': change_percent,
                    'npv': results['npv'],
                    'irr': results['irr'],
                    'payback_period': results['payback_period']
                })
        
        return pd.DataFrame(sensitivity_results)
    
    def monte_carlo_analysis(self, parameters: Dict[str, Dict], n_simulations: int = 1000) -> pd.DataFrame:
        """
        Perform Monte Carlo simulation for risk analysis
        
        Args:
            parameters: Dictionary with parameter distributions
            n_simulations: Number of simulations to run
        
        Returns:
            DataFrame with simulation results
        """
        results = []
        
        for _ in range(n_simulations):
            sim_params = {}
            
            for param_name, param_dist in parameters.items():
                if param_dist['type'] == 'normal':
                    value = np.random.normal(param_dist['mean'], param_dist['std'])
                elif param_dist['type'] == 'triangular':
                    value = np.random.triangular(param_dist['min'], param_dist['mode'], param_dist['max'])
                elif param_dist['type'] == 'uniform':
                    value = np.random.uniform(param_dist['min'], param_dist['max'])
                else:
                    value = param_dist['mean']
                
                sim_params[param_name] = max(0, value)  # Ensure positive values
            
            # Calculate profitability for this simulation
            try:
                sim_results = self.analyze_profitability(**sim_params)
                results.append({
                    'simulation': len(results) + 1,
                    'npv': sim_results['npv'],
                    'irr': sim_results['irr'],
                    'payback_period': sim_results['payback_period'],
                    'roi': sim_results['roi']
                })
            except:
                continue  # Skip failed simulations
        
        return pd.DataFrame(results)
