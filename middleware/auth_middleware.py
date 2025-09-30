"""
Authentication Middleware
JWT token verification middleware for protected routes.
"""
from functools import wraps
from flask import request, jsonify
from controllers.auth_controller import verify_token

def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from cookie
        token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'error': 'Authentication token required'}), 401
        
        # Verify token and get user
        user = verify_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from cookie
        token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'error': 'Authentication token required'}), 401
        
        # Verify token and get user
        user = verify_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if user is admin
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication (user info if available)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from cookie
        token = request.cookies.get('auth_token')
        
        if token:
            # Verify token and get user if valid
            user = verify_token(token)
            if user:
                request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function
