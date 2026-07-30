class SecurityHeadersMiddleware:
    """
    Middleware to inject security headers including Content-Security-Policy (CSP),
    COOP, Referrer-Policy, and X-Content-Type-Options into all HTTP responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy (CSP) header allowing Google OAuth, Google Fonts, Supabase, and internal assets
        csp_policies = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://apis.google.com https://accounts.google.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
            "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net",
            "img-src 'self' data: blob: https:",
            "connect-src 'self' https://*.supabase.co https://accounts.google.com https://cdn.jsdelivr.net",
            "frame-src 'self' https://accounts.google.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self' https://accounts.google.com",
        ]
        
        # Set security headers if not already set by upstream
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = "; ".join(csp_policies)
            
        if 'Referrer-Policy' not in response:
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
            
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'SAMEORIGIN'
            
        if 'Cross-Origin-Opener-Policy' not in response:
            # Allows Google OAuth popup authentication windows while protecting cross-origin context
            response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
            
        if 'Permissions-Policy' not in response:
            response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
            
        return response
