"""
Task Routes Blueprint
Routes for task management: CRUD operations with role-based access control.
"""
from flask import Blueprint
from controllers.task_controller import (
    create_task, get_tasks, get_task, update_task, delete_task, 
    get_task_stats, get_all_tasks
)
from middleware.auth_middleware import auth_required, admin_required

# Create task blueprint
task_bp = Blueprint('tasks', __name__)

# User task routes (authentication required)
@task_bp.route('', methods=['POST'])
@auth_required
def create_task_route():
    """Create a new task"""
    return create_task()

@task_bp.route('', methods=['GET'])
@auth_required
def get_tasks_route():
    """Get user's tasks with optional filters"""
    return get_tasks()

@task_bp.route('/<task_id>', methods=['GET'])
@auth_required
def get_task_route(task_id):
    """Get a specific task by ID"""
    return get_task(task_id)

@task_bp.route('/<task_id>', methods=['PUT'])
@auth_required
def update_task_route(task_id):
    """Update a specific task"""
    return update_task(task_id)

@task_bp.route('/<task_id>', methods=['DELETE'])
@auth_required
def delete_task_route(task_id):
    """Delete a specific task"""
    return delete_task(task_id)

@task_bp.route('/stats', methods=['GET'])
@auth_required
def get_task_stats_route():
    """Get task statistics for current user"""
    return get_task_stats()

# Admin routes (admin role required)
@task_bp.route('/admin/all', methods=['GET'])
@admin_required
def get_all_tasks_route():
    """Get all tasks (admin only)"""
    return get_all_tasks()
