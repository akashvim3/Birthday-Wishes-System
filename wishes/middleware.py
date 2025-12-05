from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
import time


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to access any view
    except for login, register, and public pages.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        # Define public URLs that don't require authentication
        self.public_urls = [
            reverse('login'),
            reverse('register'),
            reverse('index'),
        ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            path = request.path_info

            # Check if current path is in public URLs or starts with /static/ or /media/
            if not any(path.startswith(url) for url in self.public_urls) and \
                    not path.startswith('/static/') and \
                    not path.startswith('/media/') and \
                    not path.startswith('/admin/'):
                return redirect('login')

        return None


def process_request(request):
    request.start_time = time.time()


class RequestTimingMiddleware(MiddlewareMixin):
    """
    Middleware to track request processing time
    """

    @staticmethod
    def process_response(request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Request-Duration'] = str(duration)
        return response


class UserActivityMiddleware(MiddlewareMixin):
    """
    Track user's last activity timestamp
    """

    @staticmethod
    def process_request(request):
        if request.user.is_authenticated:
            # Update last activity timestamp
            from django.utils import timezone
            from wishes.models import UserProfile

            try:
                profile = request.user.profile
                # You could add a last_activity field to UserProfile
                # profile.last_activity = timezone.now()
                # profile.save(update_fields=['last_activity'])
            except UserProfile.DoesNotExist:
                pass
