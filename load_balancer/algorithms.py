"""
Load Balancing Algorithms
Different strategies for distributing traffic
"""

import random
from threading import Lock
from typing import List
from services.service_instance import ServiceInstance


class LoadBalancingAlgorithm:
    """Base class for load balancing algorithms"""
    
    def __init__(self):
        self.current_index = 0
    
    def select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select next instance
        Override in subclasses
        """
        raise NotImplementedError


class RoundRobinAlgorithm(LoadBalancingAlgorithm):
    """
    Round-Robin Algorithm
    Distributes requests evenly across all instances in rotation
    """

    def __init__(self):
        super().__init__()
        self._lock = Lock()

    def select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select next instance using round-robin

        Args:
            instances: List of healthy service instances

        Returns:
            Selected service instance
        """
        if not instances:
            return None

        with self._lock:
            # Get current instance
            instance = instances[self.current_index % len(instances)]

            # Move to next
            self.current_index += 1

        return instance


class WeightedRoundRobinAlgorithm(LoadBalancingAlgorithm):
    """
    Weighted Round-Robin Algorithm
    Distributes requests based on instance weights
    Higher weight = more requests
    """

    def __init__(self):
        super().__init__()
        self._lock = Lock()
        self.weighted_instances = []
        self.last_instances = None
    
    def select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select next instance using weighted round-robin

        Args:
            instances: List of healthy service instances

        Returns:
            Selected service instance
        """
        if not instances:
            return None

        with self._lock:
            # Rebuild weighted list if instances changed
            if instances != self.last_instances:
                self._build_weighted_list(instances)
                self.last_instances = instances

            if not self.weighted_instances:
                return instances[0]

            # Get current instance
            instance = self.weighted_instances[self.current_index % len(self.weighted_instances)]

            # Move to next
            self.current_index += 1

        return instance
    
    def _build_weighted_list(self, instances: List[ServiceInstance]):
        """Build weighted instance list"""
        self.weighted_instances = []
        
        for instance in instances:
            # Add instance multiple times based on weight
            for _ in range(instance.weight):
                self.weighted_instances.append(instance)


class LeastConnectionsAlgorithm(LoadBalancingAlgorithm):
    """
    Least Connections Algorithm
    Sends requests to instance with fewest active connections
    """
    
    def select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select instance with least connections
        
        Args:
            instances: List of healthy service instances
            
        Returns:
            Selected service instance
        """
        if not instances:
            return None
        
        # Find instance with minimum active connections
        return min(instances, key=lambda x: x.active_connections)


class RandomAlgorithm(LoadBalancingAlgorithm):
    """
    Random Algorithm
    Randomly selects an instance
    """
    
    def select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select random instance
        
        Args:
            instances: List of healthy service instances
            
        Returns:
            Selected service instance
        """
        if not instances:
            return None
        
        return random.choice(instances)


class LeastResponseTimeAlgorithm(LoadBalancingAlgorithm):
    """
    Least Response Time Algorithm
    Sends requests to instance with lowest average response time
    """
    
    def select_instance(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select instance with least response time
        
        Args:
            instances: List of healthy service instances
            
        Returns:
            Selected service instance
        """
        if not instances:
            return None
        
        # Find instance with minimum average response time
        return min(instances, key=lambda x: x.get_average_response_time())


# Algorithm factory
def get_algorithm(algorithm_name: str) -> LoadBalancingAlgorithm:
    """
    Get load balancing algorithm by name
    
    Args:
        algorithm_name: Name of algorithm
        
    Returns:
        Algorithm instance
    """
    algorithms = {
        'round_robin': RoundRobinAlgorithm,
        'weighted': WeightedRoundRobinAlgorithm,
        'least_connections': LeastConnectionsAlgorithm,
        'random': RandomAlgorithm,
        'least_response_time': LeastResponseTimeAlgorithm
    }
    
    algorithm_class = algorithms.get(algorithm_name.lower(), RoundRobinAlgorithm)
    return algorithm_class()
