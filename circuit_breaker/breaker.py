"""
Circuit Breaker
Prevents cascading failures by stopping requests to failing services
"""

import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit Breaker Pattern
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, failure_threshold=5, timeout=30, half_open_max_calls=3):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (OPEN -> HALF_OPEN)
            half_open_max_calls: Max calls to allow in HALF_OPEN state
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        
        logger.info("Circuit Breaker initialized")
    
    def call(self, func, *args, **kwargs):
        """
        Execute function through circuit breaker
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is OPEN or function fails
        """
        # Check if circuit should transition to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
        
        # Check HALF_OPEN call limit
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise Exception(f"Circuit breaker HALF_OPEN call limit reached")
            self.half_open_calls += 1
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Enough successes in HALF_OPEN, close circuit
            if self.success_count >= self.half_open_max_calls:
                self._transition_to_closed()
        
        logger.debug(f"Circuit breaker success (state: {self.state.value})")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure in HALF_OPEN, reopen circuit
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            # Check if should open circuit
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
        
        logger.warning(f"Circuit breaker failure (count: {self.failure_count}, state: {self.state.value})")
    
    def _should_attempt_reset(self):
        """Check if enough time has passed to try HALF_OPEN"""
        if self.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        logger.info(f"Circuit breaker: {self.state.value} -> CLOSED")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        logger.warning(f"Circuit breaker: {self.state.value} -> OPEN")
        self.state = CircuitState.OPEN
        self.success_count = 0
        self.half_open_calls = 0
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        logger.info(f"Circuit breaker: {self.state.value} -> HALF_OPEN")
        self.state = CircuitState.HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
    
    def reset(self):
        """Manually reset circuit breaker"""
        self._transition_to_closed()
        logger.info("Circuit breaker manually reset")
    
    def get_state(self):
        """Get current circuit breaker state"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time
        }
