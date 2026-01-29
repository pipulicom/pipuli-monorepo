from typing import Dict, Any, Optional
from datetime import datetime
from services.database import DatabaseService
from logger.logger import Logger
from response.formatter import success_response, error_response
from version import VERSION

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Handle user login synchronization.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        User profile data or error if inactive
    """
    workflow_logger = logger.for_module("workflow.auth_login")
    
    # 1. Extract Auth Data
    auth_data = data.get("_auth")
    if not auth_data:
        workflow_logger.error("Missing auth data in request")
        return error_response(
            error="unauthorized",
            message="User not authenticated. Missing token."
        )
    
    uid = auth_data.get("uid")
    email = auth_data.get("email")
    # Firebase sometimes puts name/picture in 'claims' or top level depending on provider
    claims = auth_data.get("claims", {})
    name = claims.get("name") or auth_data.get("name") or email.split("@")[0]
    picture = claims.get("picture") or auth_data.get("picture")
    
    workflow_logger.info(f"Processing login for user: {email} ({uid})")
    
    # 2. Initialize Database
    db = DatabaseService(config, logger)
    collection = "users"
    
    try:
        # 3. Check if user exists
        user_doc = db.get(collection, uid)
        
        current_time = datetime.utcnow().isoformat()
        
        if not user_doc:
            # 4. Create New User
            workflow_logger.info("User not found, creating new profile")
            new_user = {
                "email": email,
                "name": name,
                "picture": picture,
                "created_at": current_time,
                "last_login": current_time,
                "status": False, # Inactive by default - requires admin approval
                "roles": ["user"]
            }
            db.create(collection, new_user, document_id=uid)
            
            return success_response(
                message="User created successfully",
                data={**new_user, "uid": uid, "version": VERSION}
            )
            
        else:
            # 5. Existing User - Update Login
            workflow_logger.info("Updating existing user profile")
            update_data = {
                "last_login": current_time
            }
            
            # Update profile info if changed and present
            if name and name != user_doc.get("name"):
                update_data["name"] = name
            if picture and picture != user_doc.get("picture"):
                update_data["picture"] = picture
                
            updated_user = db.update(collection, uid, update_data)
            
            # Return success with user data (including status field)
            # Frontend should check data.status to determine if user is active
            return success_response(
                message="Login successful",
                data={**updated_user, "version": VERSION}
            )
            
    except Exception as e:
        workflow_logger.error("Error processing login", error=e)
        return error_response(
            error="internal_error",
            message=f"Error processing login: {str(e)}"
        )
