from django.core.exceptions import PermissionDenied
from social_core.exceptions import AuthForbidden

def verify_marian_college_domain(backend, details, response, user=None, *args, **kwargs):
    if backend.name == 'google-oauth2':
        email = details.get('email', '')
        if not email or not email.endswith('@mariancollege.org'):
            raise AuthForbidden(backend, 'Only @mariancollege.org email addresses are allowed to sign in.')
        
        # Block login if user has been deactivated/blocked by admin
        if user and not user.is_active:
            raise AuthForbidden(backend, 'Your account has been temporarily blocked by the administrator.')
