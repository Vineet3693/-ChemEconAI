
"""
Input validation functions for ChemEconAI
"""

from typing import Any, List, Dict, Optional
import pandas as pd
import numpy as np

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_positive_number(value: Any, field_name: str) -> float:
    """
    Validate that a value is a positive number
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
    
    Returns:
        Validated float value
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        num_value = float(value)
        if num_value <= 0:
            raise ValidationError(f"{field_name} must be a positive number")
        return num_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")

def validate_non_negative_number(value: Any, field_name: str) -> float:
    """
    Validate that a value is a non-negative number
    """
    try:
        num_value = float(value)
        if num_value < 0:
            raise ValidationError(f"{field_name} cannot be negative")
        return num_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")

def validate_percentage(value: Any, field_name: str, max_percent: float = 100) -> float:
    """
    Validate percentage input
    """
    try:
        num_value = float(value)
        if not (0 <= num_value <= max_percent):
            raise ValidationError(f"{field_name} must be between 0 and {max_percent}%")
        return num_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid percentage")

def validate_process_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate process design parameters
    """
    validated_params = {}
    
    # Required fields
    required_fields = ['production_rate', 'operating_hours', 'process_type']
    for field in required_fields:
        if field not in params or params[field] is None:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate production rate
    validated_params['production_rate'] = validate_positive_number(
        params['production_rate'], 'Production Rate'
    )
    
    # Validate operating hours
    operating_hours = validate_positive_number(params['operating_hours'], 'Operating Hours')
    if operating_hours > 8760:  # Hours in a year
        raise ValidationError("Operating hours cannot exceed 8760 hours per year")
    validated_params['operating_hours'] = operating_hours
    
    # Validate process type
    valid_process_types = ['batch', 'continuous', 'semi-batch']
    if params['process_type'].lower() not in valid_process_types:
        raise ValidationError(f"Process type must be one of: {', '.join(valid_process_types)}")
    validated_params['process_type'] = params['process_type'].lower()
    
    return validated_params

def validate_economic_inputs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate economic calculation inputs
    """
    validated_inputs = {}
    
    # Validate discount rate
    if 'discount_rate' in inputs:
        validated_inputs['discount_rate'] = validate_percentage(
            inputs['discount_rate'], 'Discount Rate', 50
        ) / 100  # Convert to decimal
    
    # Validate project lifetime
    if 'project_lifetime' in inputs:
        lifetime = validate_positive_number(inputs['project_lifetime'], 'Project Lifetime')
        if lifetime > 50:
            raise ValidationError("Project lifetime seems too long (>50 years)")
        validated_inputs['project_lifetime'] = int(lifetime)
    
    # Validate capital investment
    if 'capital_investment' in inputs:
        validated_inputs['capital_investment'] = validate_positive_number(
            inputs['capital_investment'], 'Capital Investment'
        )
    
    return validated_inputs
