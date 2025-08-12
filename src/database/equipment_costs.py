
"""
Equipment cost database and correlations
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List

class EquipmentCostDatabase:
    """
    Database for equipment costs and correlations
    """
    
    def __init__(self):
        self.data_path = Path("data")
        self.equipment_db = self._load_equipment_database()
        self.cepci_data = self._load_cepci_data()
    
    def _load_equipment_database(self) -> pd.DataFrame:
        """
        Load equipment database from CSV
        """
        try:
            db_path = self.data_path / "equipment_database.csv"
            return pd.read_csv(db_path)
        except FileNotFoundError:
            # Return default database if file not found
            return self._create_default_database()
    
    def _create_default_database(self) -> pd.DataFrame:
        """
        Create default equipment database
        """
        data = {
            'equipment_type': ['reactor_cstr', 'reactor_batch', 'distillation_column', 
                             'heat_exchanger_shell_tube', 'pump_centrifugal', 'tank_storage'],
            'base_cost': [50000, 45000, 80000, 15000, 3000, 10000],
            'base_capacity': [1000, 1000, 100, 50, 100, 1000],
            'base_capacity_unit': ['L', 'L', 'theoretical_plates', 'm2', 'L_min', 'L'],
            'scaling_factor': [0.65, 0.70, 0.70, 0.60, 0.35, 0.85],
            'material_cs': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'material_ss': [2.5, 2.5, 2.2, 2.0, 1.8, 2.0],
            'material_hastelloy': [6.0, 6.0, 4.5, 3.5, 3.0, 4.0],
            'description': ['Continuous stirred tank reactor', 'Batch reactor with agitation',
                          'Distillation column with trays', 'Shell and tube heat exchanger',
                          'Centrifugal pump', 'Storage tank']
        }
        return pd.DataFrame(data)
    
    def _load_cepci_data(self) -> Dict[int, float]:
        """
        Load CEPCI (Chemical Engineering Plant Cost Index) data
        """
        return {
            2010: 550.8,
            2015: 556.8,
            2018: 603.1,
            2020: 596.2,
            2021: 708.0,
            2022: 816.0,
            2023: 832.0,
            2024: 850.0  # Estimated
        }
    
    def get_equipment_data(self, equipment_type: str) -> Optional[Dict]:
        """
        Get equipment data by type
        
        Args:
            equipment_type: Type of equipment
            
        Returns:
            Dictionary with equipment data or None if not found
        """
        equipment_row = self.equipment_db[self.equipment_db['equipment_type'] == equipment_type]
        
        if equipment_row.empty:
            return None
        
        return equipment_row.iloc[0].to_dict()
    
    def estimate_equipment_cost(self, equipment_type: str, capacity: float,
                              material: str = 'carbon_steel', year: int = 2024) -> Dict:
        """
        Estimate equipment cost with detailed breakdown
        
        Args:
            equipment_type: Type of equipment
            capacity: Equipment capacity
            material: Material of construction
            year: Year for cost estimation
            
        Returns:
            Dictionary with cost breakdown
        """
        equipment_data = self.get_equipment_data(equipment_type)
        
        if not equipment_data:
            raise ValueError(f"Equipment type '{equipment_type}' not found")
        
        # Base cost calculation
        base_cost = equipment_data['base_cost']
        base_capacity = equipment_data['base_capacity']
        scaling_factor = equipment_data['scaling_factor']
        
        # Capacity scaling
        scaled_cost = base_cost * (capacity / base_capacity) ** scaling_factor
        
        # Material factor
        material_column = f'material_{material.replace("_steel", "_").replace("steel", "").strip("_")}'
        if material == 'carbon_steel':
            material_column = 'material_cs'
        elif material == 'stainless_steel':
            material_column = 'material_ss'
        
        material_factor = equipment_data.get(material_column, 1.0)
        material_adjusted_cost = scaled_cost * material_factor
        
        # CEPCI adjustment
        base_year = 2020
        base_cepci = self.cepci_data.get(base_year, 596.2)
        current_cepci = self.cepci_data.get(year, 850.0)
        
        final_cost = material_adjusted_cost * (current_cepci / base_cepci)
        
        return {
            'base_cost': base_cost,
            'capacity_factor': (capacity / base_capacity) ** scaling_factor,
            'scaled_cost': scaled_cost,
            'material_factor': material_factor,
            'material_adjusted_cost': material_adjusted_cost,
            'cepci_factor': current_cepci / base_cepci,
            'final_cost': final_cost,
            'unit': equipment_data['base_capacity_unit'],
            'description': equipment_data['description']
        }
    
    def get_available_equipment_types(self) -> List[str]:
        """
        Get list of available equipment types
        
        Returns:
            List of equipment type names
        """
        return self.equipment_db['equipment_type'].tolist()
    
    def get_equipment_by_category(self, category: str) -> pd.DataFrame:
        """
        Get equipment by category
        
        Args:
            category: Equipment category (reactor, separator, etc.)
            
        Returns:
            DataFrame with matching equipment
        """
        return self.equipment_db[self.equipment_db['equipment_type'].str.contains(category, case=False)]
    
    def update_cepci(self, year: int, index_value: float):
        """
        Update CEPCI index for a specific year
        
        Args:
            year: Year
            index_value: CEPCI index value
        """
        self.cepci_data[year] = index_value
    
    def get_cost_range(self, equipment_type: str, capacity_range: tuple, 
                      material: str = 'carbon_steel') -> Dict:
        """
        Get cost range for equipment over capacity range
        
        Args:
            equipment_type: Type of equipment
            capacity_range: Tuple of (min_capacity, max_capacity)
            material: Material of construction
            
        Returns:
            Dictionary with cost range information
        """
        min_cap, max_cap = capacity_range
        
        min_cost_data = self.estimate_equipment_cost(equipment_type, min_cap, material)
        max_cost_data = self.estimate_equipment_cost(equipment_type, max_cap, material)
        
        return {
            'capacity_range': capacity_range,
            'cost_range': (min_cost_data['final_cost'], max_cost_data['final_cost']),
            'unit': min_cost_data['unit'],
            'material': material,
            'equipment_type': equipment_type
        }
