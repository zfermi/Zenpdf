"""
Pesapal Payment Gateway Integration
Version 3.0 API
"""
import os
import requests
import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class PesapalService:
    """Service class for Pesapal payment integration"""

    def __init__(self, consumer_key, consumer_secret, base_url, ipn_url, callback_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = base_url
        self.ipn_url = ipn_url
        self.callback_url = callback_url
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self):
        """Get OAuth access token from Pesapal"""
        # Check if we have a valid token
        if self.access_token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            return self.access_token

        url = f"{self.base_url}/api/Auth/RequestToken"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            self.access_token = data.get('token')
            # Token expires in 5 minutes, refresh 1 minute before
            self.token_expiry = datetime.utcnow() + timedelta(seconds=240)

            logger.info("Successfully obtained Pesapal access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Pesapal access token: {e}")
            raise Exception(f"Failed to authenticate with Pesapal: {str(e)}")

    def register_ipn(self):
        """Register IPN URL with Pesapal"""
        token = self.get_access_token()
        url = f"{self.base_url}/api/URLSetup/RegisterIPN"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        payload = {
            'url': self.ipn_url,
            'ipn_notification_type': 'GET'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            ipn_id = data.get('ipn_id')
            logger.info(f"Successfully registered IPN with ID: {ipn_id}")
            return ipn_id

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register IPN: {e}")
            raise Exception(f"Failed to register IPN: {str(e)}")

    def get_ipn_list(self):
        """Get list of registered IPNs"""
        token = self.get_access_token()
        url = f"{self.base_url}/api/URLSetup/GetIpnList"
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get IPN list: {e}")
            return []

    def submit_order(self, order_data):
        """
        Submit order to Pesapal

        order_data should contain:
        - id: Merchant reference (unique order ID)
        - currency: Currency code (e.g., 'USD', 'KES')
        - amount: Amount in decimal format
        - description: Order description
        - callback_url: URL to redirect after payment
        - notification_id: IPN ID from registration
        - billing_address: Dict with customer details
        """
        token = self.get_access_token()
        url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.post(url, json=order_data, headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Successfully submitted order: {order_data.get('id')}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit order: {e}")
            raise Exception(f"Failed to submit order to Pesapal: {str(e)}")

    def get_transaction_status(self, order_tracking_id):
        """Get transaction status from Pesapal"""
        token = self.get_access_token()
        url = f"{self.base_url}/api/Transactions/GetTransactionStatus"
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        params = {
            'orderTrackingId': order_tracking_id
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Retrieved transaction status for: {order_tracking_id}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get transaction status: {e}")
            raise Exception(f"Failed to get transaction status: {str(e)}")

    def create_payment_order(self, user_email, user_name, amount, currency, order_id, description):
        """
        Create a payment order for premium subscription

        Returns the redirect URL for payment
        """
        # Get or register IPN
        ipn_list = self.get_ipn_list()
        if ipn_list and len(ipn_list) > 0:
            notification_id = ipn_list[0].get('ipn_id')
        else:
            notification_id = self.register_ipn()

        order_data = {
            'id': order_id,
            'currency': currency,
            'amount': amount,
            'description': description,
            'callback_url': self.callback_url,
            'notification_id': notification_id,
            'billing_address': {
                'email_address': user_email,
                'phone_number': '',
                'country_code': '',
                'first_name': user_name.split()[0] if user_name else '',
                'middle_name': '',
                'last_name': user_name.split()[-1] if len(user_name.split()) > 1 else '',
                'line_1': '',
                'line_2': '',
                'city': '',
                'state': '',
                'postal_code': '',
                'zip_code': ''
            }
        }

        result = self.submit_order(order_data)
        return result


def create_pesapal_service(app):
    """Factory function to create PesapalService from Flask app config"""
    return PesapalService(
        consumer_key=app.config['PESAPAL_CONSUMER_KEY'],
        consumer_secret=app.config['PESAPAL_CONSUMER_SECRET'],
        base_url=app.config['PESAPAL_BASE_URL'],
        ipn_url=app.config['PESAPAL_IPN_URL'],
        callback_url=app.config['PESAPAL_CALLBACK_URL']
    )
