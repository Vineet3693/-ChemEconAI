
"""
Market data provider for chemical prices and trends
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class MarketDataProvider:
    """
    Provider for chemical market data and pricing
    """
    
    def __init__(self):
        self.data_path = Path("data")
        self.material_prices = self._load_material_prices()
        self.utility_costs = self._load_utility_costs()
        self.market_trends = self._initialize_trends()
    
    def _load_material_prices(self) -> pd.DataFrame:
        """
        Load material prices from CSV
        """
        try:
            prices_path = self.data_path / "material_prices.csv"
            return pd.read_csv(prices_path)
        except FileNotFoundError:
            return self._create_default_material_prices()
    
    def _create_default_material_prices(self) -> pd.DataFrame:
        """
        Create default material prices database
        """
        data = {
            'material_name': ['methanol', 'ethanol', 'acetone', 'sodium_hydroxide', 
                            'sulfuric_acid', 'hydrochloric_acid', 'hydrogen', 'nitrogen'],
            'category': ['solvent', 'solvent', 'solvent', 'base', 'acid', 'acid', 'gas', 'gas'],
            'price_usd_per_kg': [0.45, 0.65, 1.20, 0.35, 0.25, 0.30, 3.50, 0.05],
            'unit': ['kg', 'kg', 'kg', 'kg', 'kg', 'kg', 'kg', 'm3'],
            'volatility': ['medium', 'medium', 'high', 'low', 'medium', 'medium', 'high', 'low'],
            'supplier_location': ['global', 'global', 'global', 'global', 'regional', 
                                'regional', 'regional', 'regional'],
            'description': ['Methanol 99.5%', 'Ethanol 99.5%', 'Acetone 99.5%', 
                          'Caustic soda 50%', 'Sulfuric acid 98%', 'HCl 37%', 
                          'Hydrogen 99.9%', 'Nitrogen 99.9%']
        }
        return pd.DataFrame(data)
    
    def _load_utility_costs(self) -> pd.DataFrame:
        """
        Load utility costs from CSV
        """
        try:
            utility_path = self.data_path / "utility_costs.csv"
            return pd.read_csv(utility_path)
        except FileNotFoundError:
            return self._create_default_utility_costs()
    
    def _create_default_utility_costs(self) -> pd.DataFrame:
        """
        Create default utility costs database
        """
        data = {
            'utility_type': ['electricity', 'steam_lp', 'steam_mp', 'steam_hp', 
                           'cooling_water', 'process_water', 'natural_gas'],
            'unit': ['dollar_per_kWh', 'dollar_per_ton', 'dollar_per_ton', 
                    'dollar_per_ton', 'dollar_per_m3', 'dollar_per_m3', 'dollar_per_MMBtu'],
            'usa_gulf_coast': [0.08, 15.0, 18.0, 22.0, 0.05, 0.50, 8.0],
            'usa_northeast': [0.12, 18.0, 22.0, 28.0, 0.08, 0.80, 12.0],
            'europe_germany': [0.15, 22.0, 28.0, 35.0, 0.12, 1.20, 15.0],
            'asia_singapore': [0.10, 16.0, 20.0, 25.0, 0.06, 0.60, 10.0],
            'asia_china': [0.07, 12.0, 15.0, 18.0, 0.04, 0.40, 6.0]
        }
        return pd.DataFrame(data)
    
    def _initialize_trends(self) -> Dict:
        """
        Initialize market trend data
        """
        return {
            'chemicals': {
                'solvents': {'trend': 'increasing', 'volatility': 'high'},
                'acids': {'trend': 'stable', 'volatility': 'medium'},
                'bases': {'trend': 'stable', 'volatility': 'low'}
            },
            'utilities': {
                'electricity': {'trend': 'increasing', 'volatility': 'medium'},
                'natural_gas': {'trend': 'volatile', 'volatility': 'high'},
                'steam': {'trend': 'increasing', 'volatility': 'medium'}
            }
        }
    
    def get_material_price(self, material_name: str) -> Optional[Dict]:
        """
        Get current price for a material
        
        Args:
            material_name: Name of material
            
        Returns:
            Dictionary with price information
        """
        material_row = self.material_prices[
            self.material_prices['material_name'] == material_name.lower()
        ]
        
        if material_row.empty:
            return None
        
        material_data = material_row.iloc[0].to_dict()
        
        # Add price volatility adjustment
        base_price = material_data['price_usd_per_kg']
        volatility = material_data['volatility']
        
        # Simulate price range based on volatility
        if volatility == 'low':
            price_range = (base_price * 0.95, base_price * 1.05)
        elif volatility == 'medium':
            price_range = (base_price * 0.85, base_price * 1.15)
        else:  # high volatility
            price_range = (base_price * 0.70, base_price * 1.30)
        
        material_data['price_range'] = price_range
        material_data['last_updated'] = datetime.now().isoformat()
        
        return material_data
    
    def get_utility_cost(self, utility_type: str, location: str = 'usa_gulf_coast') -> Optional[Dict]:
        """
        Get utility cost for specific location
        
        Args:
            utility_type: Type of utility
            location: Plant location
            
        Returns:
            Dictionary with utility cost information
        """
        utility_row = self.utility_costs[
            self.utility_costs['utility_type'] == utility_type.lower()
        ]
        
        if utility_row.empty:
            return None
        
        utility_data = utility_row.iloc[0].to_dict()
        location_key = location.lower().replace(' ', '_').replace('-', '_')
        
        if location_key not in utility_data:
            location_key = 'usa_gulf_coast'  # Default fallback
        
        cost = utility_data.get(location_key, 0)
        
        return {
            'utility_type': utility_type,
            'location': location,
            'cost': cost,
            'unit': utility_data['unit'],
            'currency': 'USD',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_price_forecast(self, material_name: str, years: int = 5) -> Dict:
        """
        Generate price forecast for material
        
        Args:
            material_name: Name of material
            years: Number of years to forecast
            
        Returns:
            Dictionary with forecast data
        """
        material_data = self.get_material_price(material_name)
        
        if not material_data:
            return None
        
        base_price = material_data['price_usd_per_kg']
        volatility = material_data['volatility']
        
        # Generate forecast based on historical trends and volatility
        forecast_years = list(range(1, years + 1))
        
        # Base trend assumptions
        if volatility == 'low':
            annual_growth = np.random.normal(0.02, 0.01, years)  # 2% ± 1%
        elif volatility == 'medium':
            annual_growth = np.random.normal(0.03, 0.02, years)  # 3% ± 2%
        else:  # high volatility
            annual_growth = np.random.normal(0.04, 0.03, years)  # 4% ± 3%
        
        # Calculate forecasted prices
        forecasted_prices = []
        current_price = base_price
        
        for growth_rate in annual_growth:
            current_price = current_price * (1 + growth_rate)
            forecasted_prices.append(current_price)
        
        return {
            'material_name': material_name,
            'base_price': base_price,
            'forecast_years': forecast_years,
            'forecasted_prices': forecasted_prices,
            'volatility': volatility,
            'confidence': 'medium' if volatility == 'medium' else 'low' if volatility == 'high' else 'high'
        }
    
    def get_materials_by_category(self, category: str) -> pd.DataFrame:
        """
        Get all materials in a specific category
        
        Args:
            category: Material category
            
        Returns:
            DataFrame with materials in category
        """
        return self.material_prices[
            self.material_prices['category'].str.lower() == category.lower()
        ]
    
    def calculate_cost_escalation(self, base_cost: float, years: int, 
                                escalation_rate: float = 0.03) -> Dict:
        """
        Calculate cost escalation over time
        
        Args:
            base_cost: Base cost in current year
            years: Number of years to escalate
            escalation_rate: Annual escalation rate (default 3%)
            
        Returns:
            Dictionary with escalated costs
        """
        escalated_costs = []
        
        for year in range(1, years + 1):
            escalated_cost = base_cost * (1 + escalation_rate) ** year
            escalated_costs.append({
                'year': year,
                'escalated_cost': escalated_cost,
                'escalation_factor': (1 + escalation_rate) ** year
            })
        
        return {
            'base_cost': base_cost,
            'escalation_rate': escalation_rate,
            'years': years,
            'escalated_costs': escalated_costs,
            'total_escalation': ((1 + escalation_rate) ** years - 1) * 100
        }
    
    def get_regional_cost_factors(self) -> Dict:
        """
        Get regional cost adjustment factors
        
        Returns:
            Dictionary with regional factors
        """
        return {
            'usa_gulf_coast': 1.00,     # Base case
            'usa_northeast': 1.25,      # 25% higher
            'usa_west_coast': 1.30,     # 30% higher
            'europe_germany': 1.40,     # 40% higher
            'europe_uk': 1.45,          # 45% higher
            'asia_singapore': 1.15,     # 15% higher
            'asia_china': 0.75,         # 25% lower
            'asia_india': 0.65,         # 35% lower
            'middle_east': 0.80,        # 20% lower
            'south_america': 0.70       # 30% lower
        }
    
    def get_market_summary(self) -> Dict:
        """
        Get market summary statistics
        
        Returns:
            Dictionary with market summary
        """
        avg_prices = self.material_prices.groupby('category')['price_usd_per_kg'].mean()
        price_volatility = self.material_prices['volatility'].value_counts()
        
        return {
            'total_materials': len(self.material_prices),
            'categories': self.material_prices['category'].unique().tolist(),
            'average_prices_by_category': avg_prices.to_dict(),
            'volatility_distribution': price_volatility.to_dict(),
            'last_updated': datetime.now().isoformat()
        }
