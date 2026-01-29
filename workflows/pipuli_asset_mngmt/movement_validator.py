"""
Movement validation helper for shared validation logic.
"""
from typing import Dict, Any, Optional, Tuple
from response.formatter import error_response
from messages import ErrorMessages

# Type alias for validation results
ValidationResult = Tuple[bool, Optional[Dict[str, Any]]]


def validate_movement_fields(
    month: Optional[str] = None,
    contribution: Optional[float] = None,
    withdraw: Optional[float] = None,
    asset_type: Optional[str] = None,
    current_gross_balance: Optional[float] = None,
    market_value: Optional[float] = None,
    outstanding_balance: Optional[float] = None,
    required: bool = True
) -> ValidationResult:
    """
    Validate movement fields with consistent rules.
    
    Args:
        month: Month in format YYYY-MM
        contribution: Contribution amount
        withdraw: Withdrawal amount
        asset_type: Asset type (INVESTMENT or PROPERTY)
        current_gross_balance: Current gross balance (for INVESTMENT)
        market_value: Market value (for PROPERTY)
        outstanding_balance: Outstanding balance (for PROPERTY)
        required: If True, all fields are required (create mode)
                 If False, only validate provided fields (update mode)
    
    Returns:
        ValidationResult: (is_valid, error_response)
            - is_valid: True if validation passed
            - error_response: Error dict if validation failed, None otherwise
    """
    
    # Validation: Month
    if required:
        if not month or len(month.strip()) == 0:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.MONTH_EMPTY
            )
    else:
        if month is not None and len(month.strip()) == 0:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.MONTH_EMPTY
            )
    
    # Validation: Contribution
    if required:
        if contribution is None:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.CONTRIBUTION_REQUIRED
            )
    
    if contribution is not None:
        try:
            contribution_float = float(contribution)
            if contribution_float < 0:
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.CONTRIBUTION_NEGATIVE
                )
        except (ValueError, TypeError):
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.INVALID_NUMBER
            )
    
    # Validation: Withdraw
    if required:
        if withdraw is None:
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.WITHDRAW_REQUIRED
            )
    
    if withdraw is not None:
        try:
            withdraw_float = float(withdraw)
            if withdraw_float < 0:
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.WITHDRAW_NEGATIVE
                )
        except (ValueError, TypeError):
            return False, error_response(
                error="validation_error",
                message=ErrorMessages.INVALID_NUMBER
            )
    
    # Validation: Type-Specific Fields
    if asset_type == "INVESTMENT":
        # Validate currentGrossBalance
        if required:
            if current_gross_balance is None:
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.BALANCE_NEGATIVE
                )
        
        if current_gross_balance is not None:
            try:
                balance_float = float(current_gross_balance)
                if balance_float < 0:
                    return False, error_response(
                        error="validation_error",
                        message=ErrorMessages.BALANCE_NEGATIVE
                    )
            except (ValueError, TypeError):
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.BALANCE_INVALID
                )
    
    elif asset_type == "PROPERTY":
        # Validate marketValue
        if required:
            if market_value is None:
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.MARKET_VALUE_NEGATIVE
                )
        
        if market_value is not None:
            try:
                market_float = float(market_value)
                if market_float < 0:
                    return False, error_response(
                        error="validation_error",
                        message=ErrorMessages.MARKET_VALUE_NEGATIVE
                    )
            except (ValueError, TypeError):
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.MARKET_VALUE_INVALID
                )
        
        # Validate outstandingBalance
        if required:
            if outstanding_balance is None:
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.OUTSTANDING_BALANCE_NEGATIVE
                )
        
        if outstanding_balance is not None:
            try:
                outstanding_float = float(outstanding_balance)
                if outstanding_float < 0:
                    return False, error_response(
                        error="validation_error",
                        message=ErrorMessages.OUTSTANDING_BALANCE_NEGATIVE
                    )
            except (ValueError, TypeError):
                return False, error_response(
                    error="validation_error",
                    message=ErrorMessages.OUTSTANDING_BALANCE_INVALID
                )
    
    # All validations passed
    return True, None
