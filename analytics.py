"""
Server-side Google Analytics 4 tracking using Measurement Protocol
This bypasses ad blockers since tracking happens server-side
"""
import requests
import uuid
import os
from datetime import datetime
from flask import request
import logging

logger = logging.getLogger(__name__)

class ServerSideAnalytics:
    """Server-side Google Analytics 4 implementation"""
    
    def __init__(self, measurement_id, api_secret):
        """
        Initialize analytics tracker
        
        Args:
            measurement_id: Your GA4 Measurement ID (G-XXXXXXXXXX)
            api_secret: Your GA4 API Secret (get from GA4 Admin > Data Streams > Measurement Protocol API secrets)
        """
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.endpoint = "https://www.google-analytics.com/mp/collect"
        self.debug_endpoint = "https://www.google-analytics.com/debug/mp/collect"
        
    def _get_client_id(self):
        """Generate or retrieve client ID for the user"""
        # Try to get from session/cookie, or generate new one
        from flask import session
        if 'ga_client_id' not in session:
            session['ga_client_id'] = str(uuid.uuid4())
        return session['ga_client_id']
    
    def _get_user_data(self):
        """Extract user data from request"""
        return {
            'ip_override': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
        }
    
    def track_pageview(self, page_path, page_title=None, user_id=None, debug=False):
        """
        Track a page view
        
        Args:
            page_path: The path of the page (e.g., '/pricing')
            page_title: Optional page title
            user_id: Optional authenticated user ID
            debug: If True, use debug endpoint to validate
        """
        try:
            client_id = self._get_client_id()
            
            payload = {
                'client_id': client_id,
                'events': [{
                    'name': 'page_view',
                    'params': {
                        'page_location': request.url,
                        'page_path': page_path,
                        'page_title': page_title or page_path,
                        'engagement_time_msec': '100'
                    }
                }]
            }
            
            # Add user ID if authenticated
            if user_id:
                payload['user_id'] = str(user_id)
            
            # Add user properties
            payload['user_properties'] = {
                'user_agent': {'value': request.headers.get('User-Agent', '')[:100]},
            }
            
            endpoint = self.debug_endpoint if debug else self.endpoint
            
            response = requests.post(
                f"{endpoint}?measurement_id={self.measurement_id}&api_secret={self.api_secret}",
                json=payload,
                timeout=2  # Don't wait too long
            )
            
            if debug:
                logger.info(f"GA4 Debug Response: {response.json()}")
            
            return response.status_code == 204 or response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error tracking pageview: {e}")
            return False
    
    def track_event(self, event_name, event_params=None, user_id=None, debug=False):
        """
        Track a custom event
        
        Args:
            event_name: Name of the event (e.g., 'pdf_split', 'file_upload')
            event_params: Dictionary of event parameters
            user_id: Optional authenticated user ID
            debug: If True, use debug endpoint to validate
        """
        try:
            client_id = self._get_client_id()
            
            params = event_params or {}
            params['engagement_time_msec'] = '100'
            
            payload = {
                'client_id': client_id,
                'events': [{
                    'name': event_name,
                    'params': params
                }]
            }
            
            # Add user ID if authenticated
            if user_id:
                payload['user_id'] = str(user_id)
            
            endpoint = self.debug_endpoint if debug else self.endpoint
            
            response = requests.post(
                f"{endpoint}?measurement_id={self.measurement_id}&api_secret={self.api_secret}",
                json=payload,
                timeout=2
            )
            
            if debug:
                logger.info(f"GA4 Debug Response: {response.json()}")
            
            return response.status_code == 204 or response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            return False
    
    def track_conversion(self, conversion_name, value=None, currency='USD', user_id=None):
        """
        Track a conversion event
        
        Args:
            conversion_name: Name of the conversion (e.g., 'purchase', 'sign_up')
            value: Monetary value of the conversion
            currency: Currency code (default: USD)
            user_id: Optional authenticated user ID
        """
        params = {}
        if value is not None:
            params['value'] = value
            params['currency'] = currency
        
        return self.track_event(conversion_name, params, user_id)


# Initialize analytics (will be configured in app.py)
analytics = None

def init_analytics(app):
    """Initialize analytics with app config"""
    global analytics
    
    measurement_id = app.config.get('GA4_MEASUREMENT_ID')
    api_secret = app.config.get('GA4_API_SECRET')
    
    if measurement_id and api_secret:
        analytics = ServerSideAnalytics(measurement_id, api_secret)
        app.logger.info("Server-side analytics initialized")
    else:
        app.logger.warning("GA4_MEASUREMENT_ID or GA4_API_SECRET not set - analytics disabled")
