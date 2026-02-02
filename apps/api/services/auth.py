"""
Authentication service for validating Firebase ID Tokens.
"""
import firebase_admin
from firebase_admin import auth
from typing import Dict, Any, Optional
from utils.logger import Logger


class AuthService:
    """
    Service to handle authentication and token validation.
    Manages multiple Firebase App instances for multi-tenant support.
    """
    _apps = {}

    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize AuthService.
        
        Args:
            config: Project configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger.for_module("auth")
        self.auth_project_id = config.get("auth_project_id")

    def _get_app(self, project_id: str) -> firebase_admin.App:
        """
        Get or initialize Firebase App for a specific project.
        
        Args:
            project_id: Firebase Project ID
            
        Returns:
            Firebase App instance
        """
        if project_id in self._apps:
            return self._apps[project_id]
        
        try:
            # Check if already initialized globally
            return firebase_admin.get_app(name=project_id)
        except ValueError:
            # Initialize new app with specific project ID
            self.logger.info(f"Initializing Firebase App for project: {project_id}")
            
            options = {'projectId': project_id}
            credential = None
            
            # Check for credentials in config
            credentials_path = self.config.get("credentials_path")
            if credentials_path:
                import os
                if not os.path.isabs(credentials_path):
                    base_path = os.getcwd()
                    credentials_path = os.path.join(base_path, credentials_path)
                
                if os.path.exists(credentials_path):
                    self.logger.info(f"Using external credentials for Auth: {credentials_path}")
                    credential = firebase_admin.credentials.Certificate(credentials_path)
                else:
                    self.logger.warning(f"Credentials file not found at {credentials_path}. Falling back to default credentials.")
                    credential = None
            
            app = firebase_admin.initialize_app(
                credential=credential,
                options=options,
                name=project_id
            )
            self._apps[project_id] = app
            return app

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate Firebase ID Token.
        
        Args:
            token: JWT ID Token
            
        Returns:
            Decoded token claims (uid, email, etc)
            
        Raises:
            ValueError: If token is invalid or auth is not configured
        """
        if not self.auth_project_id:
            self.logger.warning("No auth_project_id configured, skipping token validation")
            return None

        try:
            app = self._get_app(self.auth_project_id)
            
            # Verify token
            # This validates the signature, expiration, and 'aud' (project_id)
            decoded_token = auth.verify_id_token(token, app=app)
            
            self.logger.info("Token validated successfully", {"uid": decoded_token.get("uid")})
            return decoded_token
            
        except Exception as e:
            self.logger.error(f"Token validation failed for project {self.auth_project_id}", error=e)
            raise ValueError(f"Invalid authentication token: {str(e)}")
