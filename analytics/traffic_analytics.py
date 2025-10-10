"""
Traffic Analytics
Track and analyze load balancer traffic
"""

import time
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class TrafficAnalytics:
    """
    Traffic analytics system
    Tracks requests, response times, errors, and distribution
    """
    
    def __init__(self):
        self.requests_by_instance = defaultdict(int)
        self.errors_by_instance = defaultdict(int)
        self.response_times = defaultdict(list)
        self.request_history = []
        self.start_time = time.time()
        
        logger.info("Traffic Analytics initialized")
    
    def record_request(self, instance_name, success, response_time):
        """
        Record a request
        
        Args:
            instance_name: Name of instance that handled request
            success: Whether request was successful
            response_time: Response time in seconds
        """
        # Increment request count
        self.requests_by_instance[instance_name] += 1
        
        # Record error if failed
        if not success:
            self.errors_by_instance[instance_name] += 1
        
        # Record response time
        self.response_times[instance_name].append(response_time)
        
        # Add to history
        self.request_history.append({
            'timestamp': datetime.now(),
            'instance': instance_name,
            'success': success,
            'response_time': response_time
        })
        
        # Limit history size
        if len(self.request_history) > 1000:
            self.request_history.pop(0)
    
    def get_instance_stats(self, instance_name):
        """Get statistics for a specific instance"""
        total_requests = self.requests_by_instance.get(instance_name, 0)
        total_errors = self.errors_by_instance.get(instance_name, 0)
        response_times = self.response_times.get(instance_name, [])
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'instance': instance_name,
            'total_requests': total_requests,
            'successful_requests': total_requests - total_errors,
            'failed_requests': total_errors,
            'error_rate': f"{error_rate:.2f}%",
            'avg_response_time': f"{avg_response_time:.4f}s",
            'min_response_time': f"{min(response_times):.4f}s" if response_times else "N/A",
            'max_response_time': f"{max(response_times):.4f}s" if response_times else "N/A"
        }
    
    def get_overall_stats(self):
        """Get overall statistics"""
        total_requests = sum(self.requests_by_instance.values())
        total_errors = sum(self.errors_by_instance.values())
        
        all_response_times = []
        for times in self.response_times.values():
            all_response_times.extend(times)
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        uptime = time.time() - self.start_time
        
        return {
            'total_requests': total_requests,
            'successful_requests': total_requests - total_errors,
            'failed_requests': total_errors,
            'error_rate': f"{error_rate:.2f}%",
            'avg_response_time': f"{avg_response_time:.4f}s",
            'uptime_seconds': uptime,
            'requests_per_second': total_requests / uptime if uptime > 0 else 0
        }
    
    def get_traffic_distribution(self):
        """Get traffic distribution across instances"""
        total_requests = sum(self.requests_by_instance.values())
        
        distribution = {}
        for instance_name, count in self.requests_by_instance.items():
            percentage = (count / total_requests * 100) if total_requests > 0 else 0
            distribution[instance_name] = {
                'requests': count,
                'percentage': f"{percentage:.2f}%"
            }
        
        return distribution
    
    def get_recent_requests(self, limit=10):
        """Get recent request history"""
        return self.request_history[-limit:]
    
    def reset(self):
        """Reset all analytics"""
        self.requests_by_instance.clear()
        self.errors_by_instance.clear()
        self.response_times.clear()
        self.request_history.clear()
        self.start_time = time.time()
        logger.info("Analytics reset")
