import time
import functools
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse

def get_client_ip(request):
    """Utility function to extract client IP address accurately from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip or '127.0.0.1'

def parse_rate(rate_str):
    """
    Parses rate limit strings like '5/m', '10/h', '100/d', '5/300s'.
    Returns (max_requests, period_seconds).
    """
    if isinstance(rate_str, (tuple, list)):
        return rate_str[0], rate_str[1]
    
    parts = rate_str.split('/')
    count = int(parts[0])
    unit = parts[1].lower() if len(parts) > 1 else 'm'
    
    if unit == 's':
        seconds = 1
    elif unit == 'm':
        seconds = 60
    elif unit == 'h':
        seconds = 3600
    elif unit == 'd':
        seconds = 86400
    elif unit.endswith('s') and unit[:-1].isdigit():
        seconds = int(unit[:-1])
    elif unit.endswith('m') and unit[:-1].isdigit():
        seconds = int(unit[:-1]) * 60
    else:
        seconds = 60
        
    return count, seconds

def ratelimit(rate='5/m', key='ip', block=True):
    """
    Decorator to rate limit view requests using Django Cache.
    
    Parameters:
    - rate: e.g. '5/m' (5 requests per min), '10/h' (10 per hour), '5/300s' (5 per 300s).
    - key: 'ip', 'user', or 'user_or_ip'.
    - block: If True, returns HTTP 429 when rate limit exceeded.
    """
    max_requests, period = parse_rate(rate)
    
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if key == 'user' and request.user.is_authenticated:
                identifier = f"user_{request.user.pk}"
            elif key == 'user_or_ip':
                identifier = f"user_{request.user.pk}" if request.user.is_authenticated else f"ip_{get_client_ip(request)}"
            else:
                identifier = f"ip_{get_client_ip(request)}"
                
            cache_key = f"ratelimit:{view_func.__name__}:{identifier}"
            
            history = cache.get(cache_key, [])
            now = time.time()
            # Filter out timestamps older than current period window
            history = [ts for ts in history if now - ts < period]
            
            if len(history) >= max_requests:
                if block:
                    retry_after = int(period - (now - history[0])) if history else period
                    error_msg = f"Rate limit exceeded. Too many requests. Please try again in {max(1, retry_after)} seconds."
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.endswith('/api/') or 'json' in request.META.get('HTTP_ACCEPT', ''):
                        response = JsonResponse({'status': 'error', 'message': error_msg}, status=429)
                    else:
                        response = HttpResponse(f"<h1>429 Too Many Requests</h1><p>{error_msg}</p>", status=429)
                    response['Retry-After'] = str(max(1, retry_after))
                    return response
            
            history.append(now)
            cache.set(cache_key, history, timeout=period)
            return view_func(request, *args, **kwargs)
            
        return _wrapped_view
    return decorator
