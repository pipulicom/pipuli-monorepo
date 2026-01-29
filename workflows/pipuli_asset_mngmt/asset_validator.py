"""
Asset validation helper for shared validation logic.
"""
from typing import Dict, Any, Optional, Tuple
from response.formatter import error_response
from messages import ErrorMessages
from constants import MIN_NAME_LENGTH, VALID_ASSET_TYPES

# Type alias for validation results
ValidationResult = Tuple[bool, Optional[Dict[str, Any]]]


def validate_asset_fields(
    name: Optional[str] = None,
    asset_type: Optional[str] = None,
    category: Optional[str] = None,
    required: bool = True
) -> ValidationResult:
    """
    Validate asset fields with consistent rules.
    
    Args:
        name: Asset name
        asset_type: Asset type (INVESTMENT or PROPERTY)
        category: Asset category
        required: If True, all fields are required (create mode)
                 If False, only validate provided fields (update mode)
    
    Returns:
        ValidationResult: (is_valid, error_response)
            - is_valid: True if validation passed
            - error_response: Error dict if validation failed, None otherwise
    """
    
    # Validation: Name
    if required:
        if not name or len(name) < MIN_NAME_LENGTH:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.NAME_TOO_SHORT
            )
    else:
        if name is not None and len(name) < MIN_NAME_LENGTH:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.NAME_TOO_SHORT
            )
    
    # Validation: Type
    if required:
        if asset_type not in VALID_ASSET_TYPES:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.INVALID_ASSET_TYPE
            )
    else:
        if asset_type is not None and asset_type not in VALID_ASSET_TYPES:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.INVALID_ASSET_TYPE
            )
    
    # Validation: Category
    if required:
        if not category or not isinstance(category, str) or len(category.strip()) == 0:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.CATEGORY_EMPTY
            )
    else:
        if category is not None and (not isinstance(category, str) or len(category.strip()) == 0):
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.CATEGORY_EMPTY
            )
    
    # All validations passed
    return True, None
