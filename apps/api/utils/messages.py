"""
Centralized error and success messages for consistent UX.
All messages follow the app's creative, fun tone.
"""


class ErrorMessages:
    """Error messages with creative, fun tone."""
    
    # Auth
    UNAUTHORIZED = "User not authenticated. Missing token."
    INVALID_UID = "Invalid user ID in token."
    
    # Assets
    ASSET_NOT_FOUND = "Ghost Asset? We can't find that one in your books."
    ASSET_DELETED = "This asset has been deleted. You can't update what doesn't exist."
    ASSET_ID_MISSING = "We need a target. Asset ID is missing."
    ASSET_DELETED_CANNOT_ADD_MOVEMENT = "Cannot add movements to a deleted asset. Restore it first."
    ASSET_DELETED_CANNOT_UPDATE_MOVEMENT = "Cannot update movements of a deleted asset."
    
    # Movements
    MOVEMENT_NOT_FOUND = "This movement vanished from the ledger. Check the ID and try again."
    MOVEMENT_DELETED = "This movement has been erased. You can't update what doesn't exist."
    MOVEMENT_ID_MISSING = "Which movement are we updating? Movement ID is missing."
    
    # Validation - Names
    NAME_TOO_SHORT = "A name so short? Give it at least 2 characters to shine."
    
    # Validation - Asset Types
    INVALID_ASSET_TYPE = "Whoops! That asset type is from another dimension. We only accept 'INVESTMENT' or 'PROPERTY'."
    
    # Validation - Categories
    CATEGORY_EMPTY = "Everything needs a home. Pick a category."
    
    # Validation - Dates/Time
    MONTH_EMPTY = "Time is money. Please tell us which month this is for."
    
    # Validation - Numbers (Contributions/Withdrawals)
    CONTRIBUTION_REQUIRED = "You can't grow an empire with nothing. Contribution is required."
    CONTRIBUTION_NEGATIVE = "Negative money? Nice try, but contributions must be positive."
    WITHDRAW_REQUIRED = "Taking profits? We need to know how much."
    WITHDRAW_NEGATIVE = "Negative money? Nice try, but withdrawals must be positive."
    INVALID_NUMBER = "Is that a number? Our calculators are confused."
    
    # Validation - Balances (INVESTMENT)
    BALANCE_NEGATIVE = "Balance can't go negative! Keep it at 0 or above."
    BALANCE_INVALID = "Is that a number? Our calculators are confused."
    
    # Validation - Property Values (PROPERTY)
    MARKET_VALUE_NEGATIVE = "Market value in the red? That's not how this works. Keep it positive!"
    MARKET_VALUE_INVALID = "Is that a number? Our calculators are confused."
    OUTSTANDING_BALANCE_NEGATIVE = "Outstanding balance can't be negative. Math doesn't work that way!"
    OUTSTANDING_BALANCE_INVALID = "Is that a number? Our calculators are confused."
    
    # Database
    DB_ERROR_GENERIC = "The vault is jammed. We couldn't complete that operation. Try again."
    DB_ERROR_SAVE = "Ink spill on the ledger! We couldn't save that {item}. Try again."
    DB_ERROR_UPDATE = "Ink spill on the ledger! We couldn't update that {item}. Try again."
    DB_ERROR_DELETE = "The vault is locked. We couldn't delete that {item}. Try again."


class SuccessMessages:
    """Success messages with creative, fun tone."""
    
    # Assets
    ASSET_CREATED = "Asset Minted! Your empire grows."
    ASSET_UPDATED = "Asset updated! Your empire evolves."
    ASSET_DELETED = "Asset incinerated. Wiped from the ledger."
    
    # Movements
    MOVEMENT_CREATED = "Movement recorded. The ledger is updated."
    MOVEMENT_UPDATED = "Movement updated! The ledger evolves."
    MOVEMENT_DELETED = "Movement erased from history."
