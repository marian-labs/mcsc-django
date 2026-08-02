import re
from django.core.exceptions import PermissionDenied
from social_core.exceptions import AuthForbidden

def verify_marian_college_domain(backend, details, response, user=None, *args, **kwargs):
    if backend.name == 'google-oauth2':
        email = details.get('email', '')
        if not email or not email.endswith('@mariancollege.org'):
            raise AuthForbidden(backend, 'Only @mariancollege.org email addresses are allowed to sign in.')
        
        # Block login if user has been deactivated/blocked by admin
        if user and not user.is_active:
            raise AuthForbidden(backend, 'Your account has been temporarily deactivated by the MCSC Administrator.')


def set_clean_user_name(backend, details, response, user=None, *args, **kwargs):
    """
    Extracts the user's exact clean name from Google OAuth profile/email
    (stripping college reg codes like 24UBC145) and sets first_name.
    """
    if user:
        raw_name = details.get('fullname') or f"{details.get('first_name', '')} {details.get('last_name', '')}".strip()
        if not raw_name and details.get('email'):
            raw_name = details.get('email').split('@')[0]
        
        # Remove trailing reg number patterns (e.g. "Muhammed Sinan M 24UBC145" -> "Muhammed Sinan M")
        clean_name = re.sub(r'\s+\d{2}[A-Z]{2,4}\d+\s*$', '', raw_name).strip()
        
        if clean_name and user.first_name != clean_name:
            user.first_name = clean_name
            user.save(update_fields=['first_name'])
