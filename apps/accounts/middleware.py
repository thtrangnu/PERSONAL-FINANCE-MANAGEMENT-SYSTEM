from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """Require authentication for all non-public pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated or self._is_public_path(request.path):
            return self.get_response(request)

        login_url = reverse('login')
        return redirect(f'{login_url}?next={request.get_full_path()}')

    def _is_public_path(self, path):
        public_paths = {
            reverse('landing'),
            reverse('login'),
            reverse('google_login_start'),
            reverse('register'),
        }
        public_prefixes = [
            settings.STATIC_URL,
            '/accounts/',
            '/healthz',
            '/metrics',
            '/favicon.ico',
        ]
        return path in public_paths or any(path.startswith(prefix) for prefix in public_prefixes if prefix)
