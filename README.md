# Local Load Balancer

Educational Python application demonstrating **local load balancing**, **health monitoring**, **round-robin/weighted algorithms**, **circuit breaker patterns**, **service health endpoints**, **failover mechanisms**, and **traffic analytics**.

## Features

### ⚖️ Load Balancing Algorithms
- **Round-Robin** - Even distribution across instances
- **Weighted Round-Robin** - Priority-based distribution
- **Least Connections** - Send to instance with fewest connections
- **Random** - Random instance selection
- **Least Response Time** - Send to fastest instance

### 🏥 Health Monitoring
- **Periodic Health Checks** - Automatic health verification
- **Health Status Tracking** - Healthy, Unhealthy, Degraded
- **Consecutive Failure Tracking** - Count failures before marking unhealthy
- **Auto-Recovery Detection** - Re-enable when healthy
- **Health Endpoints** - `/health` API for each service

### 🔌 Circuit Breaker Pattern
- **Three States** - CLOSED, OPEN, HALF_OPEN
- **Failure Threshold** - Open after N failures
- **Timeout Recovery** - Try again after timeout
- **Half-Open Testing** - Test recovery with limited calls
- **Cascading Failure Prevention** - Stop calling failing services

### 🔄 Failover Mechanisms
- **Primary/Backup** - Automatic backup switching
- **Auto-Failover** - Switch when primary fails
- **Failback** - Return to primary when recovered
- **Failover History** - Track all failover events
- **Health-Based** - Failover based on health status

### 📊 Traffic Analytics
- **Request Tracking** - Count requests per instance
- **Success/Error Rates** - Track failure rates
- **Response Time** - Average, min, max latency
- **Traffic Distribution** - Percentage per instance
- **Request History** - Recent request log

### 🎯 Service Pool Management
- **Add/Remove Instances** - Dynamic instance management
- **Instance Metadata** - Track name, URL, weight
- **Connection Tracking** - Active connection count
- **Statistics** - Per-instance metrics

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Amruth22/Python-Local-Load-Balancer.git
cd Python-Local-Load-Balancer
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Demonstrations
```bash
python main.py
```

### 5. Run Tests
```bash
python tests.py
```

## Project Structure

```
Python-Local-Load-Balancer/
│
├── load_balancer/
│   ├── balancer.py              # Main load balancer
│   └── algorithms.py            # Load balancing algorithms
│
├── health/
│   └── health_checker.py        # Health monitoring
│
├── circuit_breaker/
│   └── breaker.py               # Circuit breaker pattern
│
├── failover/
│   └── failover_manager.py      # Failover logic
│
├── analytics/
│   └── traffic_analytics.py     # Traffic tracking
│
├── services/
│   ├── service_instance.py      # Service instance class
│   └── backend_service.py       # Simulated backend
│
├── main.py                      # Demonstration script
├── tests.py                     # 10 unit tests
├── requirements.txt             # Dependencies
├── .env                         # Configuration
└── README.md                    # This file
```

## Architecture Diagram

```
                    ┌─────────────────────┐
                    │   Client Requests   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Load Balancer     │
                    │  ┌───────────────┐  │
                    │  │  Algorithm    │  │
                    │  │ - Round-Robin │  │
                    │  │ - Weighted    │  │
                    │  │ - Least Conn  │  │
                    │  └───────────────┘  │
                    │  ┌───────────────┐  │
                    │  │Circuit Breaker│  │
                    │  └───────────────┘  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐   ┌─────────▼────────┐   ┌───────▼────────┐
│  Service 1     │   │   Service 2      │   │  Service 3     │
│  Port: 5001    │   │   Port: 5002     │   │  Port: 5003    │
│  Status: ✅    │   │   Status: ✅     │   │  Status: ❌    │
│  Conn: 3       │   │   Conn: 1        │   │  Conn: 0       │
└────────────────┘   └──────────────────┘   └────────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Health Monitor     │
                    │  - Check every 5s   │
                    │  - Mark unhealthy   │
                    │  - Auto-recovery    │
                    └─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Traffic Analytics   │
                    │  - Request count    │
                    │  - Response time    │
                    │  - Error rate       │
                    └─────────────────────┘
```

## Usage Examples

### Basic Load Balancer

```python
from load_balancer.balancer import LoadBalancer

# Create load balancer with round-robin
lb = LoadBalancer(algorithm='round_robin')

# Add service instances
lb.add_instance("service-1", "http://localhost:5001")
lb.add_instance("service-2", "http://localhost:5002")
lb.add_instance("service-3", "http://localhost:5003")

# Mark instances as healthy
for instance in lb.instances:
    instance.mark_healthy()

# Get next instance
instance = lb.get_next_instance()
print(f"Selected: {instance.name}")
```

### Weighted Load Balancing

```python
# Create load balancer with weighted algorithm
lb = LoadBalancer(algorithm='weighted')

# Add instances with different weights
lb.add_instance("powerful-server", "http://localhost:5001", weight=3)
lb.add_instance("medium-server", "http://localhost:5002", weight=2)
lb.add_instance("small-server", "http://localhost:5003", weight=1)

# powerful-server gets 3x more traffic than small-server
```

### Health Monitoring

```python
from health.health_checker import HealthChecker

# Create health checker
checker = HealthChecker(lb, check_interval=5, timeout=2)

# Start monitoring
checker.start()

# Get health summary
summary = checker.get_health_summary()
print(f"Healthy instances: {summary['healthy']}")
print(f"Unhealthy instances: {summary['unhealthy']}")

# Stop monitoring
checker.stop()
```

### Circuit Breaker

```python
from circuit_breaker.breaker import CircuitBreaker

# Create circuit breaker
breaker = CircuitBreaker(failure_threshold=5, timeout=30)

# Use circuit breaker
try:
    result = breaker.call(lambda: make_api_call())
    print(f"Success: {result}")
except Exception as e:
    print(f"Circuit breaker rejected: {e}")

# Check state
print(f"Circuit state: {breaker.state.value}")
```

### Failover

```python
from failover.failover_manager import FailoverManager

# Create failover manager
failover = FailoverManager(lb, enable_failback=True)

# Set primary and backup
failover.set_primary("service-1")
failover.set_backup("service-1", "service-2")

# Check and perform failover if needed
failover.check_and_failover()

# Get failover history
history = failover.get_failover_history()
```

### Traffic Analytics

```python
from analytics.traffic_analytics import TrafficAnalytics

# Create analytics
analytics = TrafficAnalytics()

# Record requests
analytics.record_request("service-1", success=True, response_time=0.05)
analytics.record_request("service-2", success=False, response_time=0.10)

# Get statistics
stats = analytics.get_overall_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Error rate: {stats['error_rate']}")

# Get distribution
distribution = analytics.get_traffic_distribution()
```

## Load Balancing Algorithms Comparison

| Algorithm | Use Case | Pros | Cons |
|-----------|----------|------|------|
| **Round-Robin** | Equal servers | Simple, fair | Ignores load |
| **Weighted** | Different capacity | Respects capacity | Static weights |
| **Least Connections** | Long requests | Dynamic load | More overhead |
| **Random** | Simple distribution | Very simple | Less predictable |
| **Least Response Time** | Performance-critical | Optimizes latency | Requires tracking |

## Circuit Breaker States

```
┌─────────────┐
│   CLOSED    │  Normal operation
│             │  Requests pass through
└──────┬──────┘
       │ Failures >= Threshold
       ▼
┌─────────────┐
│    OPEN     │  Too many failures
│             │  Reject all requests
└──────┬──────┘
       │ Timeout elapsed
       ▼
┌─────────────┐
│ HALF_OPEN   │  Testing recovery
│             │  Allow limited requests
└──────┬──────┘
       │
       ├─ Success → CLOSED
       └─ Failure → OPEN
```

## Testing

Run the comprehensive test suite:

```bash
python tests.py
```

### Test Coverage (10 Tests)

1. ✅ **Round-Robin Algorithm** - Test rotation
2. ✅ **Weighted Algorithm** - Test weight distribution
3. ✅ **Health Monitoring** - Test health checks
4. ✅ **Circuit Breaker** - Test state transitions
5. ✅ **Failover Mechanism** - Test automatic failover
6. ✅ **Service Pool** - Test instance management
7. ✅ **Traffic Analytics** - Test metrics tracking
8. ✅ **Least Connections** - Test connection-based routing
9. ✅ **Load Distribution** - Test request distribution
10. ✅ **Service Recovery** - Test recovery after failure

## Educational Notes

### 1. Why Load Balancing?

**Benefits:**
- **High Availability** - No single point of failure
- **Scalability** - Handle more traffic
- **Performance** - Distribute load evenly
- **Reliability** - Failover to healthy instances

### 2. Circuit Breaker Pattern

**Purpose:**
- Prevent cascading failures
- Fast failure detection
- Automatic recovery testing
- System stability

**When to Use:**
- Calling external services
- Microservices communication
- Unreliable dependencies

### 3. Health Monitoring

**Why Monitor?**
- Detect failures quickly
- Remove unhealthy instances
- Prevent bad requests
- Enable auto-recovery

### 4. Failover vs Load Balancing

**Failover:**
- Primary/backup model
- Switch on failure
- High availability focus

**Load Balancing:**
- Distribute across all
- Performance focus
- Scalability focus

## Production Considerations

For production use:

1. **External Load Balancer:**
   - Use HAProxy, Nginx, or cloud LB
   - Hardware load balancers
   - DNS-based load balancing

2. **Persistence:**
   - Session persistence (sticky sessions)
   - Consistent hashing
   - Cookie-based routing

3. **Advanced Features:**
   - SSL/TLS termination
   - HTTP/2 support
   - WebSocket support
   - Rate limiting

4. **Monitoring:**
   - Metrics collection
   - Alerting
   - Dashboards
   - Distributed tracing

5. **Scalability:**
   - Auto-scaling
   - Geographic distribution
   - CDN integration

## Dependencies

- **Flask 3.0.0** - Web framework
- **requests 2.31.0** - HTTP client
- **python-dotenv 1.0.0** - Environment variables
- **pytest 7.4.3** - Testing framework

## License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Happy Learning! 🚀**
