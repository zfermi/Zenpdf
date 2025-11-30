"""
Payment handling routes for Pesapal integration
API 3.0
"""
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models import db, User
from pesapal_service import create_pesapal_service

payment_bp = Blueprint('payment', __name__)
logger = logging.getLogger(__name__)


@payment_bp.route('/subscribe/premium', methods=['GET'])
@login_required
def subscribe_premium():
    """Initiate premium subscription payment"""
    try:
        # Check if user is already premium
        if current_user.is_premium:
            flash('You already have an active premium subscription.', 'info')
            return redirect(url_for('dashboard'))

        # Create Pesapal service
        pesapal = create_pesapal_service(current_app)

        # Generate unique order ID
        order_id = f"BESTPDF-{current_user.id}-{secrets.token_hex(8)}"

        # Create payment order
        amount = current_app.config['PREMIUM_PRICE'] / 100  # Convert cents to dollars
        currency = 'USD'
        description = f'Best Pdf Converter Premium Subscription - Monthly ({current_user.email})'

        result = pesapal.create_payment_order(
            user_email=current_user.email,
            user_name=current_user.username,
            amount=amount,
            currency=currency,
            order_id=order_id,
            description=description
        )

        # API 3.0 response format
        redirect_url = result.get('redirect_url')
        order_tracking_id = result.get('order_tracking_id')

        # Check for errors in response
        if result.get('error'):
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            flash(f'Failed to initiate payment: {error_msg}', 'error')
            logger.error(f"Pesapal API error: {result.get('error')}")
            return redirect(url_for('pricing'))

        if not redirect_url:
            flash('Failed to initiate payment. Please try again.', 'error')
            logger.error(f"No redirect URL in Pesapal response: {result}")
            return redirect(url_for('pricing'))

        # Store order tracking ID in session or database for verification
        # You might want to create a Payment model to track this
        logger.info(f"Payment initiated for user {current_user.id}, order: {order_id}, tracking: {order_tracking_id}")

        # Redirect to Pesapal payment page
        return redirect(redirect_url)

    except Exception as e:
        logger.error(f"Payment initiation failed: {e}")
        flash('An error occurred while processing your payment. Please try again.', 'error')
        return redirect(url_for('pricing'))


@payment_bp.route('/callback', methods=['GET'])
def payment_callback():
    """Handle payment callback from Pesapal"""
    try:
        # API 2.0 uses different parameter names
        # Try API 2.0 parameters first, then fall back to API 3.0
        order_tracking_id = request.args.get('pesapal_transaction_tracking_id') or request.args.get('OrderTrackingId')
        order_merchant_reference = request.args.get('pesapal_merchant_reference') or request.args.get('OrderMerchantReference')

        if not order_merchant_reference:
            flash('Invalid payment callback.', 'error')
            return redirect(url_for('dashboard'))

        # Identify user from merchant reference (BESTPDF-{user_id}-token)
        user = None
        if order_merchant_reference:
            try:
                user_id = int(order_merchant_reference.split('-')[1])
                user = User.query.get(user_id)
            except (IndexError, ValueError):
                logger.error(f"Failed to parse merchant reference: {order_merchant_reference}")

        # Create Pesapal service
        pesapal = create_pesapal_service(current_app)

        # Get transaction status using order tracking ID (API 3.0)
        status_data = pesapal.get_transaction_status(order_tracking_id)

        payment_status = status_data.get('payment_status_description', '').lower()
        status_code = status_data.get('status_code')
        merchant_reference = status_data.get('merchant_reference') or order_merchant_reference

        logger.info(
            f"Payment callback - MerchantRef: {merchant_reference}, Status: {payment_status}, Code: {status_code}"
        )

        # Check if payment was successful
        if payment_status == 'completed' and status_code == 1:
            if not user:
                flash('Payment completed, but we could not match your account. Please contact support.', 'error')
                return redirect(url_for('pricing'))

            if not user.is_premium:
                user.subscription_tier = 'premium'
                user.subscription_start = datetime.utcnow()
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
                db.session.commit()
                logger.info(f"Premium subscription activated for user {user.id} via callback")

            flash('Payment successful! Your premium subscription is now active.', 'success')
            return redirect(url_for('dashboard'))

        elif payment_status == 'failed' and status_code == 2:
            flash('Payment failed. Please try again or contact support.', 'error')
            return redirect(url_for('pricing'))

        elif payment_status == 'invalid' and status_code == 3:
            flash('Invalid payment. Please contact support.', 'error')
            return redirect(url_for('pricing'))

        else:
            # Pending or other status
            flash('Payment is being processed. We will notify you once confirmed.', 'info')
            return redirect(url_for('dashboard'))

    except Exception as e:
        logger.error(f"Payment callback error: {e}")
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('dashboard'))



@payment_bp.route('/ipn', methods=['GET', 'POST'])
def payment_ipn():
    """Handle IPN (Instant Payment Notification) from Pesapal API 3.0"""
    try:
        # API 3.0 parameters
        order_tracking_id = request.args.get('OrderTrackingId')
        order_notification_type = request.args.get('OrderNotificationType')
        order_merchant_reference = request.args.get('OrderMerchantReference')

        logger.info(f"IPN received - Tracking: {order_tracking_id}, Type: {order_notification_type}, Ref: {order_merchant_reference}")

        if not order_tracking_id:
            return jsonify({'status': 'error', 'message': 'Missing order tracking ID'}), 400

        # Create Pesapal service
        pesapal = create_pesapal_service(current_app)

        # Get transaction status using tracking ID (API 3.0)
        status_data = pesapal.get_transaction_status(order_tracking_id)

        payment_status = status_data.get('payment_status_description', '').lower()
        status_code = status_data.get('status_code')
        merchant_reference = status_data.get('merchant_reference') or order_merchant_reference

        # Extract user ID from merchant reference (format: BESTPDF-{user_id}-{token})
        try:
            user_id = int(merchant_reference.split('-')[1])
            user = User.query.get(user_id)

            if not user:
                logger.error(f"User not found for merchant reference: {merchant_reference}")
                return jsonify({'status': 'error', 'message': 'User not found'}), 404

            # Update subscription based on payment status
            if payment_status == 'completed' and status_code == 1:
                if not user.is_premium:
                    user.subscription_tier = 'premium'
                    user.subscription_start = datetime.utcnow()
                    user.subscription_end = datetime.utcnow() + timedelta(days=30)
                    db.session.commit()
                    logger.info(f"Premium subscription activated via IPN for user {user_id}")

        except (IndexError, ValueError) as e:
            logger.error(f"Failed to parse merchant reference: {merchant_reference}, error: {e}")

        # Respond to Pesapal IPN
        return jsonify({
            'status': 'success',
            'message': 'IPN processed'
        }), 200

    except Exception as e:
        logger.error(f"IPN processing error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@payment_bp.route('/status/<order_tracking_id>', methods=['GET'])
@login_required
def check_payment_status(order_tracking_id):
    """Check payment status manually"""
    try:
        # Create Pesapal service
        pesapal = create_pesapal_service(current_app)

        # Get transaction status
        status_data = pesapal.get_transaction_status(order_tracking_id)

        return jsonify(status_data), 200

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500
