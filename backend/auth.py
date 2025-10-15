"""
Authentication and Authorization Module
Handles user authentication, JWT tokens, and role-based access control
"""

import bcrypt
from datetime import datetime
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

# User roles and their permissions
ROLES = {
    'admin': {
        'name': 'Administrator',
        'permissions': ['view', 'export', 'configure', 'manage_users', 'manage_zones', 'send_alerts']
    },
    'operator': {
        'name': 'Operator',
        'permissions': ['view', 'export', 'send_alerts']
    },
    'viewer': {
        'name': 'Viewer',
        'permissions': ['view']
    }
}

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_user_permissions(role):
    """Get permissions for a role"""
    return ROLES.get(role, {}).get('permissions', [])

def has_permission(role, permission):
    """Check if a role has a specific permission"""
    return permission in get_user_permissions(role)

# Decorator for requiring authentication
def jwt_required_custom(fn):
    """Custom JWT required decorator with better error handling"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'Authentication required',
                'message': str(e)
            }), 401
    return wrapper

# Decorator for requiring specific permissions
def permission_required(*permissions):
    """Decorator to require specific permissions"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role', 'viewer')
                
                # Check if user has all required permissions
                user_permissions = get_user_permissions(user_role)
                for perm in permissions:
                    if perm not in user_permissions:
                        return jsonify({
                            'error': 'Permission denied',
                            'message': f'This action requires {perm} permission',
                            'required_permissions': list(permissions),
                            'user_permissions': user_permissions
                        }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authentication required',
                    'message': str(e)
                }), 401
        return wrapper
    return decorator

# Decorator for role-based access
def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role', 'viewer')
                
                if user_role not in allowed_roles:
                    return jsonify({
                        'error': 'Access denied',
                        'message': f'This action requires one of these roles: {", ".join(allowed_roles)}',
                        'user_role': user_role
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authentication required',
                    'message': str(e)
                }), 401
        return wrapper
    return decorator

def get_current_user():
    """Get current user identity from JWT"""
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        claims = get_jwt()
        return {
            'username': identity,
            'role': claims.get('role', 'viewer'),
            'permissions': get_user_permissions(claims.get('role', 'viewer'))
        }
    except:
        return None

def log_activity(db_manager, username, action, details=None):
    """Log user activity"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity_logs (username, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (username, action, details, datetime.now().isoformat()))
            conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

def init_default_users(db_manager):
    """Initialize default users if none exist"""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        ''')
        
        if not cursor.fetchone():
            # Create users table
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Create activity logs table
            cursor.execute('''
                CREATE TABLE activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            print("✅ Created users and activity_logs tables")
        
        # Check if any users exist
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # Create default users
            default_users = [
                {
                    'username': 'admin',
                    'password': 'admin123',  # Change in production!
                    'email': 'admin@surveillance.local',
                    'role': 'admin'
                },
                {
                    'username': 'operator',
                    'password': 'operator123',  # Change in production!
                    'email': 'operator@surveillance.local',
                    'role': 'operator'
                },
                {
                    'username': 'viewer',
                    'password': 'viewer123',  # Change in production!
                    'email': 'viewer@surveillance.local',
                    'role': 'viewer'
                }
            ]
            
            for user in default_users:
                password_hash = hash_password(user['password'])
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, role, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (
                    user['username'],
                    password_hash,
                    user['email'],
                    user['role'],
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            print("✅ Created default users:")
            print("   - admin/admin123 (Administrator)")
            print("   - operator/operator123 (Operator)")
            print("   - viewer/viewer123 (Viewer)")
            print("   ⚠️  CHANGE THESE PASSWORDS IN PRODUCTION!")
        
        return True
