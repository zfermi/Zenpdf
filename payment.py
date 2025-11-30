"""
Payment handling routes for Pesapal integration
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

        # Get redirect URL from response
        redirect_url = result.get('redirect_url')
        order_tracking_id = result.get('order_tracking_id')

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


@payment_bp.route('/payment/callback', methods=['GET'])
@login_required
def payment_callback():
    """Handle payment callback from Pesapal"""
    try:
        # Get parameters from callback
        order_tracking_id = request.args.get('OrderTrackingId')
        order_merchant_reference = request.args.get('OrderMerchantReference')

        if not order_tracking_id:
            flash('Invalid payment callback.', 'error')
            return redirect(url_for('dashboard'))

        # Create Pesapal service
        pesapal = create_pesapal_service(current_app)

        # Get transaction status
        status_data = pesapal.get_transaction_status(order_tracking_id)

        payment_status = status_data.get('payment_status_description', '').lower()
        status_code = status_data.get('status_code')

        logger.info(f"Payment callback - User: {current_user.id}, Status: {payment_status}, Code: {status_code}")

        # Check if payment was successful
        if payment_status == 'completed' and status_code == 1:
            # Update user subscription
            current_user.subscription_tier = 'premium'
            current_user.subscription_start = datetime.utcnow()
            current_user.subscription_end = datetime.utcnow() + timedelta(days=30)

            db.session.commit()

            flash('Payment successful! Your premium subscription is now active.', 'success')
            logger.info(f"Premium subscription activated for user {current_user.id}")
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


@payment_bp.route('/payment/ipn', methods=['GET', 'POST'])
def payment_ipn():
    """Handle IPN (Instant Payment Notification) from Pesapal"""
    try:
        # Get parameters from IPN
        order_tracking_id = request.args.get('OrderTrackingId')
        order_notification_type = request.args.get('OrderNotificationType')
        order_merchant_reference = request.args.get('OrderMerchantReference')

        logger.info(f"IPN received - Tracking: {order_tracking_id}, Type: {order_notification_type}")

        if not order_tracking_id:
            return jsonify({'status': 'error', 'message': 'Missing order tracking ID'}), 400

        # Create Pesapal service
        pesapal = create_pesapal_service(current_app)

        # Get transaction status
        status_data = pesapal.get_transaction_status(order_tracking_id)

        payment_status = status_data.get('payment_status_description', '').lower()
        status_code = status_data.get('status_code')
        merchant_reference = status_data.get('merchant_reference', '')

        # Extract user ID from merchant reference (format: ZENPDF-{user_id}-{token})
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


@payment_bp.route('/payment/status/<order_tracking_id>', methods=['GET'])
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
