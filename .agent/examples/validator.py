"""
Template de validator baseado em asset_validator.py

Copie este arquivo e adapte conforme necessário.
"""
from typing import Dict, Any, Optional, Tuple
from response.formatter import error_response
from messages import ErrorMessages
from constants import MIN_LENGTH, VALID_TYPES  # Adicione suas constants

# Type alias for validation results
ValidationResult = Tuple[bool, Optional[Dict[str, Any]]]


def validate_resource_fields(
    field1: Optional[str] = None,
    field2: Optional[int] = None,
    required: bool = True
) -> ValidationResult:
    """
    Validate resource fields with consistent rules.
    
    Args:
        field1: First field to validate
        field2: Second field to validate
        required: If True, all fields are required (create mode)
                 If False, only validate provided fields (update mode)
    
    Returns:
        ValidationResult: (is_valid, error_response)
            - is_valid: True if validation passed
            - error_response: Error dict if validation failed, None otherwise
    
    Example:
        >>> is_valid, error = validate_resource_fields(
        ...     field1="value",
        ...     field2=42,
        ...     required=True
        ... )
        >>> print(is_valid)
        True
    """
    
    # Validation: Field1 (string length)
    if required:
        if not field1 or len(field1) < MIN_LENGTH:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.FIELD_TOO_SHORT
            )
    else:
        if field1 is not None and len(field1) < MIN_LENGTH:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.FIELD_TOO_SHORT
            )
    
    # Validation: Field2 (type check)
    if required:
        if field2 is None:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.FIELD_REQUIRED
            )
    
    if field2 is not None:
        try:
            field2_int = int(field2)
            if field2_int < 0:
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.FIELD_NEGATIVE
                )
        except (ValueError, TypeError):
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.INVALID_NUMBER
            )
    
    # All validations passed
    return True, None
