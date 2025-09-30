"""
Task Controller Functions
Simple functions for handling task CRUD operations.
"""
from flask import request, jsonify
from datetime import datetime
from bson import ObjectId
from models import Task, User

def create_task():
    """Create a new task"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('description'):
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Validate field lengths
        if len(data['title']) > 200:
            return jsonify({'error': 'Title must be less than 200 characters'}), 400
        
        if len(data['description']) > 1000:
            return jsonify({'error': 'Description must be less than 1000 characters'}), 400
        
        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO format'}), 400
        
        # Create new task
        task = Task(
            title=data['title'].strip(),
            description=data['description'].strip(),
            user=user,
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            due_date=due_date
        )
        task.save()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': {
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat() if task.created_at else None
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Task creation failed', 'details': str(e)}), 500

def get_tasks():
    """Get user's tasks with optional filters"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Build query
        query = Task.objects(user=user)
        
        if status:
            query = query.filter(status=status)
        
        if priority:
            query = query.filter(priority=priority)
        
        # Get tasks with pagination
        tasks = query.order_by('-created_at').skip(skip).limit(limit)
        total = query.count()
        
        # Format response
        task_list = []
        for task in tasks:
            task_list.append({
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            })
        
        return jsonify({
            'tasks': task_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get tasks', 'details': str(e)}), 500

def get_task(task_id):
    """Get a specific task by ID"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Find task
        task = Task.objects(id=task_id, user=user).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'task': {
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get task', 'details': str(e)}), 500

def update_task(task_id):
    """Update a specific task"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Find task
        task = Task.objects(id=task_id, user=user).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            if not data['title'] or len(data['title']) > 200:
                return jsonify({'error': 'Title is required and must be less than 200 characters'}), 400
            task.title = data['title'].strip()
        
        if 'description' in data:
            if not data['description'] or len(data['description']) > 1000:
                return jsonify({'error': 'Description is required and must be less than 1000 characters'}), 400
            task.description = data['description'].strip()
        
        if 'status' in data:
            if data['status'] in ['pending', 'in_progress', 'completed', 'cancelled']:
                task.status = data['status']
                if data['status'] == 'completed' and not task.completed_at:
                    task.completed_at = datetime.utcnow()
            else:
                return jsonify({'error': 'Invalid status'}), 400
        
        if 'priority' in data:
            if data['priority'] in ['low', 'medium', 'high', 'urgent']:
                task.priority = data['priority']
            else:
                return jsonify({'error': 'Invalid priority'}), 400
        
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid due_date format'}), 400
            else:
                task.due_date = None
        
        task.updated_at = datetime.utcnow()
        task.save()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': {
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Task update failed', 'details': str(e)}), 500

def delete_task(task_id):
    """Delete a specific task"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Find and delete task
        task = Task.objects(id=task_id, user=user).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task.delete()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Task deletion failed', 'details': str(e)}), 500

def get_task_stats():
    """Get task statistics for current user"""
    try:
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get task counts by status
        total = Task.objects(user=user).count()
        pending = Task.objects(user=user, status='pending').count()
        in_progress = Task.objects(user=user, status='in_progress').count()
        completed = Task.objects(user=user, status='completed').count()
        cancelled = Task.objects(user=user, status='cancelled').count()
        
        # Get overdue tasks
        overdue = Task.objects(
            user=user,
            due_date__lt=datetime.utcnow(),
            status__nin=['completed', 'cancelled']
        ).count()
        
        return jsonify({
            'stats': {
                'total': total,
                'pending': pending,
                'in_progress': in_progress,
                'completed': completed,
                'cancelled': cancelled,
                'overdue': overdue
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get task stats', 'details': str(e)}), 500

# Admin functions
def get_all_tasks():
    """Get all tasks (admin only)"""
    try:
        user = getattr(request, 'current_user', None)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Get all tasks with pagination
        tasks = Task.objects().order_by('-created_at').skip(skip).limit(limit)
        total = Task.objects().count()
        
        # Format response
        task_list = []
        for task in tasks:
            task_list.append({
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'user': {
                    'id': str(task.user.id),
                    'username': task.user.username,
                    'email': task.user.email
                } if task.user else None,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat() if task.created_at else None
            })
        
        return jsonify({
            'tasks': task_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get all tasks', 'details': str(e)}), 500
