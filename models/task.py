"""
Task Model using MongoEngine
Simple MongoDB document schema for Task collection.
"""
from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime
from .user import User

class Task(Document):
    """Task document schema for MongoDB using MongoEngine"""
    
    # Schema fields
    title = StringField(required=True, max_length=200)
    description = StringField(required=True, max_length=1000)
    user = ReferenceField(User, required=True)
    status = StringField(
        default="pending", 
        choices=["pending", "in_progress", "completed", "cancelled"]
    )
    priority = StringField(
        default="medium",
        choices=["low", "medium", "high", "urgent"]
    )
    due_date = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    
    # MongoDB collection settings
    meta = {
        'collection': 'tasks',
        'indexes': [
            'user',
            'status',
            'priority',
            'due_date',
            'created_at',
            ('user', 'status'),
            ('user', 'created_at'),
            ('user', 'priority')
        ]
    }