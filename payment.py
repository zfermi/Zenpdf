"""
Payment handling routes for PayPal integration
"""
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models import db, User
from paypal_service import create_paypal_service

payment_bp = Blueprint('payment', __name__)
logger = logging.getLogger(__name__)


@payment_bp.route('/subscribe/premium', methods=['GET'])
@login_required
def subscribe_premium():
    """Initiate premium subscription payment via PayPal"""
    try:
        # Check if user is already premium
        if current_user.is_premium:
            flash('You already have an active premium subscription.', 'info')
            return redirect(url_for('dashboard'))

        # Create PayPal service
        paypal = create_paypal_service(current_app)

        # Generate unique order ID
        order_ref = f"BESTPDF-{current_user.id}-{secrets.token_hex(8)}"

        # Create payment order
        amount = current_app.config['PREMIUM_PRICE'] / 100  # Convert cents to dollars
        currency = 'USD'
        description = f'Best Pdf Converter Premium Subscription - Monthly'

        # Build return and cancel URLs
        return_url = url_for('payment.payment_success', _external=True)
        cancel_url = url_for('payment.payment_cancel', _external=True)

        result = paypal.create_order(
            amount=amount,
            currency=currency,
            order_id=order_ref,
            description=description,
            return_url=return_url,
            cancel_url=cancel_url
        )

        # Get approval URL
        approve_url = result.get('approve_url')
        paypal_order_id = result.get('order_id')

        if not approve_url:
            flash('Failed to initiate payment. Please try again.', 'error')
            logger.error(f"No approval URL in PayPal response: {result}")
            return redirect(url_for('pricing'))

        logger.info(f"Payment initiated for user {current_user.id}, PayPal order: {paypal_order_id}, ref: {order_ref}")

        # Redirect to PayPal for payment
        return redirect(approve_url)

    except Exception as e:
        logger.error(f"Payment initiation failed: {e}")
        flash('An error occurred while processing your payment. Please try again.', 'error')
        return redirect(url_for('pricing'))


@payment_bp.route('/success', methods=['GET'])
@login_required
def payment_success():
    """Handle successful payment return from PayPal"""
    try:
        # Get PayPal order ID from query params
        paypal_order_id = request.args.get('token')  # PayPal returns 'token' param

        if not paypal_order_id:
            flash('Invalid payment response.', 'error')
            return redirect(url_for('dashboard'))

        # Create PayPal service
        paypal = create_paypal_service(current_app)

        # Capture the payment
        capture_result = paypal.capture_order(paypal_order_id)

        # Check capture status
        status = capture_result.get('status')

        logger.info(f"PayPal capture result for order {paypal_order_id}: Status={status}")

        if status == 'COMPLETED':
            # Payment successful - activate premium subscription
            if not current_user.is_premium:
                current_user.subscription_tier = 'premium'
                current_user.subscription_start = datetime.utcnow()
                current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
                db.session.commit()
                logger.info(f"Premium subscription activated for user {current_user.id}")

            flash('Payment successful! Your premium subscription is now active.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Payment status: {status}. Please contact support if you were charged.', 'warning')
            return redirect(url_for('pricing'))

    except Exception as e:
        logger.error(f"Payment success handling failed: {e}")
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('dashboard'))


@payment_bp.route('/cancel', methods=['GET'])
@login_required
def payment_cancel():
    """Handle cancelled payment from PayPal"""
    logger.info(f"Payment cancelled by user {current_user.id}")
    flash('Payment was cancelled. You can try again anytime.', 'info')
    return redirect(url_for('pricing'))


@payment_bp.route('/webhook', methods=['POST'])
def paypal_webhook():
    """
    Handle PayPal webhook notifications (IPN alternative)
    For production, you should verify webhook signatures
    """
    try:
        event_data = request.get_json()
        event_type = event_data.get('event_type')

        logger.info(f"PayPal webhook received: {event_type}")

        # Handle different event types
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Payment captured successfully
            resource = event_data.get('resource', {})
            order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')

            logger.info(f"Payment captured via webhook for order: {order_id}")

            # You can add additional processing here
            # For now, the success callback handles subscription activation

        return jsonify({'status': 'received'}), 200

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@payment_bp.route('/status/<order_id>', methods=['GET'])
@login_required
def check_payment_status(order_id):
    """Check PayPal order status manually"""
    try:
        # Create PayPal service
        paypal = create_paypal_service(current_app)

        # Get order details
        order_details = paypal.get_order_details(order_id)

        return jsonify(order_details), 200

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500
