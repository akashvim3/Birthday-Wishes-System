from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def profile_required(view_func):
    """
    Decorator to ensure user has completed their profile
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            profile = request.user.profile
            if not profile.birthday:
                messages.warning(request, 'Please complete your profile first.')
                return redirect('profile')
        except:
            messages.warning(request, 'Please complete your profile first.')
            return redirect('profile')

        return view_func(request, *args, **kwargs)

    return wrapper


def ajax_required(view_func):
    """
    Decorator to ensure request is AJAX
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden('This endpoint only accepts AJAX requests')
        return view_func(request, *args, **kwargs)

    return wrapper


def owner_required(model_class, pk_field='pk'):
    """
    Decorator to ensure user is the owner of the object
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            obj_id = kwargs.get(pk_field)
            obj = model_class.objects.get(pk=obj_id)

            if hasattr(obj, 'user'):
                if obj.user != request.user:
                    return HttpResponseForbidden('You do not have permission to access this.')
            elif hasattr(obj, 'sender'):
                if obj.sender != request.user:
                    return HttpResponseForbidden('You do not have permission to access this.')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
