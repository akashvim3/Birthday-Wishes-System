from django.http import JsonResponse
from django.db import connection
from django.utils import timezone


def health_check(request):
    """
    Health check endpoint for monitoring
    """
    status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': 'disconnected',
        'redis': 'disconnected'
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'connected'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['database'] = f'error: {str(e)}'

    # Check Redis connection
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 1)
        if cache.get('health_check') == 'ok':
            status['redis'] = 'connected'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'

    return JsonResponse(status)
