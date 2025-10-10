"""
Health Checker
Monitors service instance health
"""

import logging
import requests
import time
from threading import Thread
from services.service_instance import HealthStatus

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Health monitoring system
    Periodically checks service instance health
    """
    
    def __init__(self, load_balancer, check_interval=5, timeout=2, unhealthy_threshold=3):
        """
        Initialize health checker
        
        Args:
            load_balancer: LoadBalancer instance
            check_interval: Seconds between health checks
            timeout: Health check timeout
            unhealthy_threshold: Consecutive failures before marking unhealthy
        """
        self.load_balancer = load_balancer
        self.check_interval = check_interval
        self.timeout = timeout
        self.unhealthy_threshold = unhealthy_threshold
        self.running = False
        self.monitor_thread = None
        
        logger.info("Health Checker initialized")
    
    def start(self):
        """Start health monitoring in background thread"""
        self.running = True
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop(self):
        """Stop health monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.check_all_instances()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
    
    def check_all_instances(self):
        """Check health of all instances"""
        for instance in self.load_balancer.instances:
            self.check_instance_health(instance)
    
    def check_instance_health(self, instance):
        """
        Check health of a single instance
        
        Args:
            instance: ServiceInstance to check
        """
        try:
            # Make health check request
            health_url = f"{instance.url}/health"
            response = requests.get(health_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Instance is healthy
                instance.mark_healthy()
                logger.debug(f"Instance {instance.name} is healthy")
            else:
                # Instance returned error
                instance.mark_unhealthy()
                logger.warning(f"Instance {instance.name} returned status {response.status_code}")
        
        except requests.exceptions.Timeout:
            # Health check timed out
            instance.mark_unhealthy()
            logger.warning(f"Health check timeout for {instance.name}")
        
        except requests.exceptions.RequestException as e:
            # Health check failed
            instance.mark_unhealthy()
            logger.warning(f"Health check failed for {instance.name}: {e}")
        
        # Check if should mark as unhealthy
        if instance.consecutive_failures >= self.unhealthy_threshold:
            if instance.health_status != HealthStatus.UNHEALTHY:
                instance.mark_unhealthy()
                logger.error(f"Instance {instance.name} marked as UNHEALTHY after {instance.consecutive_failures} failures")
    
    def get_health_summary(self):
        """Get health summary of all instances"""
        summary = {
            'total_instances': len(self.load_balancer.instances),
            'healthy': 0,
            'unhealthy': 0,
            'degraded': 0,
            'unknown': 0,
            'instances': []
        }
        
        for instance in self.load_balancer.instances:
            status = instance.health_status.value
            summary[status] = summary.get(status, 0) + 1
            
            summary['instances'].append({
                'name': instance.name,
                'url': instance.url,
                'status': status,
                'consecutive_failures': instance.consecutive_failures,
                'last_check': instance.last_health_check.isoformat() if instance.last_health_check else None
            })
        
        return summary
