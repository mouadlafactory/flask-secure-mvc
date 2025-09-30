"""
Authentication Controller Functions
Simple functions for handling user registration, login, logout, and authentication.
"""
from flask import request, jsonify, make_response
from datetime import datetime, timedelta
import jwt
from models import User
from config import Config

def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.objects(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.objects(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create new user
        user = User(
            username=data['username'].strip(),
            email=data['email'].lower().strip(),
            name=data['name'].strip(),
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        user.save()
        
        # Generate JWT token
        token = generate_token(user)
        
        # Create response
        response = make_response(jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'role': user.role
            },
            'token': token
        }), 201)
        
        # Set JWT token in HTTP-only cookie
        response.set_cookie(
            'auth_token',
            token,
            max_age=Config.JWT_ACCESS_TOKEN_EXPIRES,
            httponly=Config.JWT_COOKIE_HTTPONLY,
            secure=Config.JWT_COOKIE_SECURE,
            samesite=Config.JWT_COOKIE_SAMESITE
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

def login():
    """Login user with email/username and password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('login') or not data.get('password'):
            return jsonify({'error': 'Login and password are required'}), 400
        
        # Find user by email or username
        login_field = data['login'].strip()
        user = User.objects(email=login_field.lower()).first()
        if not user:
            user = User.objects(username=login_field).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Generate JWT token
        token = generate_token(user)
        
        # Create response
        response = make_response(jsonify({
            'message': 'Login successful',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'role': user.role
            },
            'token': token
        }), 200)
        
        # Set JWT token in HTTP-only cookie
        response.set_cookie(
            'auth_token',
            token,
            max_age=Config.JWT_ACCESS_TOKEN_EXPIRES,
            httponly=Config.JWT_COOKIE_HTTPONLY,
            secure=Config.JWT_COOKIE_SECURE,
            samesite=Config.JWT_COOKIE_SAMESITE
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

def logout():
    """Logout user by clearing the auth token cookie"""
    try:
        response = make_response(jsonify({'message': 'Logout successful'}), 200)
        
        # Clear the auth token cookie
        response.set_cookie(
            'auth_token',
            '',
            max_age=0,
            httponly=Config.JWT_COOKIE_HTTPONLY,
            secure=Config.JWT_COOKIE_SECURE,
            samesite=Config.JWT_COOKIE_SAMESITE
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

def get_current_user():
    """Get current authenticated user info"""
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'current_user', None)
        
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        return jsonify({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500

def change_password():
    """Change user password"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        # Update password
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        user.save()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Password change failed', 'details': str(e)}), 500

def generate_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user.id),
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        user = User.objects(id=payload['user_id']).first()
        
        if not user or not user.is_active:
            return None
            
        return user
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None