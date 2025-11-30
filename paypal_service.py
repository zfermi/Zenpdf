"""
PayPal Payment Integration Service
Uses PayPal REST API v2 for payment processing
"""
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PayPalService:
    """Service class for PayPal payment integration"""

    def __init__(self, client_id, client_secret, base_url):
        """
        Initialize PayPal service

        Args:
            client_id: PayPal Client ID
            client_secret: PayPal Secret
            base_url: PayPal API base URL (sandbox or live)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self):
        """Get OAuth 2.0 access token from PayPal"""
        # Check if we have a valid token
        if self.access_token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            return self.access_token

        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data.get('access_token')
            # Token expires in ~9 hours, refresh 1 hour before
            expires_in = token_data.get('expires_in', 32400)  # Default 9 hours
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 3600)

            logger.info("Successfully obtained PayPal access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise Exception(f"Failed to authenticate with PayPal: {str(e)}")

    def create_order(self, amount, currency, order_id, description, return_url, cancel_url):
        """
        Create a PayPal order for payment

        Args:
            amount: Amount in decimal (e.g., 9.99)
            currency: Currency code (USD, EUR, etc.)
            order_id: Your unique reference ID
            description: Order description
            return_url: URL to return after successful payment
            cancel_url: URL to return if payment is cancelled

        Returns:
            dict with order details including approve_url
        """
        token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        # PayPal requires amount as string with 2 decimal places
        amount_str = f"{float(amount):.2f}"

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": order_id,
                "description": description,
                "amount": {
                    "currency_code": currency,
                    "value": amount_str
                }
            }],
            "application_context": {
                "brand_name": "Best Pdf Converter",
                "landing_page": "NO_PREFERENCE",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            order_data = response.json()

            # Extract approval URL
            approve_url = None
            for link in order_data.get('links', []):
                if link.get('rel') == 'approve':
                    approve_url = link.get('href')
                    break

            logger.info(f"Successfully created PayPal order: {order_data.get('id')}")

            return {
                'order_id': order_data.get('id'),
                'status': order_data.get('status'),
                'approve_url': approve_url,
                'order_data': order_data
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create PayPal order: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"PayPal error response: {e.response.text}")
            raise Exception(f"Failed to create PayPal order: {str(e)}")

    def capture_order(self, order_id):
        """
        Capture payment for an approved order

        Args:
            order_id: PayPal order ID

        Returns:
            dict with capture details
        """
        token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            capture_data = response.json()

            logger.info(f"Successfully captured PayPal order: {order_id}")
            return capture_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to capture PayPal order: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"PayPal error response: {e.response.text}")
            raise Exception(f"Failed to capture PayPal order: {str(e)}")

    def get_order_details(self, order_id):
        """
        Get order details from PayPal

        Args:
            order_id: PayPal order ID

        Returns:
            dict with order details
        """
        token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{order_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal order details: {e}")
            raise Exception(f"Failed to get PayPal order details: {str(e)}")


def create_paypal_service(app):
    """Factory function to create PayPalService from Flask app config"""
    return PayPalService(
        client_id=app.config['PAYPAL_CLIENT_ID'],
        client_secret=app.config['PAYPAL_CLIENT_SECRET'],
        base_url=app.config['PAYPAL_BASE_URL']
    )
