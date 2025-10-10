"""
Local Load Balancer - Main Demonstration
Shows examples of all load balancing features
"""

import time
from load_balancer.balancer import LoadBalancer
from load_balancer.algorithms import get_algorithm
from health.health_checker import HealthChecker
from circuit_breaker.breaker import CircuitBreaker, CircuitState
from failover.failover_manager import FailoverManager
from analytics.traffic_analytics import TrafficAnalytics
from services.service_instance import ServiceInstance, HealthStatus


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_round_robin():
    """Demonstrate round-robin algorithm"""
    print_section("1. Round-Robin Load Balancing")
    
    lb = LoadBalancer(algorithm='round_robin')
    
    # Add instances
    lb.add_instance("service-1", "http://localhost:5001")
    lb.add_instance("service-2", "http://localhost:5002")
    lb.add_instance("service-3", "http://localhost:5003")
    
    # Mark all as healthy for demo
    for instance in lb.instances:
        instance.mark_healthy()
    
    print("\n📊 Distributing 6 requests with Round-Robin:")
    for i in range(6):
        instance = lb.get_next_instance()
        print(f"   Request {i+1} -> {instance.name}")


def demo_weighted_algorithm():
    """Demonstrate weighted round-robin"""
    print_section("2. Weighted Round-Robin Algorithm")
    
    lb = LoadBalancer(algorithm='weighted')
    
    # Add instances with different weights
    lb.add_instance("service-1", "http://localhost:5001", weight=3)
    lb.add_instance("service-2", "http://localhost:5002", weight=2)
    lb.add_instance("service-3", "http://localhost:5003", weight=1)
    
    # Mark all as healthy
    for instance in lb.instances:
        instance.mark_healthy()
    
    print("\n📊 Distributing 12 requests with Weighted Round-Robin:")
    print("   Weights: service-1=3, service-2=2, service-3=1")
    
    distribution = {}
    for i in range(12):
        instance = lb.get_next_instance()
        distribution[instance.name] = distribution.get(instance.name, 0) + 1
    
    print("\n   Distribution:")
    for name, count in distribution.items():
        print(f"   {name}: {count} requests ({count/12*100:.1f}%)")


def demo_health_monitoring():
    """Demonstrate health monitoring"""
    print_section("3. Health Monitoring")
    
    lb = LoadBalancer()
    
    # Add instances
    lb.add_instance("service-1", "http://localhost:5001")
    lb.add_instance("service-2", "http://localhost:5002")
    
    # Simulate health states
    lb.instances[0].mark_healthy()
    lb.instances[1].mark_unhealthy()
    
    print("\n🏥 Instance Health Status:")
    for instance in lb.instances:
        print(f"   {instance.name}: {instance.health_status.value}")
    
    print("\n✅ Healthy instances:")
    healthy = lb.get_healthy_instances()
    for instance in healthy:
        print(f"   - {instance.name}")


def demo_circuit_breaker():
    """Demonstrate circuit breaker pattern"""
    print_section("4. Circuit Breaker Pattern")
    
    breaker = CircuitBreaker(failure_threshold=3, timeout=5)
    
    print(f"\n🔌 Initial state: {breaker.state.value}")
    
    # Simulate failures
    print("\n❌ Simulating 3 failures...")
    for i in range(3):
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Service error")))
        except:
            print(f"   Failure {i+1}: State = {breaker.state.value}")
    
    print(f"\n🔌 Circuit breaker is now: {breaker.state.value}")
    
    # Try to call when OPEN
    print("\n🚫 Trying to call when circuit is OPEN...")
    try:
        breaker.call(lambda: "success")
    except Exception as e:
        print(f"   ❌ Rejected: {e}")
    
    # Wait for timeout
    print(f"\n⏳ Waiting {breaker.timeout} seconds for timeout...")
    time.sleep(breaker.timeout)
    
    # Should transition to HALF_OPEN
    print("\n✅ Attempting call after timeout...")
    try:
        result = breaker.call(lambda: "success")
        print(f"   ✅ Success! State = {breaker.state.value}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def demo_failover():
    """Demonstrate failover mechanism"""
    print_section("5. Failover Mechanism")
    
    lb = LoadBalancer()
    
    # Add primary and backup
    lb.add_instance("primary", "http://localhost:5001", weight=2)
    lb.add_instance("backup", "http://localhost:5002", weight=1)
    
    # Setup failover
    failover = FailoverManager(lb)
    failover.set_primary("primary")
    failover.set_backup("primary", "backup")
    
    # Mark primary as healthy, backup as healthy
    lb.instances[0].mark_healthy()
    lb.instances[1].mark_healthy()
    
    print("\n✅ Initial state:")
    print(f"   Primary: {lb.instances[0].name} - {lb.instances[0].health_status.value}")
    print(f"   Backup: {lb.instances[1].name} - {lb.instances[1].health_status.value}")
    
    # Simulate primary failure
    print("\n❌ Primary instance fails...")
    lb.instances[0].mark_unhealthy()
    
    # Check and perform failover
    failover.check_and_failover()
    
    print("\n✅ After failover:")
    print(f"   Primary: {lb.instances[0].name} - {lb.instances[0].health_status.value}")
    print(f"   Backup: {lb.instances[1].name} - {lb.instances[1].health_status.value}")


def demo_traffic_analytics():
    """Demonstrate traffic analytics"""
    print_section("6. Traffic Analytics")
    
    analytics = TrafficAnalytics()
    
    # Simulate requests
    print("\n📊 Simulating requests...")
    analytics.record_request("service-1", True, 0.05)
    analytics.record_request("service-1", True, 0.03)
    analytics.record_request("service-2", True, 0.08)
    analytics.record_request("service-2", False, 0.10)
    analytics.record_request("service-3", True, 0.04)
    
    # Get overall stats
    print("\n📈 Overall Statistics:")
    stats = analytics.get_overall_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Successful: {stats['successful_requests']}")
    print(f"   Failed: {stats['failed_requests']}")
    print(f"   Error rate: {stats['error_rate']}")
    print(f"   Avg response time: {stats['avg_response_time']}")
    
    # Get distribution
    print("\n📊 Traffic Distribution:")
    distribution = analytics.get_traffic_distribution()
    for instance, data in distribution.items():
        print(f"   {instance}: {data['requests']} requests ({data['percentage']})")


def demo_least_connections():
    """Demonstrate least connections algorithm"""
    print_section("7. Least Connections Algorithm")
    
    lb = LoadBalancer(algorithm='least_connections')
    
    # Add instances
    lb.add_instance("service-1", "http://localhost:5001")
    lb.add_instance("service-2", "http://localhost:5002")
    lb.add_instance("service-3", "http://localhost:5003")
    
    # Mark all as healthy
    for instance in lb.instances:
        instance.mark_healthy()
    
    # Simulate different connection counts
    lb.instances[0].active_connections = 5
    lb.instances[1].active_connections = 2
    lb.instances[2].active_connections = 8
    
    print("\n📊 Active Connections:")
    for instance in lb.instances:
        print(f"   {instance.name}: {instance.active_connections} connections")
    
    print("\n🎯 Next 3 requests will go to instance with least connections:")
    for i in range(3):
        instance = lb.get_next_instance()
        print(f"   Request {i+1} -> {instance.name} ({instance.active_connections} connections)")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  Local Load Balancer - Demonstration")
    print("=" * 70)
    
    try:
        demo_round_robin()
        demo_weighted_algorithm()
        demo_health_monitoring()
        demo_circuit_breaker()
        demo_failover()
        demo_traffic_analytics()
        demo_least_connections()
        
        print("\n" + "=" * 70)
        print("  All Demonstrations Completed!")
        print("=" * 70)
        print("\nKey Concepts Demonstrated:")
        print("  1. Round-Robin - Even distribution")
        print("  2. Weighted - Priority-based distribution")
        print("  3. Health Monitoring - Track instance health")
        print("  4. Circuit Breaker - Prevent cascading failures")
        print("  5. Failover - Automatic backup switching")
        print("  6. Traffic Analytics - Request tracking")
        print("  7. Least Connections - Load-based distribution")
        print("\nTo run tests:")
        print("  python tests.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
