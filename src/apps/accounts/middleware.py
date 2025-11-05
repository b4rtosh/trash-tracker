# apps/accounts/middleware.py
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Middleware to require login for all pages except exempted URLs.
    Exempted URLs: homepage, login, logout, signup, admin, static/media files.
    """
    EXEMPT_NAMES = ['login', 'logout', 'signup', 'home']  # URL names exempted
    EXEMPT_PATH_PREFIXES = ['/admin/', '/static/', '/media/']  # paths to skip

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow authenticated users to continue
        if request.user.is_authenticated:
            return self.get_response(request)

        path = request.path_info

        # Allow paths that start with exempt prefixes (admin, static, media)
        if any(path.startswith(p) for p in self.EXEMPT_PATH_PREFIXES):
            return self.get_response(request)

        # Resolve the URL name for the current path
        try:
            current_url_name = resolve(path).url_name
        except Exception:
            current_url_name = None

        # Allow access if the URL name is in the exempt list
        if current_url_name in self.EXEMPT_NAMES:
            return self.get_response(request)

        # Otherwise, redirect to login page with next parameter
        return redirect(f'{settings.LOGIN_URL}?next={path}')
