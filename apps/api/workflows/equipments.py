from typing import Dict, Any, Optional
from utils.logger import Logger
from services.database import DatabaseService
from models.equipment import Equipment
from response.formatter import success_response, error_response

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Optional[Logger] = None) -> Dict[str, Any]:
    """
    Execute equipment operations based on HTTP method.
    """
    method = data.get("_method", "GET")
    db = DatabaseService(config, logger)
    collection = "equipments"
    
    # 1. LIST (GET)
    if method == "GET":
        # Check if getting single item
        doc_id = data.get("id")
        if doc_id:
            logger.info(f"Getting equipment {doc_id}")
            doc = db.get(collection, doc_id)
            if not doc:
                return error_response("not_found", "Equipment not found")
            return success_response(doc)
            
        # List all
        logger.info("Listing equipments")
        items = db.list(collection)
        return success_response(items)

    # 2. CREATE (POST)
    elif method == "POST":
        logger.info("Creating equipment")
        try:
            # Validate with model
            equipment = Equipment(**data)
            # Remove id if None so DB generates it (or use if provided)
            dump = equipment.model_dump(exclude_defaults=True)
            if "id" in dump and dump["id"] is None:
                del dump["id"]
                
            result = db.create(collection, dump)
            return success_response(result)
        except Exception as e:
            logger.error("Validation or creation failed", error=e)
            return error_response("invalid_request", str(e))

    return error_response("method_not_allowed", f"Method {method} not supported")
