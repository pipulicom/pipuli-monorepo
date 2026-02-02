"""
Application constants and configuration values.
"""

# Validation
MIN_NAME_LENGTH = 2
MIN_MONTH_LENGTH = 1

# Asset Types
ASSET_TYPE_INVESTMENT = "INVESTMENT"
ASSET_TYPE_PROPERTY = "PROPERTY"
VALID_ASSET_TYPES = [ASSET_TYPE_INVESTMENT, ASSET_TYPE_PROPERTY]

# Movement ID Generation
MOVEMENT_ID_PREFIX = "mov_"
TIMESTAMP_MULTIPLIER = 1000  # Convert seconds to milliseconds

# Database Collections
COLLECTION_ASSETS = "assets"
COLLECTION_MOVEMENTS = "movements"
COLLECTION_SUMMARIES = "summaries"
