"""
User Model using MongoEngine
Simple MongoDB document schema for User collection.
"""
from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime
import bcrypt

class User(Document):
    """User document schema for MongoDB using MongoEngine"""
    
    # Schema fields
    username = StringField(required=True, unique=True, min_length=3, max_length=50)
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    name = StringField(required=True, max_length=100)
    role = StringField(default="user", choices=["user", "admin"])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # MongoDB collection settings
    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'username', 
            'role',
            'created_at'
        ]
    }
    
    # Helper methods for password handling
    def set_password(self, password: str):
        """Hash and set user password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))