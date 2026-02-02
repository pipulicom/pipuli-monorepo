"""
Validation service for data validation.
"""
from typing import Dict, Any, Optional, Tuple, Union, List
from services.base import BaseService


class ValidationService(BaseService):
    """
    Service for validating data with reusable validation rules.
    """
    
    def require(self, data: Dict[str, Any], *fields: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that required fields are present in data.
        
        Args:
            data: Data dictionary to validate
            *fields: Required field names
        
        Returns:
            (is_valid, error_message)
        """
        missing = [f for f in fields if f not in data or data[f] is None]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, None
    
    def type_check(self, data: Dict[str, Any], field: str, expected_type: Union[type, Tuple[type, ...]]) -> Tuple[bool, Optional[str]]:
        """
        Validate field type.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            expected_type: Expected type(s) (e.g., str, int, (int, float))
        
        Returns:
            (is_valid, error_message)
        """
        if field not in data:
            return True, None  # If field doesn't exist, require() will catch it
        
        value = data[field]
        if not isinstance(value, expected_type):
            type_names = expected_type.__name__ if isinstance(expected_type, type) else ', '.join(t.__name__ for t in expected_type)
            return False, f"{field} must be of type {type_names}"
        return True, None
    
    def range_check(self, data: Dict[str, Any], field: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate numeric range.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)
        
        Returns:
            (is_valid, error_message)
        """
        if field not in data:
            return True, None
        
        value = data[field]
        if not isinstance(value, (int, float)):
            return False, f"{field} must be a number"
        
        if min_val is not None and value < min_val:
            return False, f"{field} must be >= {min_val}"
        if max_val is not None and value > max_val:
            return False, f"{field} must be <= {max_val}"
        return True, None
    
    def length_check(self, data: Dict[str, Any], field: str, min_len: Optional[int] = None, max_len: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate string length.
        
        Args:
            data: Data dictionary
            field: Field name to validate
            min_len: Minimum length
            max_len: Maximum length
        
        Returns:
            (is_valid, error_message)
        """
        if field not in data:
            return True, None
        
        value = str(data[field])
        if min_len is not None and len(value) < min_len:
            return False, f"{field} must be at least {min_len} characters"
        if max_len is not None and len(value) > max_len:
            return False, f"{field} must be at most {max_len} characters"
        return True, None
    
    def email_check(self, data: Dict[str, Any], field: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Args:
            data: Data dictionary
            field: Field name to validate
        
        Returns:
            (is_valid, error_message)
        """
        if field not in data:
            return True, None
        
        import re
        email = str(data[field])
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, f"{field} must be a valid email address"
        return True, None
    
    def validate(self, data: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Validate data against multiple rules.
        
        Args:
            data: Data dictionary to validate
            rules: List of validation rules
        
        Rules format:
            [
                {"require": ["field1", "field2"]},
                {"type": {"field1": str, "field2": (int, float)}},
                {"range": {"field1": {"min": 0, "max": 100}}},
                {"length": {"field2": {"min": 2, "max": 50}}},
                {"email": ["field3"]}
            ]
        
        Returns:
            (is_valid, error_message)
        """
        for rule in rules:
            # Require fields
            if "require" in rule:
                is_valid, error = self.require(data, *rule["require"])
                if not is_valid:
                    return False, error
            
            # Type validation
            if "type" in rule:
                for field, expected_type in rule["type"].items():
                    is_valid, error = self.type_check(data, field, expected_type)
                    if not is_valid:
                        return False, error
            
            # Range validation
            if "range" in rule:
                for field, range_config in rule["range"].items():
                    is_valid, error = self.range_check(
                        data, field,
                        min_val=range_config.get("min"),
                        max_val=range_config.get("max")
                    )
                    if not is_valid:
                        return False, error
            
            # Length validation
            if "length" in rule:
                for field, length_config in rule["length"].items():
                    is_valid, error = self.length_check(
                        data, field,
                        min_len=length_config.get("min"),
                        max_len=length_config.get("max")
                    )
                    if not is_valid:
                        return False, error
            
            # Email validation
            if "email" in rule:
                for field in rule["email"]:
                    is_valid, error = self.email_check(data, field)
                    if not is_valid:
                        return False, error
        
        return True, None

