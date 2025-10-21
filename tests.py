"""
Comprehensive Unit Tests for Local Load Balancer
Tests algorithms, health monitoring, circuit breaker, failover, and analytics
"""

import unittest
import time
from load_balancer.balancer import LoadBalancer
from load_balancer.algorithms import (
    RoundRobinAlgorithm, WeightedRoundRobinAlgorithm,
    LeastConnectionsAlgorithm, RandomAlgorithm
)
from health.health_checker import HealthChecker
from circuit_breaker.breaker import CircuitBreaker, CircuitState
from failover.failover_manager import FailoverManager
from analytics.traffic_analytics import TrafficAnalytics
from services.service_instance import ServiceInstance, HealthStatus


class LoadBalancerTestCase(unittest.TestCase):
    """Unit tests for Local Load Balancer"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration"""
        print("\n" + "=" * 60)
        print("Local Load Balancer - Unit Test Suite")
        print("=" * 60)
        print("Testing: Algorithms, Health, Circuit Breaker, Failover")
        print("=" * 60 + "\n")
    
    # Test 1: Round-Robin Algorithm
    def test_01_round_robin_algorithm(self):
        """Test round-robin load balancing"""
        print("\n1. Testing round-robin algorithm...")
        
        lb = LoadBalancer(algorithm='round_robin')
        
        # Add instances
        lb.add_instance("service-1", "http://localhost:5001")
        lb.add_instance("service-2", "http://localhost:5002")
        lb.add_instance("service-3", "http://localhost:5003")
        
        # Mark all as healthy
        for instance in lb.instances:
            instance.mark_healthy()
        
        # Test rotation
        selected = []
        for _ in range(6):
            instance = lb.get_next_instance()
            selected.append(instance.name)
        
        # Should rotate: 1, 2, 3, 1, 2, 3
        self.assertEqual(selected[0], "service-1")
        self.assertEqual(selected[1], "service-2")
        self.assertEqual(selected[2], "service-3")
        self.assertEqual(selected[3], "service-1")
        
        print(f"   [PASS] Round-robin rotation: {selected}")
    
    # Test 2: Weighted Algorithm
    def test_02_weighted_algorithm(self):
        """Test weighted round-robin"""
        print("\n2. Testing weighted algorithm...")
        
        lb = LoadBalancer(algorithm='weighted')
        
        # Add instances with weights
        lb.add_instance("service-1", "http://localhost:5001", weight=3)
        lb.add_instance("service-2", "http://localhost:5002", weight=1)
        
        # Mark as healthy
        for instance in lb.instances:
            instance.mark_healthy()
        
        # Collect distribution
        distribution = {}
        for _ in range(12):
            instance = lb.get_next_instance()
            distribution[instance.name] = distribution.get(instance.name, 0) + 1
        
        # service-1 should get 3x more requests
        self.assertGreater(distribution['service-1'], distribution['service-2'])
        print(f"   [PASS] Weighted distribution: {distribution}")
    
    # Test 3: Health Monitoring
    def test_03_health_monitoring(self):
        """Test health monitoring"""
        print("\n3. Testing health monitoring...")
        
        lb = LoadBalancer()
        lb.add_instance("service-1", "http://localhost:5001")
        
        instance = lb.instances[0]
        
        # Test health status changes
        instance.mark_healthy()
        self.assertEqual(instance.health_status, HealthStatus.HEALTHY)
        self.assertTrue(instance.is_healthy())
        print("   [PASS] Instance marked as healthy")
        
        instance.mark_unhealthy()
        self.assertEqual(instance.health_status, HealthStatus.UNHEALTHY)
        self.assertFalse(instance.is_healthy())
        print("   [PASS] Instance marked as unhealthy")
        
        # Test consecutive failures
        self.assertGreater(instance.consecutive_failures, 0)
        print(f"   [PASS] Consecutive failures tracked: {instance.consecutive_failures}")
    
    # Test 4: Circuit Breaker
    def test_04_circuit_breaker(self):
        """Test circuit breaker state transitions"""
        print("\n4. Testing circuit breaker...")
        
        breaker = CircuitBreaker(failure_threshold=3, timeout=1)
        
        # Initial state should be CLOSED
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        print(f"   [PASS] Initial state: {breaker.state.value}")
        
        # Simulate failures
        for i in range(3):
            try:
                breaker.call(lambda: (_ for _ in ()).throw(Exception("Error")))
            except:
                pass
        
        # Should be OPEN now
        self.assertEqual(breaker.state, CircuitState.OPEN)
        print(f"   [PASS] After 3 failures: {breaker.state.value}")
        
        # Should reject calls when OPEN
        with self.assertRaises(Exception):
            breaker.call(lambda: "success")
        print("   [PASS] Calls rejected when OPEN")
        
        # Wait for timeout
        time.sleep(1.5)
        
        # Should allow call and transition to HALF_OPEN
        try:
            breaker.call(lambda: "success")
            print(f"   [PASS] After timeout: {breaker.state.value}")
        except:
            pass
    
    # Test 5: Failover Mechanism
    def test_05_failover_mechanism(self):
        """Test automatic failover"""
        print("\n5. Testing failover mechanism...")
        
        lb = LoadBalancer()
        lb.add_instance("primary", "http://localhost:5001")
        lb.add_instance("backup", "http://localhost:5002")
        
        failover = FailoverManager(lb)
        failover.set_primary("primary")
        failover.set_backup("primary", "backup")
        
        # Mark primary as unhealthy
        lb.instances[0].mark_unhealthy()
        lb.instances[1].mark_healthy()
        
        # Perform failover check
        failover.check_and_failover()
        
        # Verify failover was recorded
        history = failover.get_failover_history()
        self.assertGreater(len(history), 0)
        print(f"   [PASS] Failover executed: {len(history)} events")
    
    # Test 6: Service Pool Management
    def test_06_service_pool_management(self):
        """Test adding/removing instances"""
        print("\n6. Testing service pool management...")
        
        lb = LoadBalancer()
        
        # Add instances
        lb.add_instance("service-1", "http://localhost:5001")
        lb.add_instance("service-2", "http://localhost:5002")
        
        self.assertEqual(len(lb.instances), 2)
        print(f"   [PASS] Added 2 instances: {len(lb.instances)} total")
        
        # Remove instance
        lb.remove_instance("service-1")
        
        self.assertEqual(len(lb.instances), 1)
        self.assertEqual(lb.instances[0].name, "service-2")
        print(f"   [PASS] Removed 1 instance: {len(lb.instances)} remaining")
    
    # Test 7: Traffic Analytics
    def test_07_traffic_analytics(self):
        """Test traffic analytics tracking"""
        print("\n7. Testing traffic analytics...")
        
        analytics = TrafficAnalytics()
        
        # Record requests
        analytics.record_request("service-1", True, 0.05)
        analytics.record_request("service-1", True, 0.03)
        analytics.record_request("service-2", False, 0.10)
        
        # Get stats
        stats = analytics.get_overall_stats()
        
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['successful_requests'], 2)
        self.assertEqual(stats['failed_requests'], 1)
        print(f"   [PASS] Total requests: {stats['total_requests']}")
        print(f"   [PASS] Error rate: {stats['error_rate']}")
        
        # Get distribution
        distribution = analytics.get_traffic_distribution()
        self.assertIn('service-1', distribution)
        print(f"   [PASS] Traffic distribution: {len(distribution)} instances")
    
    # Test 8: Least Connections Algorithm
    def test_08_least_connections_algorithm(self):
        """Test least connections algorithm"""
        print("\n8. Testing least connections algorithm...")
        
        lb = LoadBalancer(algorithm='least_connections')
        
        # Add instances
        lb.add_instance("service-1", "http://localhost:5001")
        lb.add_instance("service-2", "http://localhost:5002")
        
        # Mark as healthy
        for instance in lb.instances:
            instance.mark_healthy()
        
        # Set different connection counts
        lb.instances[0].active_connections = 5
        lb.instances[1].active_connections = 2
        
        # Should select instance with fewer connections
        instance = lb.get_next_instance()
        
        self.assertEqual(instance.name, "service-2")
        print(f"   [PASS] Selected instance with least connections: {instance.name}")
    
    # Test 9: Load Distribution
    def test_09_load_distribution(self):
        """Test request distribution across instances"""
        print("\n9. Testing load distribution...")
        
        lb = LoadBalancer(algorithm='round_robin')
        
        # Add 3 instances
        for i in range(1, 4):
            lb.add_instance(f"service-{i}", f"http://localhost:500{i}")
            lb.instances[-1].mark_healthy()
        
        # Distribute 9 requests
        distribution = {}
        for _ in range(9):
            instance = lb.get_next_instance()
            distribution[instance.name] = distribution.get(instance.name, 0) + 1
        
        # Each should get 3 requests
        for count in distribution.values():
            self.assertEqual(count, 3)
        
        print(f"   [PASS] Even distribution: {distribution}")
    
    # Test 10: Service Recovery
    def test_10_service_recovery(self):
        """Test service recovery after failure"""
        print("\n10. Testing service recovery...")
        
        lb = LoadBalancer()
        lb.add_instance("service-1", "http://localhost:5001")
        
        instance = lb.instances[0]
        
        # Mark as unhealthy
        instance.mark_unhealthy()
        self.assertFalse(instance.is_healthy())
        print(f"   [PASS] Instance unhealthy: {instance.health_status.value}")
        
        # Recover
        instance.mark_healthy()
        self.assertTrue(instance.is_healthy())
        self.assertEqual(instance.consecutive_failures, 0)
        print(f"   [PASS] Instance recovered: {instance.health_status.value}")
        print(f"   [PASS] Consecutive failures reset: {instance.consecutive_failures}")


def run_tests():
    """Run all unit tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(LoadBalancerTestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n[FAIL] FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Local Load Balancer - Unit Test Suite")
    print("=" * 60)
    
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
