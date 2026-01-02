"""
Retry decorator for external API calls
"""
import time
import logging
from functools import wraps
import requests

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator for functions that may fail temporarily
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    
    Usage:
        @retry_on_failure(max_retries=3, delay=2)
        def pesapal_api_call():
            # Your API code
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    last_exception = e
                    
                    if retries >= max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} attempts: {str(e)}",
                            exc_info=True
                        )
                        raise
                    
                    wait_time = delay * (backoff ** (retries - 1))
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {retries}/{max_retries}). "
                        f"Retrying in {wait_time}s: {str(e)}"
                    )
                    time.sleep(wait_time)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

# Specific retry decorator for network operations
retry_network = retry_on_failure(
    max_retries=3,
    delay=2,
    backoff=2,
    exceptions=(requests.exceptions.ConnectionError, requests.exceptions.Timeout)
)

