"""
Database service for Firestore operations.
"""
import uuid
from typing import Dict, Any, Optional, List
from google.cloud import firestore
from services.base import BaseService
from utils.logger import Logger
import os


class DatabaseService(BaseService):
    """
    Service for Firestore database operations.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        Initialize database service.
        
        Args:
            config: Database configuration (must include database.database_id)
            logger: Logger instance
        """
        super().__init__(config, logger)
        # Always use Google Cloud project for Firestore client
        # Priority: Config 'gcp_project_id' > Env 'GOOGLE_CLOUD_PROJECT' > Default
        self.gcp_project_id = config.get("gcp_project_id", os.getenv("GOOGLE_CLOUD_PROJECT", "pipuli-dev"))
        # Project ID from config
        self.project_id = config.get("project_id", "")
        
        # Get database_id from config (defaults to "(default)" if not specified)
        db_config = config.get("database", {})
        database_id = db_config.get("database_id", "(default)")
        
        # Check for external credentials
        credentials_path = config.get("credentials_path")
        
        if credentials_path:
            if not os.path.isabs(credentials_path):
                # Assume relative to project root
                base_path = os.getcwd()
                credentials_path = os.path.join(base_path, credentials_path)
            
            if os.path.exists(credentials_path):
                self._log("info", f"Using external credentials from: {credentials_path}")
                from google.oauth2 import service_account
                creds = service_account.Credentials.from_service_account_file(credentials_path)
                
                if database_id == "(default)":
                    self.db = firestore.Client(credentials=creds, project=self.gcp_project_id)
                else:
                    self.db = firestore.Client(credentials=creds, project=self.gcp_project_id, database=database_id)
            else:
                self._log("warning", f"Credentials file not found at {credentials_path}. Checking Secret Manager.")
                
                creds = None
                secret_name = config.get("credentials_secret_name")
                
                if secret_name:
                    self._log("info", f"Attempting to load credentials from secret: {secret_name}")
                    try:
                        from configs.loader import get_secret
                        import json
                        
                        secret_content = get_secret(secret_name)
                        if secret_content:
                            cred_dict = json.loads(secret_content)
                            from google.oauth2 import service_account
                            creds = service_account.Credentials.from_service_account_info(cred_dict)
                            self._log("info", "Successfully loaded credentials from Secret Manager")
                        else:
                            self._log("warning", "Secret content was empty")
                    except Exception as e:
                        self._log("error", "Failed to load credentials from Secret Manager", error=e)

                if creds:
                    if database_id == "(default)":
                        self.db = firestore.Client(credentials=creds, project=self.gcp_project_id)
                    else:
                        self.db = firestore.Client(credentials=creds, project=self.gcp_project_id, database=database_id)
                else:
                    self._log("warning", "Falling back to default credentials.")
                    # Initialize Firestore client with specific database using default credentials
                    # If database_id is "(default)", use default database
                    if database_id == "(default)":
                        self.db = firestore.Client(project=self.gcp_project_id)
                    else:
                        self.db = firestore.Client(project=self.gcp_project_id, database=database_id)
        else:
            # Initialize Firestore client with specific database using default credentials
            # If database_id is "(default)", use default database
            if database_id == "(default)":
                self.db = firestore.Client(project=self.gcp_project_id)
            else:
                self.db = firestore.Client(project=self.gcp_project_id, database=database_id)
        
        self._log("info", "Database service initialized", {
            "gcp_project": self.gcp_project_id,
            "database_id": database_id,
            "project_id": self.project_id,
            "using_credentials": bool(credentials_path)
        })
    
    def create(
        self,
        collection: str,
        data: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new document.
        
        Args:
            collection: Collection name
            data: Document data
            document_id: Optional document ID (if not provided, generates UUID)
        
        Returns:
            Created document with ID
        """
        self._log("info", f"Creating document in collection '{collection}'", {"data_keys": list(data.keys())})
        
        try:
            col_ref = self.db.collection(collection)
            
            # Generate document ID: UUID if not provided
            if not document_id:
                doc_id = uuid.uuid4().hex[:12]
            else:
                doc_id = document_id
            
            doc_ref = col_ref.document(doc_id)
            doc_ref.set(data)
            
            result = {"id": doc_id, **data}
            self._log("info", f"Document created successfully", {
                "document_id": doc_id,
                "collection": collection
            })
            return result
            
        except Exception as e:
            self._log("error", f"Error creating document", error=e, data={
                "collection": collection
            })
            raise
    
    def get(
        self,
        collection: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            collection: Collection name (project_id)
            document_id: Document ID
        
        Returns:
            Document data or None if not found
        """
        self._log("info", f"Getting document '{document_id}' from collection '{collection}'")
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                result = {"id": doc.id, **doc.to_dict()}
                self._log("info", f"Document retrieved successfully", {"document_id": document_id})
                return result
            else:
                self._log("warning", f"Document not found", data={"document_id": document_id})
                return None
                
        except Exception as e:
            self._log("error", f"Error getting document", error=e, data={"document_id": document_id})
            raise
    
    def update(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a document.
        
        Args:
            collection: Collection name (project_id)
            document_id: Document ID
            data: Data to update
        
        Returns:
            Updated document
        """
        self._log("info", f"Updating document '{document_id}' in collection '{collection}'", {"update_keys": list(data.keys())})
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            
            # Get updated document
            doc = doc_ref.get()
            result = {"id": doc.id, **doc.to_dict()}
            
            self._log("info", f"Document updated successfully", {"document_id": document_id})
            return result
            
        except Exception as e:
            self._log("error", f"Error updating document", error=e, data={"document_id": document_id})
            raise
    
    def delete(
        self,
        collection: str,
        document_id: str
    ) -> bool:
        """
        Delete a document.
        
        Args:
            collection: Collection name (project_id)
            document_id: Document ID
        
        Returns:
            True if deleted, False if not found
        """
        self._log("info", f"Deleting document '{document_id}' from collection '{collection}'")
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_ref.delete()
                self._log("info", f"Document deleted successfully", {"document_id": document_id})
                return True
            else:
                self._log("warning", f"Document not found for deletion", data={"document_id": document_id})
                return False
                
        except Exception as e:
            self._log("error", f"Error deleting document", error=e, data={"document_id": document_id})
            raise
    
    def list(
        self,
        collection: str,
        limit: int = 100,
        exclude_deleted: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List documents in a collection.
        
        Args:
            collection: Collection name (project_id)
            limit: Maximum number of documents to return
            exclude_deleted: If True, exclude documents with deletedAt field (soft delete)
        
        Returns:
            List of documents
        """
        self._log("info", f"Listing documents from collection '{collection}'", {
            "limit": limit,
            "exclude_deleted": exclude_deleted
        })
        
        try:
            docs = self.db.collection(collection).limit(limit).stream()
            results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            
            # Filter out soft-deleted documents if requested
            if exclude_deleted:
                initial_count = len(results)
                results = [r for r in results if not r.get("deletedAt")]
                filtered_count = initial_count - len(results)
                if filtered_count > 0:
                    self._log("debug", f"Filtered {filtered_count} soft-deleted documents")
            
            self._log("info", f"Retrieved {len(results)} documents", {
                "collection": collection,
                "count": len(results)
            })
            return results
            
        except Exception as e:
            self._log("error", f"Error listing documents", error=e, data={"collection": collection})
            raise

    def query(
        self,
        collection: str,
        filters: List[tuple] = [],
        order_by: Optional[str] = None,
        descending: bool = False,
        limit: int = 100,
        exclude_deleted: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query documents in a collection with filters and sorting.
        
        Args:
            collection: Collection name
            filters: List of tuples (field, operator, value) e.g. [("age", ">", 18)]
            order_by: Field to sort by
            descending: Sort direction
            limit: Max results
            exclude_deleted: If True, exclude documents with deletedAt field (soft delete)
            
        Returns:
            List of matching documents
        """
        self._log("info", f"Querying collection '{collection}'", {
            "filters": str(filters),
            "order_by": order_by,
            "descending": descending,
            "exclude_deleted": exclude_deleted
        })
        
        try:
            ref = self.db.collection(collection)
            
            for field, op, value in filters:
                ref = ref.where(filter=firestore.FieldFilter(field, op, value))
                
            if order_by:
                direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
                ref = ref.order_by(order_by, direction=direction)
                
            if limit:
                ref = ref.limit(limit)
                
            docs = ref.stream()
            results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            
            # Filter out soft-deleted documents if requested
            if exclude_deleted:
                initial_count = len(results)
                results = [r for r in results if not r.get("deletedAt")]
                filtered_count = initial_count - len(results)
                if filtered_count > 0:
                    self._log("debug", f"Filtered {filtered_count} soft-deleted documents")
            
            self._log("info", f"Query returned {len(results)} documents")
            return results
            
        except Exception as e:
            self._log("error", f"Error querying documents", error=e, data={"collection": collection})
            raise

