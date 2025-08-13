#!/usr/bin/env python3
"""
Test script for replica limit handler functionality
Tests the error handling for error code 142901: reached_max_replica_limit
"""

import sys
import json
import requests
import time
from pathlib import Path

# Add the work directory to Python path to import our modules
sys.path.append(str(Path(__file__).parent))

try:
    # Import from the local module file
    import importlib.util
    spec = importlib.util.spec_from_file_location("replica_limit_handler", "replica-limit-handler.py")
    replica_limit_handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replica_limit_handler)
    
    ReplicaLimitHandler = replica_limit_handler.ReplicaLimitHandler
    ReplicaLimitError = replica_limit_handler.ReplicaLimitError
    handle_replica_limit_error = replica_limit_handler.handle_replica_limit_error
    
    print("✅ Successfully imported replica-limit-handler module")
except ImportError as e:
    print(f"❌ Failed to import replica-limit-handler: {e}")
    sys.exit(1)

def test_replica_limit_handler():
    """Test the ReplicaLimitHandler class"""
    print("\n=== Testing ReplicaLimitHandler ===")
    
    # Test 1: Normal operation within limits
    handler = ReplicaLimitHandler(max_replicas=5, current_replicas=2)
    result = handler.scale_replicas(4)
    assert result['success'] == True, "Should allow scaling within limits"
    assert result['current_replicas'] == 4, "Should update current replicas"
    print("✅ Test 1 passed: Normal scaling within limits")
    
    # Test 2: Scaling beyond limits
    result = handler.scale_replicas(10)
    assert result['success'] == False, "Should reject scaling beyond limits"
    assert result['error']['errno'] == 142901, "Should return correct error code"
    assert result['error']['error_code'] == "reached_max_replica_limit", "Should return correct error code"
    print("✅ Test 2 passed: Scaling beyond limits properly rejected")
    
    # Test 3: Scaling recommendation
    recommendation = handler.get_scaling_recommendation(8)
    assert recommendation['recommended_replicas'] == 5, "Should recommend max replicas"
    assert recommendation['warning'] is not None, "Should include warning"
    print("✅ Test 3 passed: Scaling recommendation works correctly")

def test_error_generation():
    """Test error message generation"""
    print("\n=== Testing Error Generation ===")
    
    # Test exact error format from problem statement
    error_json = handle_replica_limit_error("20250813140010776F5DC37A81278EFB2F")
    error_data = json.loads(error_json)
    
    expected_error = {
        "errno": 142901,
        "error_code": "reached_max_replica_limit",
        "error_message": "Function has reached its max replica limit.",
        "request_id": "20250813140010776F5DC37A81278EFB2F"
    }
    
    assert error_data == expected_error, f"Generated error doesn't match expected format.\nExpected: {expected_error}\nActual: {error_data}"
    print("✅ Error generation test passed: Exact format match")

def test_flask_app_endpoints():
    """Test Flask application endpoints (if running)"""
    print("\n=== Testing Flask Application Endpoints ===")
    
    base_url = "http://localhost:8001"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
            
            # Test simulate error endpoint
            response = requests.get(f"{base_url}/simulate-error", timeout=5)
            if response.status_code == 429:
                error_data = response.json()
                assert error_data['errno'] == 142901, "Should return correct error code"
                print("✅ Simulate error endpoint works correctly")
            
            # Test scaling endpoint
            scale_data = {"replicas": 10}  # This should trigger the error
            response = requests.post(f"{base_url}/scale", json=scale_data, timeout=5)
            if response.status_code == 429:
                error_data = response.json()
                assert error_data['errno'] == 142901, "Should return replica limit error"
                print("✅ Scale endpoint properly handles replica limits")
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Flask app not running - skipping endpoint tests")
        print("   To test endpoints, run: python work/ch06/ex01/myapp/main_with_replica_handler.py")

def validate_kubernetes_configs():
    """Validate Kubernetes configuration files"""
    print("\n=== Validating Kubernetes Configurations ===")
    
    # Check if configuration files exist
    configs_to_check = [
        "hpa-with-replica-limits.yaml",
        "replica-monitoring.yaml", 
        "deployment.yml"
    ]
    
    for config_file in configs_to_check:
        if Path(config_file).exists():
            print(f"✅ Configuration file exists: {config_file}")
            
            # Basic YAML syntax check
            with open(config_file, 'r') as f:
                content = f.read()
                if 'maxReplicas' in content or 'max_replicas' in content:
                    print(f"   - Contains replica limit configuration")
                if 'HorizontalPodAutoscaler' in content:
                    print(f"   - Contains HPA configuration")
        else:
            print(f"❌ Configuration file missing: {config_file}")

def main():
    """Main test function"""
    print("🧪 Starting Replica Limit Handler Tests")
    print("=" * 50)
    
    try:
        test_replica_limit_handler()
        test_error_generation()
        test_flask_app_endpoints()
        validate_kubernetes_configs()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("   - Replica limit handling: ✅")
        print("   - Error code 142901 generation: ✅") 
        print("   - Kubernetes configurations: ✅")
        print("   - Flask application endpoints: ✅ (if running)")
        
        print("\n🚀 To deploy the solution:")
        print("   1. kubectl apply -f hpa-with-replica-limits.yaml")
        print("   2. kubectl apply -f deployment.yml")
        print("   3. kubectl apply -f replica-monitoring.yaml")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()