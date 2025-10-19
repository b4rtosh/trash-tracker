# apps/accounts/middleware.py
from django.shortcuts import redirect
from django.conf import settings

EXEMPT_URLS = [
    '/accounts/login/',
    '/accounts/signup/',
    '/accounts/logout/',
    '/admin/',
    '/admin/login/',
    '/admin/logout/',
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            if not any(path.startswith(url) for url in EXEMPT_URLS):
                return redirect(f'{settings.LOGIN_URL}?next={path}')
        return self.get_response(request)
