from typing import Dict, Any
from workflows.base import Workflow
import uuid
import datetime

class SystemHealthCheck(Workflow):
    """
    Workflow to verify system health by performing a full database CRUD cycle.
    """
    
    def validate(self, data: Dict[str, Any]):
        # Optional metadata can be passed, but nothing is strictly required
        return True
        
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Setup
        check_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        collection = "admin_health_checks"
        
        doc_data = {
            "check_id": check_id,
            "timestamp": timestamp,
            "type": data.get("type", "manual_trigger"),
            "components_checked": ["firestore", "logger"],
            "status": "running",
            "meta": data.get("meta", {})
        }
        
        self.workflow_logger.info(f"Starting health check {check_id}")
        
        # 2. Create (Write Test)
        try:
            created_doc = self.db.create(collection, doc_data, document_id=check_id)
            self.workflow_logger.info("Write test passed")
        except Exception as e:
            return self.error("write_error", f"Firestore write failed: {str(e)}")
        
        # 3. Read (Read Test)
        try:
            read_doc = self.db.get(collection, check_id)
            if not read_doc:
                return self.error("read_error", "Firestore read returned None")
            self.workflow_logger.info("Read test passed")
        except Exception as e:
            return self.error("read_error", f"Firestore read failed: {str(e)}")
            
        # 4. Update (Update Test)
        try:
            update_data = {
                "status": "completed",
                "completed_at": datetime.datetime.utcnow().isoformat()
            }
            updated_doc = self.db.update(collection, check_id, update_data)
            self.workflow_logger.info("Update test passed")
        except Exception as e:
            return self.error("update_error", f"Firestore update failed: {str(e)}")
        
        return self.success({
            "check_id": check_id,
            "status": "healthy",
            "steps": {
                "write": "success",
                "read": "success",
                "update": "success"
            },
            "final_document": updated_doc
        }, message="System health check completed successfully")


def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Any) -> Dict[str, Any]:
    """
    Entry point for the workflow.
    """
    workflow = SystemHealthCheck(config, logger)
    return workflow.run(data)

