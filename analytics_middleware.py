"""
Flask middleware for automatic page view tracking
"""
from flask import request, g
from functools import wraps
import time

def track_pageview(analytics_instance):
    """
    Decorator to automatically track page views
    
    Usage:
        @app.route('/pricing')
        @track_pageview(analytics)
        def pricing():
            return render_template('pricing.html')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the route function
            response = f(*args, **kwargs)
            
            # Track pageview after successful response
            if analytics_instance and 200 <= getattr(response, 'status_code', 200) < 400:
                try:
                    from flask_login import current_user
                    user_id = current_user.id if current_user.is_authenticated else None
                    
                    # Get page title from route function name
                    page_title = f.__name__.replace('_', ' ').title()
                    
                    # Track in background (non-blocking)
                    import threading
                    thread = threading.Thread(
                        target=analytics_instance.track_pageview,
                        args=(request.path, page_title, user_id)
                    )
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    # Don't let analytics errors break the app
                    pass
            
            return response
        return decorated_function
    return decorator


def setup_analytics_middleware(app, analytics_instance):
    """
    Setup automatic analytics tracking for all requests
    
    Args:
        app: Flask app instance
        analytics_instance: ServerSideAnalytics instance
    """
    
    @app.before_request
    def before_request():
        """Track request start time"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Track page views automatically"""
        if not analytics_instance:
            return response
        
        # Only track successful GET requests to HTML pages
        if (request.method == 'GET' and 
            200 <= response.status_code < 400 and
            not request.path.startswith('/static/') and
            not request.path.startswith('/download/') and
            not request.path.endswith(('.js', '.css', '.png', '.jpg', '.ico', '.xml', '.txt'))):
            
            try:
                from flask_login import current_user
                user_id = current_user.id if current_user.is_authenticated else None
                
                # Get page title from endpoint
                page_title = request.endpoint.replace('_', ' ').title() if request.endpoint else request.path
                
                # Track in background thread (non-blocking)
                import threading
                thread = threading.Thread(
                    target=analytics_instance.track_pageview,
                    args=(request.path, page_title, user_id)
                )
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                app.logger.error(f"Analytics tracking error: {e}")
        
        return response
