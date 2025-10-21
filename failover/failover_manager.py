"""
Failover Manager
Manages automatic failover and failback
"""

import logging
import time
from services.service_instance import ServiceInstance

logger = logging.getLogger(__name__)


class FailoverManager:
    """
    Failover Manager
    Handles automatic failover to backup instances
    """
    
    def __init__(self, load_balancer, enable_failback=True):
        """
        Initialize failover manager
        
        Args:
            load_balancer: LoadBalancer instance
            enable_failback: Whether to automatically failback to primary
        """
        self.load_balancer = load_balancer
        self.enable_failback = enable_failback
        self.primary_instances = {}
        self.backup_instances = {}
        self.failover_history = []
        
        logger.info("Failover Manager initialized")
    
    def set_primary(self, instance_name: str):
        """
        Mark an instance as primary
        
        Args:
            instance_name: Name of instance to mark as primary
        """
        instance = self.load_balancer.get_instance_by_name(instance_name)
        if instance:
            self.primary_instances[instance_name] = instance
            logger.info(f"Instance {instance_name} marked as primary")
    
    def set_backup(self, primary_name: str, backup_name: str):
        """
        Set backup instance for a primary
        
        Args:
            primary_name: Name of primary instance
            backup_name: Name of backup instance
        """
        backup = self.load_balancer.get_instance_by_name(backup_name)
        if backup:
            self.backup_instances[primary_name] = backup
            logger.info(f"Instance {backup_name} set as backup for {primary_name}")
    
    def check_and_failover(self):
        """
        Check primary instances and failover if needed
        """
        for primary_name, primary_instance in self.primary_instances.items():
            if not primary_instance.is_healthy():
                # Primary is unhealthy, check for backup
                if primary_name in self.backup_instances:
                    backup = self.backup_instances[primary_name]
                    
                    if backup.is_healthy():
                        self._perform_failover(primary_instance, backup)
    
    def check_and_failback(self):
        """
        Check if primary instances have recovered and failback
        """
        if not self.enable_failback:
            return
        
        for primary_name, primary_instance in self.primary_instances.items():
            if primary_instance.is_healthy():
                # Check if we're currently using backup
                if primary_name in self.backup_instances:
                    backup = self.backup_instances[primary_name]
                    
                    # Check if backup is currently active (has more requests)
                    if backup.total_requests > primary_instance.total_requests:
                        self._perform_failback(primary_instance, backup)
    
    def _perform_failover(self, primary: ServiceInstance, backup: ServiceInstance):
        """
        Perform failover from primary to backup
        
        Args:
            primary: Primary instance
            backup: Backup instance
        """
        logger.warning(f"FAILOVER: {primary.name} -> {backup.name}")
        
        # Record failover
        self.failover_history.append({
            'timestamp': time.time(),
            'type': 'failover',
            'from': primary.name,
            'to': backup.name,
            'reason': 'primary_unhealthy'
        })
        
        print(f"\n[WARNING]  FAILOVER: {primary.name} is unhealthy, switching to {backup.name}")
    
    def _perform_failback(self, primary: ServiceInstance, backup: ServiceInstance):
        """
        Perform failback from backup to primary
        
        Args:
            primary: Primary instance (now healthy)
            backup: Backup instance (currently active)
        """
        logger.info(f"FAILBACK: {backup.name} -> {primary.name}")
        
        # Record failback
        self.failover_history.append({
            'timestamp': time.time(),
            'type': 'failback',
            'from': backup.name,
            'to': primary.name,
            'reason': 'primary_recovered'
        })
        
        print(f"\n[PASS] FAILBACK: {primary.name} recovered, switching back from {backup.name}")
    
    def get_failover_history(self):
        """Get failover history"""
        return self.failover_history
    
    def get_failover_stats(self):
        """Get failover statistics"""
        total_failovers = sum(1 for f in self.failover_history if f['type'] == 'failover')
        total_failbacks = sum(1 for f in self.failover_history if f['type'] == 'failback')
        
        return {
            'total_failovers': total_failovers,
            'total_failbacks': total_failbacks,
            'recent_events': self.failover_history[-5:]
        }
