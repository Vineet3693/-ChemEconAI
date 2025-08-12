
"""
Capital cost estimation for chemical processes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from ..utils.calculations import equipment_cost_scaling, cepci_cost_update

class CapitalCostEstimator:
    """
    Class for estimating capital costs of chemical processes
    """
    
    def __init__(self):
        self.equipment_database = self._load_equipment_database()
        self.installation_factors = self._get_installation_factors()
        self.current_cepci = 850  # Approximate 2024 CEPCI
    
    def _load_equipment_database(self) -> Dict:
        """
        Load equipment cost database
        """
        # Simplified equipment database
        return {
            'reactor': {
                'base_cost': 50000,
                'base_capacity': 1000,  # L
                'scaling_factor': 0.65,
                'material_factor': {'carbon_steel': 1.0, 'stainless_steel': 2.5, 'hastelloy': 6.0}
            },
            'distillation_column': {
                'base_cost': 80000,
                'base_capacity': 100,  # theoretical plates
                'scaling_factor': 0.70,
                'material_factor': {'carbon_steel': 1.0, 'stainless_steel': 2.2}
            },
            'heat_exchanger': {
                'base_cost': 15000,
                'base_capacity': 50,  # m2
                'scaling_factor': 0.60,
                'material_factor': {'carbon_steel': 1.0, 'stainless_steel': 2.0}
            },
            'pump': {
                'base_cost': 3000,
                'base_capacity': 100,  # L/min
                'scaling_factor': 0.35,
                'material_factor': {'carbon_steel': 1.0, 'stainless_steel': 1.8}
            },
            'tank': {
                'base_cost': 10000,
                'base_capacity': 1000,  # L
                'scaling_factor': 0.85,
                'material_factor': {'carbon_steel': 1.0, 'stainless_steel': 2.0}
            }
        }
    
    def _get_installation_factors(self) -> Dict:
        """
        Get installation factors for different equipment types
        """
        return {
            'reactor': 3.5,
            'distillation_column': 4.0,
            'heat_exchanger': 2.5,
            'pump': 2.0,
            'tank': 2.2,
            'default': 3.0
        }
    
    def estimate_equipment_cost(self, equipment_type: str, capacity: float, 
                              material: str = 'carbon_steel', year: int = 2024) -> float:
        """
        Estimate equipment cost based on capacity
        
        Args:
            equipment_type: Type of equipment
            capacity: Equipment capacity
            material: Material of construction
            year: Year for cost estimation
        
        Returns:
            Equipment cost
        """
        if equipment_type not in self.equipment_database:
            raise ValueError(f"Equipment type '{equipment_type}' not found in database")
        
        equipment_data = self.equipment_database[equipment_type]
        
        # Scale cost based on capacity
        base_cost = equipment_data['base_cost']
        base_capacity = equipment_data['base_capacity']
        scaling_factor = equipment_data['scaling_factor']
        
        scaled_cost = equipment_cost_scaling(base_cost, base_capacity, capacity, scaling_factor)
        
        # Apply material factor
        material_factor = equipment_data['material_factor'].get(material, 1.0)
        material_adjusted_cost = scaled_cost * material_factor
      
        # Update cost to current year using CEPCI (assuming base year 2020 with CEPCI 596)
        base_year_cepci = 596
        current_cost = cepci_cost_update(material_adjusted_cost, base_year_cepci, self.current_cepci)
        
        return current_cost
    
    def calculate_total_equipment_cost(self, equipment_list: List[Dict]) -> Dict[str, float]:
        """
        Calculate total equipment cost for a list of equipment
        
        Args:
            equipment_list: List of equipment dictionaries with type, capacity, material
        
        Returns:
            Dictionary with equipment costs breakdown
        """
        equipment_costs = {}
        total_equipment_cost = 0
        
        for equipment in equipment_list:
            equipment_type = equipment['type']
            capacity = equipment['capacity']
            material = equipment.get('material', 'carbon_steel')
            quantity = equipment.get('quantity', 1)
            
            unit_cost = self.estimate_equipment_cost(equipment_type, capacity, material)
            total_cost = unit_cost * quantity
            
            equipment_costs[f"{equipment_type}_{equipment.get('id', '')}"] = {
                'unit_cost': unit_cost,
                'quantity': quantity,
                'total_cost': total_cost
            }
            
            total_equipment_cost += total_cost
        
        equipment_costs['total_equipment_cost'] = total_equipment_cost
        return equipment_costs
    
    def calculate_installed_cost(self, equipment_costs: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate installed equipment costs
        """
        installed_costs = {}
        total_installed_cost = 0
        
        for equipment_id, cost_data in equipment_costs.items():
            if equipment_id == 'total_equipment_cost':
                continue
                
            equipment_type = equipment_id.split('_')[0]
            installation_factor = self.installation_factors.get(equipment_type, 
                                                              self.installation_factors['default'])
            
            if isinstance(cost_data, dict):
                equipment_cost = cost_data['total_cost']
            else:
                equipment_cost = cost_data
            
            installed_cost = equipment_cost * installation_factor
            installed_costs[equipment_id] = installed_cost
            total_installed_cost += installed_cost
        
        installed_costs['total_installed_cost'] = total_installed_cost
        return installed_costs
    
    def estimate_total_capital_investment(self, total_installed_cost: float, 
                                        plant_type: str = 'chemical') -> Dict[str, float]:
        """
        Estimate total capital investment including indirect costs
        
        Args:
            total_installed_cost: Total installed equipment cost
            plant_type: Type of plant (chemical, pharmaceutical, etc.)
        
        Returns:
            Capital cost breakdown
        """
        # Factors based on plant type
        factors = {
            'chemical': {
                'engineering': 0.15,
                'construction': 0.20,
                'contingency': 0.15,
                'working_capital': 0.10
            },
            'pharmaceutical': {
                'engineering': 0.20,
                'construction': 0.25,
                'contingency': 0.20,
                'working_capital': 0.15
            }
        }
        
        plant_factors = factors.get(plant_type, factors['chemical'])
        
        # Calculate capital cost components
        engineering_cost = total_installed_cost * plant_factors['engineering']
        construction_cost = total_installed_cost * plant_factors['construction']
        
        # Fixed capital investment
        fixed_capital = total_installed_cost + engineering_cost + construction_cost
        
        # Contingency
        contingency = fixed_capital * plant_factors['contingency']
        
        # Total fixed capital
        total_fixed_capital = fixed_capital + contingency
        
        # Working capital
        working_capital = total_fixed_capital * plant_factors['working_capital']
        
        # Total capital investment
        total_capital_investment = total_fixed_capital + working_capital
        
        return {
            'installed_equipment_cost': total_installed_cost,
            'engineering_cost': engineering_cost,
            'construction_cost': construction_cost,
            'contingency': contingency,
            'fixed_capital_investment': total_fixed_capital,
            'working_capital': working_capital,
            'total_capital_investment': total_capital_investment
        }
