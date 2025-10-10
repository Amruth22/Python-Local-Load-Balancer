"""
Service Instance
Represents a single backend service instance
"""

from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceInstance:
    """
    Represents a backend service instance
    """
    
    def __init__(self, name, url, weight=1):
        """
        Initialize service instance
        
        Args:
            name: Instance name
            url: Instance URL
            weight: Weight for weighted load balancing (default: 1)
        """
        self.name = name
        self.url = url
        self.weight = weight
        
        # Health tracking
        self.health_status = HealthStatus.UNKNOWN
        self.last_health_check = None
        self.consecutive_failures = 0
        
        # Connection tracking
        self.active_connections = 0
        
        # Analytics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        
        # Timestamps
        self.created_at = datetime.now()
        self.last_request_at = None
    
    def mark_healthy(self):
        """Mark instance as healthy"""
        self.health_status = HealthStatus.HEALTHY
        self.consecutive_failures = 0
        self.last_health_check = datetime.now()
    
    def mark_unhealthy(self):
        """Mark instance as unhealthy"""
        self.health_status = HealthStatus.UNHEALTHY
        self.consecutive_failures += 1
        self.last_health_check = datetime.now()
    
    def mark_degraded(self):
        """Mark instance as degraded"""
        self.health_status = HealthStatus.DEGRADED
        self.last_health_check = datetime.now()
    
    def is_healthy(self):
        """Check if instance is healthy"""
        return self.health_status == HealthStatus.HEALTHY
    
    def increment_connections(self):
        """Increment active connection count"""
        self.active_connections += 1
    
    def decrement_connections(self):
        """Decrement active connection count"""
        self.active_connections = max(0, self.active_connections - 1)
    
    def record_request(self, success, response_time):
        """
        Record request metrics
        
        Args:
            success: Whether request was successful
            response_time: Response time in seconds
        """
        self.total_requests += 1
        self.last_request_at = datetime.now()
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_response_time += response_time
    
    def get_average_response_time(self):
        """Get average response time"""
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time / self.total_requests
    
    def get_error_rate(self):
        """Get error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    def get_stats(self):
        """Get instance statistics"""
        return {
            'name': self.name,
            'url': self.url,
            'weight': self.weight,
            'health_status': self.health_status.value,
            'active_connections': self.active_connections,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'error_rate': f"{self.get_error_rate():.2f}%",
            'avg_response_time': f"{self.get_average_response_time():.4f}s",
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None
        }
    
    def __repr__(self):
        return f"ServiceInstance(name={self.name}, url={self.url}, health={self.health_status.value})"
