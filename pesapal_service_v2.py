import os
import time
import hmac
import hashlib
import base64
import secrets
import requests
import logging
import warnings
from urllib.parse import quote, urlencode
from xml.etree import ElementTree as ET

# Suppress SSL warnings for demo server with expired certificate
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

logger = logging.getLogger(__name__)


class PesapalServiceV2:
    """Service class for Pesapal API 2.0 (XML-based) integration"""

    def __init__(self, consumer_key, consumer_secret, is_demo=True, callback_url=None, ipn_url=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_url = callback_url
        self.ipn_url = ipn_url
        
        # API endpoints
        if is_demo:
            self.base_url = "https://demo.pesapal.com"
        else:
            self.base_url = "https://www.pesapal.com"
        
        self.post_order_url = f"{self.base_url}/API/PostPesapalDirectOrderV4"
        self.query_status_url = f"{self.base_url}/API/QueryPaymentStatus"
        self.query_status_by_ref_url = f"{self.base_url}/API/QueryPaymentStatusByMerchantRef"

    def _generate_oauth_params(self, callback_url=None):
        """Generate OAuth 1.0 parameters"""
        return {
            'oauth_consumer_key': self.consumer_key,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': secrets.token_hex(16),
            'oauth_version': '1.0',
            'oauth_callback': callback_url or self.callback_url
        }

    def _create_signature_base_string(self, method, url, params):
        """Create OAuth signature base string"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create parameter string
        param_string = '&'.join([f"{quote(str(k), safe='')}={quote(str(v), safe='')}" 
                                for k, v in sorted_params])
        
        # Create base string
        base_string = f"{method.upper()}&{quote(url, safe='')}&{quote(param_string, safe='')}"
        
        return base_string

    def _generate_signature(self, base_string):
        """Generate HMAC-SHA1 signature"""
        # Signing key is consumer_secret& (note the ampersand)
        signing_key = f"{quote(self.consumer_secret, safe='')}&"
        
        # Generate HMAC-SHA1 hash
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        # Base64 encode
        return base64.b64encode(signature).decode('utf-8')

    def _create_pesapal_xml(self, amount, description, reference, email, 
                           first_name='', last_name='', phone_number='', currency='USD'):
        """Create PesaPal XML request data"""
        xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<PesapalDirectOrderInfo 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    Amount="{amount:.2f}"
    Description="{description}"
    Type="MERCHANT"
    Reference="{reference}"
    FirstName="{first_name}"
    LastName="{last_name}"
    Email="{email}"
    PhoneNumber="{phone_number}"
    Currency="{currency}"
    xmlns="http://www.pesapal.com" />"""
        
        return xml_data

    def create_payment_order(self, user_email, user_name, amount, currency, order_id, description):
        """
        Create a payment order and get redirect URL
        
        Args:
            user_email: Customer email
            user_name: Customer name
            amount: Amount in decimal (e.g., 9.99)
            currency: Currency code (USD, KES, etc.)
            order_id: Unique merchant reference
            description: Order description
            
        Returns:
            dict with redirect_url and order_tracking_id (iframe URL in API 2.0)
        """
        try:
            # Split name
            name_parts = user_name.split()
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[-1] if len(name_parts) > 1 else ''
            
            # Create XML request data
            xml_data = self._create_pesapal_xml(
                amount=amount,
                description=description,
                reference=order_id,
                email=user_email,
                first_name=first_name,
                last_name=last_name,
                currency=currency
            )
            
            # Generate OAuth parameters
            oauth_params = self._generate_oauth_params(self.callback_url)
            
            # Add pesapal_request_data to parameters for signature
            all_params = oauth_params.copy()
            all_params['pesapal_request_data'] = xml_data
            
            # Create signature base string
            base_string = self._create_signature_base_string('GET', self.post_order_url, all_params)
            
            # Generate signature
            signature = self._generate_signature(base_string)
            oauth_params['oauth_signature'] = signature
            
            # Build final URL with all parameters
            oauth_params['pesapal_request_data'] = xml_data
            
            # Make request (disable SSL verification for demo server with expired cert)
            response = requests.get(self.post_order_url, params=oauth_params, timeout=30, verify=False)
            response.raise_for_status()
            
            # The response is an iframe URL
            iframe_url = response.text.strip()
            
            logger.info(f"Payment order created successfully: {order_id}")
            
            return {
                'redirect_url': iframe_url,
                'order_tracking_id': order_id,  # In API 2.0, we use merchant reference
                'iframe_url': iframe_url
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create payment order: {e}")
            raise Exception(f"Failed to create payment order: {str(e)}")

    def get_transaction_status(self, merchant_reference, transaction_tracking_id=None):
        """
        Get transaction status from Pesapal
        
        Args:
            merchant_reference: Your unique order ID
            transaction_tracking_id: Pesapal's tracking ID (optional)
            
        Returns:
            dict with payment status information
        """
        try:
            # Generate OAuth parameters
            oauth_params = self._generate_oauth_params()
            
            # Add query parameters
            query_params = oauth_params.copy()
            query_params['pesapal_merchant_reference'] = merchant_reference
            
            if transaction_tracking_id:
                query_params['pesapal_transaction_tracking_id'] = transaction_tracking_id
            
            # Create signature base string
            base_string = self._create_signature_base_string('GET', self.query_status_url, query_params)
            
            # Generate signature
            signature = self._generate_signature(base_string)
            query_params['oauth_signature'] = signature
            
            # Make request (disable SSL verification for demo server)
            response = requests.get(self.query_status_url, params=query_params, timeout=30, verify=False)
            response.raise_for_status()
            
            # Parse response (format: pesapal_response_data=<response>)
            response_text = response.text.strip()
            
            # Extract status from response
            # Response format: "pesapal_response_data=PENDING" or "pesapal_response_data=COMPLETED" etc.
            if '=' in response_text:
                status = response_text.split('=')[1].strip()
            else:
                status = response_text
            
            logger.info(f"Transaction status for {merchant_reference}: {status}")
            
            # Map API 2.0 status to API 3.0 format for compatibility
            status_mapping = {
                'COMPLETED': {'payment_status_description': 'completed', 'status_code': 1},
                'FAILED': {'payment_status_description': 'failed', 'status_code': 2},
                'INVALID': {'payment_status_description': 'invalid', 'status_code': 3},
                'PENDING': {'payment_status_description': 'pending', 'status_code': 0},
            }
            
            result = status_mapping.get(status.upper(), {
                'payment_status_description': status.lower(),
                'status_code': 0
            })
            
            result['merchant_reference'] = merchant_reference
            result['raw_status'] = status
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get transaction status: {e}")
            raise Exception(f"Failed to get transaction status: {str(e)}")

    def query_payment_details(self, merchant_reference, transaction_tracking_id):
        """
        Query payment details using both merchant reference and tracking ID
        This is more reliable than using just one
        """
        return self.get_transaction_status(merchant_reference, transaction_tracking_id)


def create_pesapal_service(app):
    """Factory function to create PesapalServiceV2 from Flask app config"""
    is_demo = 'demo' in app.config.get('PESAPAL_BASE_URL', '').lower() or \
              'cybqa' in app.config.get('PESAPAL_BASE_URL', '').lower()
    
    return PesapalServiceV2(
        consumer_key=app.config['PESAPAL_CONSUMER_KEY'],
        consumer_secret=app.config['PESAPAL_CONSUMER_SECRET'],
        is_demo=is_demo,
        callback_url=app.config['PESAPAL_CALLBACK_URL'],
        ipn_url=app.config.get('PESAPAL_IPN_URL')
    )
