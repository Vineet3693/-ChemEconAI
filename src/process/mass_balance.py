
"""
Material balance calculations for chemical processes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class MaterialBalanceCalculator:
    """
    Class for performing material balance calculations
    """
    
    def __init__(self):
        self.components = {}
        self.streams = {}
        self.reactions = {}
    
    def add_component(self, name: str, molecular_weight: float, 
                     phase: str = "liquid", density: Optional[float] = None):
        """
        Add a component to the material balance
        
        Args:
            name: Component name
            molecular_weight: Molecular weight (g/mol)
            phase: Phase (liquid, gas, solid)
            density: Density (kg/m3) if known
        """
        self.components[name] = {
            'molecular_weight': molecular_weight,
            'phase': phase,
            'density': density
        }
    
    def add_stream(self, name: str, components: Dict[str, float], 
                   temperature: float = 25.0, pressure: float = 1.0):
        """
        Add a process stream
        
        Args:
            name: Stream name
            components: Dictionary of component mass flows (kg/h)
            temperature: Temperature (°C)
            pressure: Pressure (bar)
        """
        self.streams[name] = {
            'components': components,
            'temperature': temperature,
            'pressure': pressure,
            'total_mass_flow': sum(components.values())
        }
    
    def add_reaction(self, name: str, stoichiometry: Dict[str, float], 
                    conversion: float, selectivity: float = 1.0):
        """
        Add a chemical reaction
        
        Args:
            name: Reaction name
            stoichiometry: Stoichiometric coefficients (negative for reactants, positive for products)
            conversion: Conversion of limiting reactant (0-1)
            selectivity: Selectivity to desired product (0-1)
        """
        self.reactions[name] = {
            'stoichiometry': stoichiometry,
            'conversion': conversion,
            'selectivity': selectivity
        }
    
    def calculate_reactor_outlet(self, inlet_stream: str, reaction_name: str) -> Dict:
        """
        Calculate reactor outlet composition based on reaction
        
        Args:
            inlet_stream: Name of inlet stream
            reaction_name: Name of reaction
            
        Returns:
            Dictionary with outlet stream composition
        """
        if inlet_stream not in self.streams:
            raise ValueError(f"Inlet stream '{inlet_stream}' not found")
        if reaction_name not in self.reactions:
            raise ValueError(f"Reaction '{reaction_name}' not found")
        
        inlet = self.streams[inlet_stream]['components'].copy()
        reaction = self.reactions[reaction_name]
        stoichiometry = reaction['stoichiometry']
        conversion = reaction['conversion']
        selectivity = reaction['selectivity']
        
        # Find limiting reactant
        limiting_reactant = None
        min_extent = float('inf')
        
        for component, coeff in stoichiometry.items():
            if coeff < 0 and component in inlet:  # Reactant
                possible_extent = inlet[component] / abs(coeff)
                if possible_extent < min_extent:
                    min_extent = possible_extent
                    limiting_reactant = component
        
        if limiting_reactant is None:
            return {'components': inlet, 'conversion_achieved': 0}
        
        # Calculate actual extent of reaction
        actual_extent = min_extent * conversion * selectivity
        
        # Update component flows
        outlet = inlet.copy()
        for component, coeff in stoichiometry.items():
            if component in outlet:
                outlet[component] += coeff * actual_extent
            else:
                outlet[component] = max(0, coeff * actual_extent)
            
            # Ensure non-negative flows
            outlet[component] = max(0, outlet[component])
        
        conversion_achieved = (inlet[limiting_reactant] - outlet[limiting_reactant]) / inlet[limiting_reactant]
        
        return {
            'components': outlet,
            'conversion_achieved': conversion_achieved,
            'limiting_reactant': limiting_reactant,
            'extent_of_reaction': actual_extent
        }
    
    def calculate_separator_outlets(self, inlet_stream: str, 
                                  split_fractions: Dict[str, Dict[str, float]]) -> Dict:
        """
        Calculate separator outlet streams
        
        Args:
            inlet_stream: Name of inlet stream
            split_fractions: Dictionary of {outlet_name: {component: fraction}}
            
        Returns:
            Dictionary with outlet streams
        """
        if inlet_stream not in self.streams:
            raise ValueError(f"Inlet stream '{inlet_stream}' not found")
        
        inlet = self.streams[inlet_stream]['components']
        outlets = {}
        
        for outlet_name, splits in split_fractions.items():
            outlet_components = {}
            for component, inlet_flow in inlet.items():
                split_fraction = splits.get(component, 0.0)
                outlet_components[component] = inlet_flow * split_fraction
            
            outlets[outlet_name] = {
                'components': outlet_components,
                'total_mass_flow': sum(outlet_components.values())
            }
        
        return outlets
    
    def calculate_annual_consumption(self, stream_name: str, operating_hours: int) -> Dict:
        """
        Calculate annual material consumption
        
        Args:
            stream_name: Name of stream
            operating_hours: Operating hours per year
            
        Returns:
            Annual consumption by component
        """
        if stream_name not in self.streams:
            raise ValueError(f"Stream '{stream_name}' not found")
        
        hourly_flows = self.streams[stream_name]['components']
        annual_consumption = {}
        
        for component, hourly_flow in hourly_flows.items():
            annual_consumption[component] = {
                'hourly_flow_kg_h': hourly_flow,
                'annual_consumption_kg': hourly_flow * operating_hours,
                'annual_consumption_tons': hourly_flow * operating_hours / 1000
            }
        
        return annual_consumption
    
    def generate_material_balance_table(self) -> pd.DataFrame:
        """
        Generate a material balance table for all streams
        
        Returns:
            DataFrame with material balance
        """
        # Get all components
        all_components = set()
        for stream_data in self.streams.values():
            all_components.update(stream_data['components'].keys())
        
        # Create balance table
        balance_data = []
        
        for stream_name, stream_data in self.streams.items():
            row = {'Stream': stream_name}
            
            # Add component flows
            for component in sorted(all_components):
                flow = stream_data['components'].get(component, 0)
                row[f'{component} (kg/h)'] = flow
            
            # Add total flow and conditions
            row['Total Flow (kg/h)'] = stream_data['total_mass_flow']
            row['Temperature (°C)'] = stream_data.get('temperature', 25)
            row['Pressure (bar)'] = stream_data.get('pressure', 1.0)
            
            balance_data.append(row)
        
        return pd.DataFrame(balance_data)
    
    def check_mass_balance(self, inlet_streams: List[str], 
                          outlet_streams: List[str], tolerance: float = 1e-6) -> Dict:
        """
        Check overall mass balance
        
        Args:
            inlet_streams: List of inlet stream names
            outlet_streams: List of outlet stream names
            tolerance: Tolerance for balance check
            
        Returns:
            Dictionary with balance results
        """
        total_inlet = 0
        total_outlet = 0
        
        for stream_name in inlet_streams:
            if stream_name in self.streams:
                total_inlet += self.streams[stream_name]['total_mass_flow']
        
        for stream_name in outlet_streams:
            if stream_name in self.streams:
                total_outlet += self.streams[stream_name]['total_mass_flow']
        
        imbalance = total_inlet - total_outlet
        relative_error = abs(imbalance) / total_inlet if total_inlet > 0 else 0
        
        is_balanced = relative_error <= tolerance
        
        return {
            'total_inlet_kg_h': total_inlet,
            'total_outlet_kg_h': total_outlet,
            'imbalance_kg_h': imbalance,
            'relative_error_percent': relative_error * 100,
            'is_balanced': is_balanced,
            'tolerance_percent': tolerance * 100
        }
    
    def calculate_yield_and_conversion(self, reaction_name: str, 
                                     feed_stream: str, product_stream: str) -> Dict:
        """
        Calculate reaction yield and conversion
        
        Args:
            reaction_name: Name of reaction
            feed_stream: Feed stream name
            product_stream: Product stream name
            
        Returns:
            Dictionary with yield and conversion data
        """
        if reaction_name not in self.reactions:
            raise ValueError(f"Reaction '{reaction_name}' not found")
        
        reaction = self.reactions[reaction_name]
        stoichiometry = reaction['stoichiometry']
        
        # Find key reactant and product
        reactants = {k: v for k, v in stoichiometry.items() if v < 0}
        products = {k: v for k, v in stoichiometry.items() if v > 0}
        
        if not reactants or not products:
            raise ValueError("Reaction must have both reactants and products")
        
        key_reactant = list(reactants.keys())[0]
        key_product = list(products.keys())[0]
        
        # Get stream data
        feed = self.streams.get(feed_stream, {}).get('components', {})
        product = self.streams.get(product_stream, {}).get('components', {})
        
        # Calculate conversion
        reactant_in = feed.get(key_reactant, 0)
        reactant_out = product.get(key_reactant, 0)
        conversion = (reactant_in - reactant_out) / reactant_in if reactant_in > 0 else 0
        
        # Calculate yield
        product_made = product.get(key_product, 0)
        theoretical_product = (reactant_in - reactant_out) * abs(stoichiometry[key_product] / stoichiometry[key_reactant])
        yield_fraction = product_made / theoretical_product if theoretical_product > 0 else 0
        
        return {
            'conversion_percent': conversion * 100,
            'yield_percent': yield_fraction * 100,
            'reactant_consumed_kg_h': reactant_in - reactant_out,
            'product_formed_kg_h': product_made,
            'theoretical_product_kg_h': theoretical_product,
            'key_reactant': key_reactant,
            'key_product': key_product
        }
