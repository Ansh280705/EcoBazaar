from functools import wraps
from flask import request, redirect, url_for, flash
from flask_login import current_user
from main import login_manager
from main.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('sign_in'))
        
        # Enforce role selection for new users
        if current_user.role is None and request.endpoint not in ['role_selection', 'logout', 'static']:
            return redirect(url_for('role_selection'))
            
        return f(*args, **kwargs)
    return decorated_function

def require_role(roles):
    """
    Decorator to restrict access based on user role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('sign_in'))
                
            if current_user.role not in roles:
                flash("Unauthorized access.", "error")
                if current_user.role == "admin":
                    return redirect(url_for('admin_dashboard'))
                elif current_user.role == "seller":
                    return redirect(url_for('seller_dashboard'))
                elif current_user.role == "buyer":
                    return redirect(url_for('buyer_dashboard'))
                else:
                    return redirect(url_for('role_selection'))

            # Check seller approval status
            if current_user.role == 'seller' and 'seller' in roles:
                if current_user.seller_status != 'approved' and request.endpoint not in ['seller_dashboard', 'about']:
                    flash("Your seller account is pending admin approval.", "error")
                    return redirect(url_for('seller_dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
