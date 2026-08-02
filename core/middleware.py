from django.contrib.auth import logout
from django.shortcuts import render
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthForbidden


class ActiveUserCheckMiddleware:
    """
    Middleware that checks if a logged-in user has been deactivated/blocked (is_active=False).
    If a blocked user tries to make any request or continue their session:
    - Logs them out immediately.
    - Displays a clean 'Account Suspended' page instead of an exception.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            return render(request, 'core/blocked.html', {
                'reason': 'Your account has been temporarily deactivated by the MCSC Administrator.'
            }, status=403)

        return self.get_response(request)


class MCSCSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    """
    Catches social auth exceptions (e.g. blocked user logging in via Google)
    and renders the friendly blocked.html template instead of a raw 500/exception page.
    """
    def process_exception(self, request, exception):
        if isinstance(exception, AuthForbidden):
            return render(request, 'core/blocked.html', {
                'reason': str(exception)
            }, status=403)
        return super().process_exception(request, exception)


class SecurityHeadersMiddleware:
    """
    Middleware to inject security headers including Content-Security-Policy (CSP),
    COOP, Referrer-Policy, and X-Content-Type-Options into all HTTP responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        csp_policies = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://apis.google.com https://accounts.google.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://api.fontshare.com",
            "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net https://api.fontshare.com",
            "img-src 'self' data: blob: https:",
            "connect-src 'self' https://*.supabase.co https://accounts.google.com https://cdn.jsdelivr.net https://cdn.tailwindcss.com",
            "frame-src 'self' https://accounts.google.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self' https://accounts.google.com",
        ]
        
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = "; ".join(csp_policies)
            
        if 'Referrer-Policy' not in response:
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
            
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'SAMEORIGIN'
            
        if 'Cross-Origin-Opener-Policy' not in response:
            response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
            
        if 'Permissions-Policy' not in response:
            response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
            
        return response
