"""
Backend Service
Simulated backend service for testing load balancer
"""

from flask import Flask, jsonify
import time
import random
import os


def create_backend_service(name, port, failure_rate=0.0, slow_rate=0.0):
    """
    Create a simulated backend service
    
    Args:
        name: Service name
        port: Port to run on
        failure_rate: Probability of failure (0.0 to 1.0)
        slow_rate: Probability of slow response (0.0 to 1.0)
    """
    app = Flask(name)
    
    request_count = {'count': 0}
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': name,
            'port': port,
            'timestamp': time.time()
        })
    
    @app.route('/api/data')
    def get_data():
        """Sample API endpoint"""
        request_count['count'] += 1
        
        # Simulate random failures
        if random.random() < failure_rate:
            return jsonify({
                'error': 'Internal server error',
                'service': name
            }), 500
        
        # Simulate slow responses
        if random.random() < slow_rate:
            time.sleep(random.uniform(1, 3))
        
        return jsonify({
            'message': 'Success',
            'service': name,
            'port': port,
            'request_number': request_count['count'],
            'timestamp': time.time()
        })
    
    @app.route('/api/info')
    def get_info():
        """Service information endpoint"""
        return jsonify({
            'name': name,
            'port': port,
            'requests_handled': request_count['count'],
            'failure_rate': failure_rate,
            'slow_rate': slow_rate
        })
    
    return app


def run_backend_service(name, port, failure_rate=0.0, slow_rate=0.0):
    """
    Run a backend service
    
    Args:
        name: Service name
        port: Port to run on
        failure_rate: Probability of failure
        slow_rate: Probability of slow response
    """
    app = create_backend_service(name, port, failure_rate, slow_rate)
    
    print(f"Starting {name} on port {port}")
    print(f"  Failure rate: {failure_rate * 100}%")
    print(f"  Slow rate: {slow_rate * 100}%")
    
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    # Run a single backend service for testing
    import sys
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        name = f"backend-{port}"
        run_backend_service(name, port)
    else:
        print("Usage: python backend_service.py <port>")
