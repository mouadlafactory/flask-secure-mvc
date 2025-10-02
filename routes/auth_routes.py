"""
Authentication Routes Blueprint
Routes for user authentication: register, login, logout, profile management.
"""
from flask import Blueprint
from controllers.auth_controller import register, login, logout, get_current_user, change_password
from middleware.auth_middleware import auth_required

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

# Public routes (no authentication required)
@auth_bp.route('/register', methods=['POST'])
def register_route():
    """Register a new user"""
    return register()

@auth_bp.route('/login', methods=['POST'])
def login_route():
    """Login user"""
    return login()

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    """Logout user"""
    return logout()

# Protected routes (authentication required)
@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user_route():
    """Get current user information"""
    return get_current_user()

@auth_bp.route('/change-password', methods=['PUT'])
@auth_required
def change_password_route():
    """Change user password"""
    return change_password()
