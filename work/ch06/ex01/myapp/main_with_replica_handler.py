from flask import Flask, jsonify, request
import os
import json
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replica limit configuration
MAX_REPLICAS = int(os.environ.get('MAX_REPLICAS', 5))
CURRENT_REPLICAS = int(os.environ.get('CURRENT_REPLICAS', 1))

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
    
    def to_dict(self):
        """Convert error to dictionary format matching the error message"""
        return {
            "errno": self.errno,
            "error_code": "reached_max_replica_limit",
            "error_message": "Function has reached its max replica limit.",
            "request_id": self.request_id
        }

class ReplicaLimitHandler:
    """Handler for managing replica limits and error responses"""
    
    def __init__(self, max_replicas: int = 10, current_replicas: int = 0):
        self.max_replicas = max_replicas
        self.current_replicas = current_replicas
    
    def check_replica_limit(self, requested_replicas: int) -> bool:
        """Check if requested replicas would exceed the limit"""
        return requested_replicas > self.max_replicas
    
    def scale_replicas(self, new_replica_count: int):
        """Attempt to scale replicas, returning error if limit exceeded"""
        if self.check_replica_limit(new_replica_count):
            error = ReplicaLimitError(
                f"Cannot scale to {new_replica_count} replicas. Maximum allowed: {self.max_replicas}"
            )
            logger.error(f"Replica limit exceeded: {json.dumps(error.to_dict())}")
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

# Initialize replica handler
replica_handler = ReplicaLimitHandler(
    max_replicas=MAX_REPLICAS,
    current_replicas=CURRENT_REPLICAS
)

@app.route('/')
def hello_world():
    """Original hello world endpoint with replica info"""
    return jsonify({
        "message": "hello world!",
        "replica_status": {
            "current_replicas": replica_handler.current_replicas,
            "max_replicas": replica_handler.max_replicas
        }
    })

@app.route('/scale', methods=['POST'])
def scale_replicas():
    """Endpoint to simulate scaling requests"""
    try:
        data = request.get_json()
        if not data or 'replicas' not in data:
            return jsonify({"error": "Missing 'replicas' parameter"}), 400
        
        requested_replicas = data['replicas']
        
        if not isinstance(requested_replicas, int) or requested_replicas < 0:
            return jsonify({"error": "Invalid replica count"}), 400
        
        # Attempt to scale
        result = replica_handler.scale_replicas(requested_replicas)
        
        if not result['success']:
            # Return the exact error format from the problem statement
            return jsonify(result['error']), 429  # Too Many Requests
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in scale endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/simulate-error')
def simulate_error():
    """Endpoint that simulates the exact error from the problem statement"""
    error = ReplicaLimitError(
        "Function has reached its max replica limit.",
        request_id="20250813140010776F5DC37A81278EFB2F"
    )
    return jsonify(error.to_dict()), 429

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "replica_info": {
            "current": replica_handler.current_replicas,
            "maximum": replica_handler.max_replicas,
            "utilization": f"{(replica_handler.current_replicas / replica_handler.max_replicas) * 100:.1f}%"
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting app with max_replicas={MAX_REPLICAS}")
    app.run(host='0.0.0.0', port=8001)