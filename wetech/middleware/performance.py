"""
Performance monitoring middleware
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Monitor request performance and log slow requests
    
    Add to MIDDLEWARE in settings.py:
    'wetech.middleware.performance.PerformanceMonitoringMiddleware',
    """
    
    def process_request(self, request):
        """Record request start time"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log slow requests"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (> 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.2f}s - Status: {response.status_code}",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration': duration,
                        'status_code': response.status_code,
                    }
                )
            # Log very slow requests (> 5 seconds) as errors
            elif duration > 5.0:
                logger.error(
                    f"Very slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s - Status: {response.status_code}",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration': duration,
                        'status_code': response.status_code,
                    }
                )
        
        return response

