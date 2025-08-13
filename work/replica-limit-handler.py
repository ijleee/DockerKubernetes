#!/usr/bin/env python3
"""
Replica Limit Handler - Error handling for max replica limit scenarios
Handles error code 142901: reached_max_replica_limit
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReplicaLimitError(Exception):
    """Custom exception for replica limit errors"""
    def __init__(self, message: str, error_code: str = "142901", request_id: str = None):
        self.message = message
        self.error_code = error_code
        self.errno = int(error_code)
        self.request_id = request_id or self._generate_request_id()
        super().__init__(self.message)
    
    def _generate_request_id(self) -> str:
        """Generate a request ID based on timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        return f"{timestamp}F5DC37A81278EFB2F"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format matching the error message"""
        return {
            "errno": self.errno,
            "error_code": "reached_max_replica_limit",
            "error_message": "Function has reached its max replica limit.",
            "request_id": self.request_id
        }
    
    def to_json(self) -> str:
        """Convert error to JSON format"""
        return json.dumps(self.to_dict())

class ReplicaLimitHandler:
    """Handler for managing replica limits and error responses"""
    
    def __init__(self, max_replicas: int = 10, current_replicas: int = 0):
        self.max_replicas = max_replicas
        self.current_replicas = current_replicas
    
    def check_replica_limit(self, requested_replicas: int) -> bool:
        """Check if requested replicas would exceed the limit"""
        return requested_replicas > self.max_replicas
    
    def scale_replicas(self, new_replica_count: int) -> Dict[str, Any]:
        """
        Attempt to scale replicas, returning error if limit exceeded
        """
        if self.check_replica_limit(new_replica_count):
            error = ReplicaLimitError(
                f"Cannot scale to {new_replica_count} replicas. Maximum allowed: {self.max_replicas}"
            )
            logger.error(f"Replica limit exceeded: {error.to_json()}")
            return {
                "success": False,
                "error": error.to_dict()
            }
        
        self.current_replicas = new_replica_count
        logger.info(f"Successfully scaled to {new_replica_count} replicas")
        return {
            "success": True,
            "current_replicas": self.current_replicas,
            "max_replicas": self.max_replicas
        }
    
    def get_scaling_recommendation(self, target_replicas: int) -> Dict[str, Any]:
        """
        Get a scaling recommendation that respects replica limits
        """
        if target_replicas > self.max_replicas:
            recommended_replicas = self.max_replicas
            warning = f"Requested {target_replicas} replicas, but maximum is {self.max_replicas}. Recommending {recommended_replicas}."
        else:
            recommended_replicas = target_replicas
            warning = None
        
        return {
            "requested_replicas": target_replicas,
            "recommended_replicas": recommended_replicas,
            "max_replicas": self.max_replicas,
            "warning": warning
        }

def handle_replica_limit_error(request_id: str = None) -> str:
    """
    Generate the exact error response format from the problem statement
    """
    error = ReplicaLimitError(
        "Function has reached its max replica limit.",
        request_id=request_id or "20250813140010776F5DC37A81278EFB2F"
    )
    return error.to_json()

# Example usage and testing
if __name__ == "__main__":
    # Demonstrate the error handling
    print("=== Replica Limit Error Handler Demo ===")
    
    # Generate the exact error from the problem statement
    error_response = handle_replica_limit_error()
    print(f"Error Response: {error_response}")
    
    # Demonstrate the handler functionality
    handler = ReplicaLimitHandler(max_replicas=5, current_replicas=3)
    
    # Test successful scaling
    result = handler.scale_replicas(4)
    print(f"Scale to 4 replicas: {json.dumps(result, indent=2)}")
    
    # Test failed scaling (exceeds limit)
    result = handler.scale_replicas(10)
    print(f"Scale to 10 replicas: {json.dumps(result, indent=2)}")
    
    # Test scaling recommendation
    recommendation = handler.get_scaling_recommendation(8)
    print(f"Scaling recommendation: {json.dumps(recommendation, indent=2)}")