# apps/accounts/middleware.py
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme

class LoginRequiredMiddleware:
    """
    Middleware to require login for all pages except exempted URLs.
    Exempted URLs: homepage, login, logout, signup, admin, static/media files.
    """
    EXEMPT_NAMES = ['login', 'logout', 'signup', 'home']
    EXEMPT_PATH_PREFIXES = ['/admin/', '/static/', '/media/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow authenticated users to continue
        if request.user.is_authenticated:
            return self.get_response(request)

        path = request.path_info

        # allow admin/static/media
        if any(path.startswith(p) for p in self.EXEMPT_PATH_PREFIXES):
            return self.get_response(request)

        # Resolve URL name
        try:
            current_url_name = resolve(path).url_name
        except Exception:
            current_url_name = None

        # Allow exempt URLs
        if current_url_name in self.EXEMPT_NAMES:
            return self.get_response(request)

        # Compute next parameter safely
        next_url = path  # candidate value from request

        # Validate 'next'
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"  # safe fallback

        login_url = settings.LOGIN_URL
        return redirect(f"{login_url}?next={next_url}")
