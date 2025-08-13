# Replica Limit Error Handler Solution

## Problem Statement
Application error occurred with the following details:
```json
{
  "errno": 142901,
  "error_code": "reached_max_replica_limit", 
  "error_message": "Function has reached its max replica limit.",
  "request_id": "20250813140010776F5DC37A81278EFB2F"
}
```

## Solution Overview

This solution implements comprehensive error handling for replica scaling limits in Docker/Kubernetes environments. It includes:

1. **Error Handler Module** (`replica-limit-handler.py`)
2. **Enhanced Flask Application** with replica limit awareness
3. **Kubernetes HPA Configuration** with proper scaling limits
4. **Monitoring and Alerting** setup
5. **Comprehensive Testing** suite

## Components

### 1. Replica Limit Handler (`replica-limit-handler.py`)

Core module that provides:
- `ReplicaLimitError` exception class
- `ReplicaLimitHandler` for managing scaling operations
- Exact error format generation matching the problem statement

Key features:
- Generates error code 142901 when replica limits are exceeded
- Provides scaling recommendations within limits
- Comprehensive logging and monitoring

### 2. Enhanced Flask Application

Updated Flask application with endpoints:
- `/health` - Health check with replica status
- `/scale` - POST endpoint for scaling requests
- `/simulate-error` - Generates the exact error from problem statement
- `/` - Original hello world with replica information

### 3. Kubernetes Configuration

#### HPA Configuration (`hpa-with-replica-limits.yaml`)
- Conservative scaling limits (maxReplicas: 5)
- CPU and memory-based scaling metrics
- Scaling behavior policies to prevent rapid scaling

#### Updated Deployment (`deployment.yml`)
- Resource limits and requests
- Environment variables for replica configuration
- Proper labels and annotations

#### Monitoring Setup (`replica-monitoring.yaml`)
- Prometheus monitoring configuration
- Alerting rules for replica limits
- Service discovery setup

## Usage

### Deploy to Kubernetes

```bash
# Apply the HPA configuration
kubectl apply -f hpa-with-replica-limits.yaml

# Deploy the application
kubectl apply -f deployment.yml

# Set up monitoring (optional)
kubectl apply -f replica-monitoring.yaml
```

### Test the Solution

```bash
# Run the test suite
python test-replica-limits.py

# Test Flask application endpoints
python ch06/ex01/myapp/main_with_replica_handler.py

# Test health endpoint
curl http://localhost:8001/health

# Test error simulation
curl http://localhost:8001/simulate-error

# Test scaling beyond limits
curl -X POST http://localhost:8001/scale \
  -H "Content-Type: application/json" \
  -d '{"replicas": 10}'
```

### Docker Build

```bash
# Build the enhanced application
cd ch06/ex01
docker build -f Dockerfile-replica-handler -t app-with-replica-limits .

# Run the container
docker run -p 8001:8001 \
  -e MAX_REPLICAS=5 \
  -e CURRENT_REPLICAS=1 \
  app-with-replica-limits
```

## Error Handling

The solution handles the replica limit error in multiple ways:

1. **Preventive**: HPA configuration prevents scaling beyond limits
2. **Reactive**: Application-level checks and error responses
3. **Monitoring**: Alerts when approaching or reaching limits

### Error Response Format

When replica limits are exceeded, the exact error format from the problem statement is returned:

```json
{
  "errno": 142901,
  "error_code": "reached_max_replica_limit",
  "error_message": "Function has reached its max replica limit.",
  "request_id": "20250813140010776F5DC37A81278EFB2F"
}
```

## Configuration

### Environment Variables

- `MAX_REPLICAS`: Maximum allowed replicas (default: 5)
- `CURRENT_REPLICAS`: Current replica count (default: 1)

### Kubernetes ConfigMap

The solution includes a ConfigMap for centralized configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: replica-limit-config
data:
  max_replicas: "5"
  error_code: "142901"
  error_message: "Function has reached its max replica limit."
```

## Monitoring and Alerts

### Prometheus Metrics

The solution exposes metrics for monitoring:
- Current replica count
- Maximum replica limit
- Utilization percentage

### Alert Rules

- **ReplicaLimitApproaching**: Warning when >80% of max replicas
- **ReplicaLimitReached**: Critical when at max replicas

## Testing

The test suite validates:
- Error code generation (142901)
- Scaling within and beyond limits
- Flask endpoint functionality
- Kubernetes configuration validity

Run tests with:
```bash
python test-replica-limits.py
```

## Files Created/Modified

1. `replica-limit-handler.py` - Core error handling module
2. `hpa-with-replica-limits.yaml` - HPA configuration
3. `replica-monitoring.yaml` - Monitoring setup
4. `deployment.yml` - Enhanced deployment
5. `ch06/ex01/myapp/main_with_replica_handler.py` - Enhanced Flask app
6. `ch06/ex01/Dockerfile-replica-handler` - Docker configuration
7. `ch06/ex01/requirements.txt` - Python dependencies
8. `test-replica-limits.py` - Comprehensive test suite
9. `README-replica-limits.md` - This documentation

## Best Practices Implemented

1. **Conservative Scaling**: Set reasonable replica limits
2. **Proper Resource Limits**: CPU and memory constraints
3. **Monitoring**: Comprehensive alerting and metrics
4. **Error Handling**: Graceful error responses
5. **Testing**: Thorough validation of functionality

This solution ensures that the replica limit error (142901) is properly handled while maintaining application functionality and providing appropriate feedback to users.