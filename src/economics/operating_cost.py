
"""
Operating cost calculations for chemical processes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class OperatingCostCalculator:
    """
    Class for calculating operating costs of chemical processes
    """
    
    def __init__(self):
        self.utility_prices = self._get_utility_prices()
        self.labor_rates = self._get_labor_rates()
    
    def _get_utility_prices(self) -> Dict[str, float]:
        """
        Get utility prices (can be loaded from database)
        """
        return {
            'electricity': 0.08,  # $/kWh
            'steam_low_pressure': 15.0,  # $/ton
            'steam_medium_pressure': 18.0,  # $/ton
            'steam_high_pressure': 22.0,  # $/ton
            'cooling_water': 0.05,  # $/m3
            'process_water': 0.50,  # $/m3
            'natural_gas': 8.0,  # $/MMBtu
            'compressed_air': 0.20  # $/1000 ft3
        }
    
    def _get_labor_rates(self) -> Dict[str, float]:
        """
        Get labor rates by position
        """
        return {
            'operator': 35.0,  # $/hour
            'supervisor': 50.0,  # $/hour
            'maintenance': 40.0,  # $/hour
            'engineer': 60.0,  # $/hour
        }
    
    def calculate_raw_material_costs(self, materials: List[Dict], production_rate: float,
                                   operating_hours: int) -> Dict[str, float]:
        """
        Calculate raw material costs
        
        Args:
            materials: List of materials with name, price, consumption_rate
            production_rate: Production rate (tons/year)
            operating_hours: Operating hours per year
        
        Returns:
            Raw material cost breakdown
        """
        material_costs = {}
        total_material_cost = 0
        
        for material in materials:
            name = material['name']
            price = material['price']  # $/kg
            consumption_rate = material['consumption_rate']  # kg/ton product
            
            annual_consumption = production_rate * consumption_rate  # kg/year
            annual_cost = annual_consumption * price
            
            material_costs[name] = {
                'consumption_rate': consumption_rate,
                'annual_consumption': annual_consumption,
                'unit_price': price,
                'annual_cost': annual_cost
            }
            
            total_material_cost += annual_cost
        
        material_costs['total_raw_material_cost'] = total_material_cost
        return material_costs
    
    def calculate_utility_costs(self, utilities: List[Dict]) -> Dict[str, float]:
        """
        Calculate utility costs
        
        Args:
            utilities: List of utilities with type and consumption
        
        Returns:
            Utility cost breakdown
        """
        utility_costs = {}
        total_utility_cost = 0
        
        for utility in utilities:
            utility_type = utility['type']
            consumption = utility['consumption']  # per year
            
            if utility_type not in self.utility_prices:
                continue
            
            unit_price = self.utility_prices[utility_type]
            annual_cost = consumption * unit_price
            
            utility_costs[utility_type] = {
                'consumption': consumption,
                'unit_price': unit_price,
                'annual_cost': annual_cost
            }
            
            total_utility_cost += annual_cost
        
        utility_costs['total_utility_cost'] = total_utility_cost
        return utility_costs
    
    def calculate_labor_costs(self, labor_requirements: Dict[str, int], 
                            shifts_per_day: int = 3) -> Dict[str, float]:
        """
        Calculate labor costs
        
        Args:
            labor_requirements: Dictionary with position and number of people per shift
            shifts_per_day: Number of shifts per day
        
        Returns:
            Labor cost breakdown
        """
        labor_costs = {}
        total_labor_cost = 0
        
        hours_per_year = 365 * 24  # Continuous operation
        
        for position, people_per_shift in labor_requirements.items():
            if position not in self.labor_rates:
                continue
            
            hourly_rate = self.labor_rates[position]
            total_people = people_per_shift * shifts_per_day
            annual_hours = total_people * hours_per_year
            annual_cost = annual_hours * hourly_rate
            
            labor_costs[position] = {
                'people_per_shift': people_per_shift,
                'total_people': total_people,
                'hourly_rate': hourly_rate,
                'annual_hours': annual_hours,
                'annual_cost': annual_cost
            }
            
            total_labor_cost += annual_cost
        
        labor_costs['total_labor_cost'] = total_labor_cost
        return labor_costs
    
    def calculate_maintenance_costs(self, fixed_capital_investment: float,
                                  maintenance_factor: float = 0.04) -> float:
        """
        Calculate annual maintenance costs
        
        Args:
            fixed_capital_investment: Fixed capital investment
            maintenance_factor: Maintenance factor (typically 2-6% of FCI)
        
        Returns:
            Annual maintenance cost
        """
        return fixed_capital_investment * maintenance_factor
    
    def calculate_overhead_costs(self, direct_costs: Dict[str, float],
                               overhead_factor: float = 0.60) -> Dict[str, float]:
        """
        Calculate overhead costs
        
        Args:
            direct_costs: Dictionary of direct costs
            overhead_factor: Overhead factor (typically 50-80% of direct costs)
        
        Returns:
            Overhead cost breakdown
        """
        total_direct_costs = sum(direct_costs.values())
        
        overhead_costs = {
            'administrative': total_direct_costs * 0.15,
            'sales_marketing': total_direct_costs * 0.10,
            'research_development': total_direct_costs * 0.05,
            'general_overhead': total_direct_costs * (overhead_factor - 0.30)
        }
        
        overhead_costs['total_overhead_cost'] = sum(overhead_costs.values())
        return overhead_costs
    
    def calculate_total_operating_costs(self, cost_inputs: Dict) -> Dict[str, float]:
        """
        Calculate total annual operating costs
        
        Args:
            cost_inputs: Dictionary with all cost inputs
        
        Returns:
            Complete operating cost breakdown
        """
        operating_costs = {}
        
        # Raw material costs
        if 'raw_materials' in cost_inputs:
            material_costs = self.calculate_raw_material_costs(
                cost_inputs['raw_materials'],
                cost_inputs.get('production_rate', 1000),
                cost_inputs.get('operating_hours', 8000)
            )
            operating_costs.update(material_costs)
        
        # Utility costs
        if 'utilities' in cost_inputs:
            utility_costs = self.calculate_utility_costs(cost_inputs['utilities'])
            operating_costs.update(utility_costs)
        
        # Labor costs
        if 'labor_requirements' in cost_inputs:
            labor_costs = self.calculate_labor_costs(cost_inputs['labor_requirements'])
            operating_costs.update(labor_costs)
        
        # Maintenance costs
        if 'fixed_capital_investment' in cost_inputs:
            maintenance_cost = self.calculate_maintenance_costs(
                cost_inputs['fixed_capital_investment']
            )
            operating_costs['maintenance_cost'] = maintenance_cost
        
        # Calculate direct costs
        direct_costs = {
            'raw_materials': operating_costs.get('total_raw_material_cost', 0),
            'utilities': operating_costs.get('total_utility_cost', 0),
            'labor': operating_costs.get('total_labor_cost', 0),
            'maintenance': operating_costs.get('maintenance_cost', 0)
        }
        
        # Overhead costs
        overhead_costs = self.calculate_overhead_costs(direct_costs)
        operating_costs.update(overhead_costs)
        
        # Total operating cost
        total_operating_cost = (
            sum(direct_costs.values()) + 
            overhead_costs['total_overhead_cost']
        )
        
        operating_costs['total_annual_operating_cost'] = total_operating_cost
        
        return operating_costs
