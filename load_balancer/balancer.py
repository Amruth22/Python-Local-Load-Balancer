"""
Load Balancer
Main load balancer implementation
"""

import logging
import requests
import time
from typing import List, Optional
from services.service_instance import ServiceInstance, HealthStatus
from load_balancer.algorithms import get_algorithm

logger = logging.getLogger(__name__)


class LoadBalancer:
    """
    Local Load Balancer
    Distributes requests across multiple service instances
    """
    
    def __init__(self, algorithm='round_robin'):
        """
        Initialize load balancer
        
        Args:
            algorithm: Load balancing algorithm to use
        """
        self.instances: List[ServiceInstance] = []
        self.algorithm = get_algorithm(algorithm)
        self.algorithm_name = algorithm
        
        logger.info(f"Load Balancer initialized with {algorithm} algorithm")
    
    def add_instance(self, name: str, url: str, weight: int = 1):
        """
        Add a service instance to the pool
        
        Args:
            name: Instance name
            url: Instance URL
            weight: Instance weight (for weighted algorithms)
        """
        instance = ServiceInstance(name, url, weight)
        self.instances.append(instance)
        
        logger.info(f"Added instance: {name} ({url}) with weight {weight}")
    
    def remove_instance(self, name: str):
        """
        Remove a service instance from the pool
        
        Args:
            name: Instance name to remove
        """
        self.instances = [i for i in self.instances if i.name != name]
        logger.info(f"Removed instance: {name}")
    
    def get_healthy_instances(self) -> List[ServiceInstance]:
        """Get list of healthy instances"""
        return [i for i in self.instances if i.is_healthy()]
    
    def get_next_instance(self) -> Optional[ServiceInstance]:
        """
        Get next instance using configured algorithm
        
        Returns:
            Selected service instance or None if no healthy instances
        """
        healthy_instances = self.get_healthy_instances()
        
        if not healthy_instances:
            logger.warning("No healthy instances available")
            return None
        
        instance = self.algorithm.select_instance(healthy_instances)
        
        if instance:
            logger.debug(f"Selected instance: {instance.name}")
        
        return instance
    
    def forward_request(self, path: str, method: str = 'GET', data: dict = None, timeout: int = 5):
        """
        Forward request to a service instance
        
        Args:
            path: Request path
            method: HTTP method
            data: Request data
            timeout: Request timeout
            
        Returns:
            Response from service or error
        """
        instance = self.get_next_instance()
        
        if not instance:
            return {
                'error': 'No healthy instances available',
                'status': 'error'
            }, 503
        
        # Increment connections
        instance.increment_connections()
        
        try:
            # Build URL
            url = f"{instance.url}{path}"
            
            # Make request
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            else:
                response = requests.request(method, url, json=data, timeout=timeout)
            
            response_time = time.time() - start_time
            
            # Record metrics
            success = response.status_code < 400
            instance.record_request(success, response_time)
            
            # Decrement connections
            instance.decrement_connections()
            
            return response.json(), response.status_code
            
        except requests.exceptions.Timeout:
            response_time = timeout
            instance.record_request(False, response_time)
            instance.decrement_connections()
            
            logger.error(f"Request to {instance.name} timed out")
            return {'error': 'Request timeout', 'service': instance.name}, 504
            
        except requests.exceptions.RequestException as e:
            instance.record_request(False, 0)
            instance.decrement_connections()
            
            logger.error(f"Request to {instance.name} failed: {e}")
            return {'error': str(e), 'service': instance.name}, 502
    
    def get_instance_by_name(self, name: str) -> Optional[ServiceInstance]:
        """Get instance by name"""
        for instance in self.instances:
            if instance.name == name:
                return instance
        return None
    
    def get_stats(self):
        """Get load balancer statistics"""
        total_requests = sum(i.total_requests for i in self.instances)
        total_failures = sum(i.failed_requests for i in self.instances)
        
        return {
            'algorithm': self.algorithm_name,
            'total_instances': len(self.instances),
            'healthy_instances': len(self.get_healthy_instances()),
            'total_requests': total_requests,
            'total_failures': total_failures,
            'overall_error_rate': f"{(total_failures / total_requests * 100) if total_requests > 0 else 0:.2f}%",
            'instances': [i.get_stats() for i in self.instances]
        }
