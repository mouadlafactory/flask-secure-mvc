"""
Flask Application Entry Point
Main application setup with blueprints, database connection, and configuration.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect
import os
from config import config
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['*']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Connect to MongoDB
    try:
        connect(
            db=app.config['MONGO_DB_NAME'],
            host=app.config['MONGO_URI']
        )
        print(f"✓ Connected to MongoDB: {app.config['MONGO_DB_NAME']}")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    
    # Health check route
    @app.route('/')
    def health_check():
        return jsonify({
            "message": "Flask Task API is running!",
            "status": "healthy",
            "version": "1.0.0"
        })
    
    @app.route('/api')
    def api_info():
        return jsonify({
            "message": "Task Management API",
            "version": "1.0.0",
            "endpoints": {
                "auth": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login", 
                    "logout": "POST /api/auth/logout",
                    "profile": "GET /api/auth/me",
                    "change_password": "PUT /api/auth/change-password"
                },
                "tasks": {
                    "create": "POST /api/tasks",
                    "list": "GET /api/tasks",
                    "get": "GET /api/tasks/<id>",
                    "update": "PUT /api/tasks/<id>",
                    "delete": "DELETE /api/tasks/<id>",
                    "stats": "GET /api/tasks/stats",
                    "admin_all": "GET /api/tasks/admin/all"
                }
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    # Get configuration
    debug_mode = app.config.get('DEBUG', True)
    port = int(os.environ.get('PORT', 6000))
    
    print("🚀 Starting Flask Task Management API...")
    print(f"📍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📚 API docs: http://localhost:{port}/api")
    
    app.run(
        debug=debug_mode,
        port=port,
        host='0.0.0.0'
    )