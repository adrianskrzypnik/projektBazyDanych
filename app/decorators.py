from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.http import JsonResponse


def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):

            return JsonResponse({
                'error': 'Brak uprawnień administratora',
                'status': 'forbidden'
            }, status=403)


        return view_func(request, *args, **kwargs)

    return wrapper