"""
Middleware for debugging session and authentication issues.
"""
import logging

logger = logging.getLogger(__name__)


class AuthDebugMiddleware:
    """Logs authentication and session information for debugging."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log before view
        if request.path.startswith(('/unit/create/', '/session/create/', '/dashboard/')):
            print(f'[AUTH DEBUG] Path: {request.path}')
            print(f'[AUTH DEBUG] User authenticated: {request.user.is_authenticated}')
            print(f'[AUTH DEBUG] Username: {request.user.username if request.user.is_authenticated else "None"}')
            print(f'[AUTH DEBUG] Session key: {request.session.session_key}')
            print(f'[AUTH DEBUG] Session data keys: {list(request.session.keys())}')
            print(f'[AUTH DEBUG] Method: {request.method}')
            print(f'[AUTH DEBUG] Has CSRF token: {"csrftoken" in request.POST or "csrfmiddlewaretoken" in request.POST}')
            logger.info(f'AUTH DEBUG: {request.path} | auth={request.user.is_authenticated} | user={request.user.username}')
        
        response = self.get_response(request)
        
        # Log after view
        if request.path.startswith(('/unit/create/', '/session/create/', '/dashboard/')):
            print(f'[AUTH DEBUG RESPONSE] Status: {response.status_code}')
            if 'Location' in response:
                print(f'[AUTH DEBUG RESPONSE] Redirect to: {response["Location"]}')
        
        return response
