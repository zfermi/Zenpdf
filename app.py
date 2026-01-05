"""
Best Pdf Converter - A SaaS PDF manipulation tool
Version 2.0.0 with full authentication and database support
"""
import os
import zipfile
import secrets
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, session
from flask_login import LoginManager, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv

# Optional PDF2Word conversion support
try:
    from pdf2docx import Converter
    PDF2WORD_AVAILABLE = True
except ImportError:
    PDF2WORD_AVAILABLE = False

# Load environment variables
load_dotenv()

# Import local modules
from config import config
from models import db, bcrypt, User, UsageRecord
from auth import auth_bp
from payment import payment_bp
from analytics import init_analytics
from analytics_middleware import setup_analytics_middleware

__version__ = "2.0.0"

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/zenpdf.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ZenPDF startup')

    # Log configuration warnings (avoid reentrant logging issues)
    if config_name == 'production':
        if not os.environ.get('DATABASE_URL'):
            app.logger.warning(
                "DATABASE_URL not set - using SQLite. "
                "For production, add PostgreSQL database in Railway dashboard."
            )
        if not os.environ.get('SECRET_KEY'):
            app.logger.warning(
                "SECRET_KEY not set - using default (INSECURE!). "
                "Set SECRET_KEY environment variable in Railway."
            )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )

    # Security headers (disable in development)
    if not app.debug:
        Talisman(
            app,
            force_https=app.config['TALISMAN_FORCE_HTTPS'],
            strict_transport_security=app.config['TALISMAN_STRICT_TRANSPORT_SECURITY'],
            content_security_policy=app.config['TALISMAN_CONTENT_SECURITY_POLICY']
        )

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(payment_bp, url_prefix='/payment')

    # Initialize server-side analytics
    from analytics import analytics
    init_analytics(app)
    if analytics:
        setup_analytics_middleware(app, analytics)

    # Context processor to inject Google Drive config into templates
    @app.context_processor
    def inject_google_config():
        return {
            'google_config': {
                'api_key': os.environ.get('GOOGLE_PICKER_API_KEY', ''),
                'client_id': os.environ.get('GOOGLE_DRIVE_CLIENT_ID', ''),
                'app_id': os.environ.get('GOOGLE_APP_ID', '')
            }
        }

    # ========== HELPER FUNCTIONS ==========

    def cleanup_old_files(folder, max_age_hours=1):
        """Remove files older than max_age_hours"""
        try:
            if not os.path.exists(folder):
                return
            current_time = datetime.now().timestamp()
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > (max_age_hours * 3600):
                        try:
                            os.remove(file_path)
                            app.logger.info(f'Cleaned up old file: {filename}')
                        except OSError as e:
                            app.logger.error(f'Failed to remove old file {filename}: {e}')
        except Exception as e:
            app.logger.error(f'Error during file cleanup in {folder}: {e}')

    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def sanitize_filename(filename):
        """Sanitize filename to prevent path traversal"""
        filename = os.path.basename(filename)
        filename = secure_filename(filename)
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        return filename

    def validate_file_size(file):
        """Validate file size based on user tier"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        # Premium users get higher limits, free users and anonymous get standard limit
        is_premium = current_user.is_authenticated and current_user.is_premium
        max_size = app.config['MAX_FILE_SIZE_PREMIUM'] if is_premium else app.config['MAX_FILE_SIZE']

        if size > max_size:
            max_mb = max_size // (1024 * 1024)
            raise ValueError(f"File size exceeds {max_mb}MB limit")
        if size == 0:
            raise ValueError("File is empty")
        return size

    def record_usage(operation_type, file_size=None, pages_processed=None, success=True, error_message=None):
        """Record usage for analytics and rate limiting"""
        if current_user.is_authenticated:
            usage = UsageRecord(
                user_id=current_user.id,
                operation_type=operation_type,
                file_size=file_size,
                pages_processed=pages_processed,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:255],
                success=success,
                error_message=error_message
            )
            db.session.add(usage)
            db.session.commit()

    def check_usage_limit():
        """Check if user has exceeded their usage limit - BASIC TOOLS ARE UNLIMITED"""
        # All basic PDF operations are FREE and UNLIMITED for everyone
        return True, None
    
    def check_ai_usage_limit():
        """Check if user can use AI features based on their credits"""
        if not current_user.is_authenticated:
            # Anonymous users cannot use AI features - require login
            return False, "Please sign up or log in to use AI features. Get 3 free AI credits every month!"
        
        if current_user.can_use_ai_feature():
            remaining = current_user.get_ai_credits_remaining()
            limit = current_user.get_ai_credits_limit()
            return True, f"AI credits: {remaining}/{limit} remaining this month"
        else:
            return False, f"You've used all your AI credits this month. Upgrade to Pro for 20 credits/month or Business for unlimited!"

    # Ensure upload folders exist
    for folder in [app.config['UPLOAD_FOLDER'], app.config['SPLIT_FOLDER'], app.config['MERGED_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Clean up old files on startup
    cleanup_old_files(app.config['SPLIT_FOLDER'], app.config['FILE_CLEANUP_HOURS'])
    cleanup_old_files(app.config['MERGED_FOLDER'], app.config['FILE_CLEANUP_HOURS'])
    cleanup_old_files(app.config['UPLOAD_FOLDER'], app.config['FILE_CLEANUP_HOURS'])

    # ========== ERROR HANDLERS ==========

    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def too_large(e):
        app.logger.warning(f'File too large from {request.remote_addr}')
        flash('File too large. Maximum size is 50MB for free users, 100MB for premium.', 'error')
        return redirect(request.url), 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'Internal error: {e}')
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('home')), 500

    @app.errorhandler(404)
    def not_found(e):
        return render_template('index.html'), 404

    # ========== PUBLIC ROUTES ==========

    @app.route('/')
    def home():
        return render_template('index.html', version=__version__)

    @app.route('/sitemap.xml')
    def sitemap():
        return send_file('static/sitemap.xml', mimetype='application/xml')

    @app.route('/robots.txt')
    def robots():
        return send_file('static/robots.txt', mimetype='text/plain')

    @app.route('/version')
    def version():
        """API endpoint to check version"""
        return jsonify({
            'version': __version__,
            'name': 'ZenPDF',
            'status': 'production'
        })

    @app.route('/health')
    def health():
        """Health check endpoint for monitoring"""
        try:
            # Check database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            app.logger.error(f'Database health check failed: {e}')
            db_status = 'unhealthy'

        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'version': __version__,
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if db_status == 'healthy' else 503

    @app.route('/api/live-stats')
    def live_stats():
        """API endpoint for live activity stats on homepage"""
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_operations = UsageRecord.query.filter(UsageRecord.created_at >= today_start).count()
            total_operations = UsageRecord.query.count()
            total_users = User.query.count()
            
            # Add some padding to make numbers look more impressive initially
            # These will naturally grow as real users come in
            display_today = today_operations + 47  # baseline activity
            display_total = total_operations + 5000  # baseline total
            display_users = total_users + 150  # baseline users
            
            return jsonify({
                'today_operations': display_today,
                'total_operations': display_total,
                'total_users': display_users,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            app.logger.error(f'Live stats error: {e}')
            return jsonify({
                'today_operations': 47,
                'total_operations': 5000,
                'total_users': 150,
                'timestamp': datetime.utcnow().isoformat()
            })

    @app.route('/pricing')
    def pricing():
        """Pricing page"""
        return render_template('pricing.html')

    @app.route('/privacy')
    def privacy_policy():
        """Privacy Policy page"""
        return render_template('privacy.html')

    @app.route('/terms')
    def terms_of_service():
        """Terms of Service page"""
        return render_template('terms.html')

    # ========== BLOG ==========

    @app.route('/blog')
    def blog():
        """Blog listing page"""
        return render_template('blog.html')

    @app.route('/blog/how-to-compress-pdf-without-losing-quality')
    def blog_compress():
        """Blog post: How to compress PDF"""
        return render_template('blog/how-to-compress-pdf-without-losing-quality.html')

    @app.route('/blog/merge-pdf-files-free-online')
    def blog_merge():
        """Blog post: How to merge PDF files"""
        return render_template('blog/merge-pdf-files-free-online.html')

    @app.route('/blog/split-pdf-extract-pages')
    def blog_split():
        """Blog post: How to split PDF"""
        return render_template('blog/split-pdf-extract-pages.html')

    @app.route('/blog/convert-pdf-to-word-editable')
    def blog_pdf2word():
        """Blog post: Convert PDF to Word"""
        return render_template('blog/convert-pdf-to-word-editable.html')

    @app.route('/blog/ocr-pdf-extract-text-scanned')
    def blog_ocr():
        """Blog post: OCR PDF extract text"""
        return render_template('blog/ocr-pdf-extract-text-scanned.html')

    @app.route('/blog/rotate-pdf-fix-orientation')
    def blog_rotate():
        """Blog post: Rotate PDF fix orientation"""
        return render_template('blog/rotate-pdf-fix-orientation.html')

    # ========== DASHBOARD ==========

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        # Get usage stats
        daily_usage = current_user.get_daily_usage_count()
        monthly_usage = current_user.get_monthly_usage_count()

        # Get recent operations
        recent_operations = current_user.usage_records.order_by(
            UsageRecord.created_at.desc()
        ).limit(10).all()

        return render_template('dashboard.html',
                             daily_usage=daily_usage,
                             monthly_usage=monthly_usage,
                             recent_operations=recent_operations)

    # ========== ADMIN PANEL ==========

    @app.route('/admin')
    @login_required
    def admin_panel():
        """Admin panel - only accessible to admin users"""
        # Check if user is admin
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))

        # Get all users
        users = User.query.order_by(User.created_at.desc()).all()

        # Get system statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        premium_users = User.query.filter(User.subscription_tier != 'free').count()

        # Get all operations
        total_operations = UsageRecord.query.count()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_operations = UsageRecord.query.filter(UsageRecord.created_at >= today_start).count()

        # Get recent operations across all users
        recent_operations = UsageRecord.query.order_by(
            UsageRecord.created_at.desc()
        ).limit(20).all()

        return render_template('admin_panel.html',
                             users=users,
                             total_users=total_users,
                             active_users=active_users,
                             premium_users=premium_users,
                             total_operations=total_operations,
                             today_operations=today_operations,
                             recent_operations=recent_operations)

    @app.route('/admin/user/<int:user_id>/toggle-active', methods=['POST'])
    @login_required
    def admin_toggle_user_active(user_id):
        """Toggle user active status"""
        if not current_user.is_admin:
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()

        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.email} has been {status}.', 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/admin/user/<int:user_id>/update-tier', methods=['POST'])
    @login_required
    def admin_update_user_tier(user_id):
        """Update user subscription tier"""
        if not current_user.is_admin:
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get_or_404(user_id)
        new_tier = request.form.get('tier')

        if new_tier not in ['free', 'premium', 'enterprise']:
            flash('Invalid subscription tier.', 'error')
            return redirect(url_for('admin_panel'))

        user.subscription_tier = new_tier

        # If upgrading to premium/enterprise, set subscription dates
        if new_tier != 'free':
            user.subscription_start = datetime.utcnow()
            # Set to 1 year from now
            from datetime import timedelta
            user.subscription_end = datetime.utcnow() + timedelta(days=365)
        else:
            user.subscription_start = None
            user.subscription_end = None

        db.session.commit()
        flash(f'User {user.email} subscription updated to {new_tier}.', 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
    @login_required
    def admin_toggle_user_admin(user_id):
        """Toggle user admin status"""
        if not current_user.is_admin:
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get_or_404(user_id)

        # Prevent removing admin from yourself
        if user.id == current_user.id:
            flash('You cannot remove admin privileges from yourself.', 'error')
            return redirect(url_for('admin_panel'))

        user.is_admin = not user.is_admin
        db.session.commit()

        status = 'granted' if user.is_admin else 'revoked'
        flash(f'Admin privileges {status} for {user.email}.', 'success')
        return redirect(url_for('admin_panel'))

    # ========== DOWNLOAD ENDPOINT ==========

    @app.route('/download/<filename>')
    def download_file(filename):
        """Download processed PDF file"""
        # Check in all possible folders
        for folder in [app.config['SPLIT_FOLDER'], app.config['MERGED_FOLDER'], app.config['UPLOAD_FOLDER']]:
            file_path = os.path.join(folder, filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True, download_name=filename, mimetype='application/pdf' if filename.endswith('.pdf') else 'application/zip')

        flash('File not found or has expired.', 'error')
        return redirect(url_for('home'))

    # ========== PDF OPERATIONS ==========

    @app.route('/split', methods=['GET', 'POST'])
    @limiter.limit("30 per hour")
    def split_pdf():
        if request.method == 'POST':
            if 'file' in request.files:
                # Check usage limit
                can_proceed, error_msg = check_usage_limit()
                if not can_proceed:
                    flash(error_msg, 'error')
                    return render_template('split.html', file_uploaded=False)

                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        file_size = validate_file_size(file)

                        safe_filename = sanitize_filename(file.filename)
                        unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        file.save(file_path)

                        try:
                            reader = PdfReader(file_path)
                            page_count = len(reader.pages)
                            if page_count == 0:
                                os.remove(file_path)
                                flash('Invalid PDF: File has no pages.', 'error')
                                return render_template('split.html', file_uploaded=False)
                        except Exception as e:
                            os.remove(file_path)
                            flash(f'Invalid PDF file: {str(e)}', 'error')
                            return render_template('split.html', file_uploaded=False)

                        session['split_file'] = unique_filename
                        flash('PDF uploaded successfully!', 'success')
                        return render_template('split.html', file_uploaded=True, page_count=page_count, file_name=unique_filename)

                    except ValueError as e:
                        flash(str(e), 'error')
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')
                else:
                    flash('Please select a valid PDF file.', 'error')

            elif 'split_type' in request.form:
                try:
                    file_name = session.get('split_file') or request.form.get('file_name')
                    if not file_name:
                        flash('File not found. Please upload again.', 'error')
                        return render_template('split.html', file_uploaded=False)

                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

                    if not os.path.exists(file_path):
                        flash('File not found. Please upload again.', 'error')
                        session.pop('split_file', None)
                        return render_template('split.html', file_uploaded=False)

                    split_type = request.form['split_type']
                    pages_to_split = []

                    reader = PdfReader(file_path)
                    total_pages = len(reader.pages)

                    if split_type == 'range':
                        try:
                            page_ranges = request.form.get('page_ranges', '').strip()
                            if not page_ranges:
                                flash('Please enter page ranges.', 'error')
                                return render_template('split.html', file_uploaded=True,
                                                     page_count=total_pages, file_name=file_name)
                            
                            page_set = set()
                            for part in page_ranges.split(','):
                                part = part.strip()
                                if '-' in part:
                                    start, end = map(int, part.split('-'))
                                    if start > end:
                                        flash(f'Invalid range: {start}-{end}. Start must be less than or equal to end.', 'error')
                                        return render_template('split.html', file_uploaded=True,
                                                             page_count=total_pages, file_name=file_name)
                                    page_set.update(range(start, end + 1))
                                else:
                                    page_set.add(int(part))
                            
                            # Validate all pages are within bounds
                            invalid_pages = [p for p in page_set if p < 1 or p > total_pages]
                            if invalid_pages:
                                flash(f'Invalid pages: {invalid_pages}. Pages must be between 1 and {total_pages}.', 'error')
                                return render_template('split.html', file_uploaded=True,
                                                     page_count=total_pages, file_name=file_name)
                            
                            pages_to_split = sorted([p - 1 for p in page_set])
                            
                            if not pages_to_split:
                                flash('No valid pages specified.', 'error')
                                return render_template('split.html', file_uploaded=True,
                                                     page_count=total_pages, file_name=file_name)
                        except ValueError:
                            flash('Invalid page range format. Use ranges like 1-5, 10-15.', 'error')
                            return render_template('split.html', file_uploaded=True,
                                                 page_count=total_pages, file_name=file_name)

                    elif split_type == 'specific':
                        try:
                            specific_pages = request.form.get('specific_pages', '').strip()
                            page_set = set()
                            for part in specific_pages.split(','):
                                part = part.strip()
                                if '-' in part:
                                    start, end = map(int, part.split('-'))
                                    page_set.update(range(start, end + 1))
                                else:
                                    page_set.add(int(part))

                            pages_to_split = sorted([p - 1 for p in page_set if 1 <= p <= total_pages])

                            if not pages_to_split:
                                flash('No valid pages specified.', 'error')
                                return render_template('split.html', file_uploaded=True,
                                                     page_count=total_pages, file_name=file_name)
                        except ValueError:
                            flash('Invalid page format. Use comma-separated numbers or ranges (e.g., 1,3,5-7).', 'error')
                            return render_template('split.html', file_uploaded=True,
                                                 page_count=total_pages, file_name=file_name)

                    elif split_type == 'even':
                        pages_to_split = [i for i in range(total_pages) if (i + 1) % 2 == 0]
                    elif split_type == 'odd':
                        pages_to_split = [i for i in range(total_pages) if (i + 1) % 2 != 0]
                    else:
                        flash('Invalid split type.', 'error')
                        return render_template('split.html', file_uploaded=True,
                                             page_count=total_pages, file_name=file_name)

                    if not pages_to_split:
                        flash('No pages selected to split.', 'error')
                        return render_template('split.html', file_uploaded=True,
                                             page_count=total_pages, file_name=file_name)

                    # Split PDF and create ZIP
                    zip_file_path = split_pdf_pages(file_path, pages_to_split, app.config['SPLIT_FOLDER'])
                    zip_filename = os.path.basename(zip_file_path)

                    # Record usage
                    file_size = os.path.getsize(file_path)
                    record_usage('split', file_size=file_size, pages_processed=len(pages_to_split))

                    # Clean up uploaded file
                    try:
                        os.remove(file_path)
                        session.pop('split_file', None)
                    except:
                        pass

                    # Return success page with download button instead of auto-download
                    return render_template('success.html',
                                         operation='Split',
                                         filename=zip_filename,
                                         pages_count=len(pages_to_split))

                except Exception as e:
                    record_usage('split', success=False, error_message=str(e))
                    flash(f'Error processing PDF: {str(e)}', 'error')
                    session.pop('split_file', None)
                    return render_template('split.html', file_uploaded=False)

        return render_template('split.html', file_uploaded=False)

    # Similar refactoring needed for compress, rotate, and merge routes
    # (keeping original logic but adding authentication and usage tracking)

    @app.route('/compress', methods=['GET', 'POST'])
    @limiter.limit("30 per hour")
    def compress_pdf():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file selected.', 'error')
                return render_template('compress.html', file_uploaded=False)

            # Check usage limit
            can_proceed, error_msg = check_usage_limit()
            if not can_proceed:
                flash(error_msg, 'error')
                return render_template('compress.html', file_uploaded=False)

            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    file_size = validate_file_size(file)

                    safe_filename = sanitize_filename(file.filename)
                    unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)

                    try:
                        reader = PdfReader(file_path)
                        page_count = len(reader.pages)
                        if page_count == 0:
                            os.remove(file_path)
                            flash('Invalid PDF: File has no pages.', 'error')
                            return render_template('compress.html', file_uploaded=False)
                    except Exception as e:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        app.logger.error(f'PDF validation error: {e}')
                        flash(f'Invalid PDF file: {str(e)}', 'error')
                        return render_template('compress.html', file_uploaded=False)

                    # Compress the PDF
                    compressed_path = compress_pdf_file(file_path)
                    compressed_filename = os.path.basename(compressed_path)

                    # Record usage
                    record_usage('compress', file_size=file_size, pages_processed=page_count)

                    # Clean up original file
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        app.logger.error(f'Failed to remove temp file: {e}')

                    # Return success page with download button
                    return render_template('success.html',
                                         operation='Compress',
                                         filename=compressed_filename,
                                         pages_count=page_count)

                except ValueError as e:
                    flash(str(e), 'error')
                except Exception as e:
                    app.logger.error(f'Compression error: {e}')
                    record_usage('compress', success=False, error_message=str(e))
                    flash(f'Error compressing PDF: {str(e)}', 'error')
            else:
                flash('Please select a valid PDF file.', 'error')

        return render_template('compress.html', file_uploaded=False)

    @app.route('/rotate', methods=['GET', 'POST'])
    @limiter.limit("30 per hour")
    def rotate_pdf():
        if request.method == 'POST':
            if 'file' in request.files:
                # Check usage limit
                can_proceed, error_msg = check_usage_limit()
                if not can_proceed:
                    flash(error_msg, 'error')
                    return render_template('rotate.html', file_uploaded=False)

                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        file_size = validate_file_size(file)

                        safe_filename = sanitize_filename(file.filename)
                        unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        file.save(file_path)

                        try:
                            reader = PdfReader(file_path)
                            page_count = len(reader.pages)
                            if page_count == 0:
                                os.remove(file_path)
                                flash('Invalid PDF: File has no pages.', 'error')
                                return render_template('rotate.html', file_uploaded=False)
                        except Exception as e:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            app.logger.error(f'PDF validation error: {e}')
                            flash(f'Invalid PDF file: {str(e)}', 'error')
                            return render_template('rotate.html', file_uploaded=False)

                        session['rotate_file'] = unique_filename
                        flash('PDF uploaded successfully!', 'success')
                        return render_template('rotate.html', file_uploaded=True, page_count=page_count, file_name=unique_filename)

                    except ValueError as e:
                        flash(str(e), 'error')
                    except Exception as e:
                        app.logger.error(f'Upload error: {e}')
                        flash(f'Error uploading file: {str(e)}', 'error')
                else:
                    flash('Please select a valid PDF file.', 'error')

            elif 'rotation_angle' in request.form:
                try:
                    file_name = session.get('rotate_file') or request.form.get('file_name')
                    if not file_name:
                        flash('File not found. Please upload again.', 'error')
                        return render_template('rotate.html', file_uploaded=False)

                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

                    if not os.path.exists(file_path):
                        flash('File not found. Please upload again.', 'error')
                        session.pop('rotate_file', None)
                        return render_template('rotate.html', file_uploaded=False)

                    rotation_angle = request.form['rotation_angle']
                    apply_to = request.form.get('apply_to', 'all')

                    # Rotate PDF
                    rotated_path = rotate_pdf_pages(file_path, rotation_angle, apply_to)
                    rotated_filename = os.path.basename(rotated_path)

                    # Record usage
                    file_size = os.path.getsize(file_path)
                    reader = PdfReader(file_path)
                    pages_processed = len(reader.pages)
                    record_usage('rotate', file_size=file_size, pages_processed=pages_processed)

                    # Clean up uploaded file
                    try:
                        os.remove(file_path)
                        session.pop('rotate_file', None)
                    except OSError as e:
                        app.logger.error(f'Failed to remove temp file: {e}')

                    # Return success page with download button
                    return render_template('success.html',
                                         operation='Rotate',
                                         filename=rotated_filename,
                                         pages_count=pages_processed)

                except Exception as e:
                    app.logger.error(f'Rotation error: {e}')
                    record_usage('rotate', success=False, error_message=str(e))
                    flash(f'Error rotating PDF: {str(e)}', 'error')
                    session.pop('rotate_file', None)
                    return render_template('rotate.html', file_uploaded=False)

        return render_template('rotate.html', file_uploaded=False)

    @app.route('/merge', methods=['GET', 'POST'])
    @limiter.limit("30 per hour")
    def merge_pdf():
        if request.method == 'POST':
            if 'files' in request.files:
                # Check usage limit
                can_proceed, error_msg = check_usage_limit()
                if not can_proceed:
                    flash(error_msg, 'error')
                    return render_template('merge.html', files_uploaded=False)

                files = request.files.getlist('files')
                max_files = app.config['MAX_MERGE_FILES_PREMIUM'] if current_user.is_premium else app.config['MAX_MERGE_FILES']

                if len(files) < 2:
                    flash('Please select at least 2 PDF files to merge.', 'error')
                    return render_template('merge.html', files_uploaded=False)

                if len(files) > max_files:
                    flash(f'Maximum {max_files} files allowed.', 'error')
                    return render_template('merge.html', files_uploaded=False)

                uploaded_files = []
                try:
                    for file in files:
                        if file and file.filename and allowed_file(file.filename):
                            try:
                                validate_file_size(file)
                                safe_filename = sanitize_filename(file.filename)
                                unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                                file_path = os.path.join(app.config['MERGED_FOLDER'], unique_filename)
                                file.save(file_path)
                                uploaded_files.append(unique_filename)
                            except ValueError as e:
                                # Clean up already uploaded files
                                for uploaded_file in uploaded_files:
                                    try:
                                        os.remove(os.path.join(app.config['MERGED_FOLDER'], uploaded_file))
                                    except OSError:
                                        pass
                                flash(str(e), 'error')
                                return render_template('merge.html', files_uploaded=False)

                    if uploaded_files:
                        session['merge_files'] = uploaded_files
                        flash(f'{len(uploaded_files)} files uploaded successfully!', 'success')
                        return render_template('merge.html', files_uploaded=True, file_names=uploaded_files)

                except Exception as e:
                    app.logger.error(f'Merge upload error: {e}')
                    flash(f'Error uploading files: {str(e)}', 'error')

        return render_template('merge.html', files_uploaded=False)

    @app.route('/rearrange', methods=['POST'])
    def rearrange_files():
        """Handle drag-and-drop reordering of files"""
        try:
            file_paths = request.json.get('file_paths', [])
            valid_paths = []
            for path in file_paths:
                if os.path.exists(os.path.join(app.config['MERGED_FOLDER'], path)):
                    valid_paths.append(path)
            return jsonify({'success': True, 'file_paths': valid_paths})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/merge_files', methods=['POST'])
    def merge_files():
        """Merge multiple PDF files"""
        try:
            file_paths = session.get('merge_files') or request.form.getlist('file_paths[]')

            if not file_paths:
                flash('No files to merge. Please upload files first.', 'error')
                return redirect(url_for('merge_pdf'))

            valid_paths = []
            for file_path in file_paths:
                full_path = os.path.join(app.config['MERGED_FOLDER'], file_path)
                if os.path.exists(full_path):
                    valid_paths.append(file_path)

            if not valid_paths:
                flash('Files not found. Please upload again.', 'error')
                session.pop('merge_files', None)
                return redirect(url_for('merge_pdf'))

            merged_file_path = merge_pdf_files(valid_paths, app.config['MERGED_FOLDER'])
            merged_filename = os.path.basename(merged_file_path)

            # Record usage
            total_size = sum(os.path.getsize(os.path.join(app.config['MERGED_FOLDER'], p)) for p in valid_paths if os.path.exists(os.path.join(app.config['MERGED_FOLDER'], p)))
            record_usage('merge', file_size=total_size, pages_processed=len(valid_paths))

            session.pop('merge_files', None)

            # Return success page with download button
            return render_template('success.html',
                                 operation='Merge',
                                 filename=merged_filename,
                                 files_count=len(valid_paths))

        except Exception as e:
            record_usage('merge', success=False, error_message=str(e))
            flash(f'Error merging PDFs: {str(e)}', 'error')
            session.pop('merge_files', None)
            return redirect(url_for('merge_pdf'))

    @app.route('/pdf2word', methods=['GET', 'POST'])
    @limiter.limit("30 per hour")
    def pdf2word():
        """Convert PDF to Word document"""
        if request.method == 'POST':
            # Check usage limit
            can_proceed, error_msg = check_usage_limit()
            if not can_proceed:
                flash(error_msg, 'error')
                return render_template('pdf2word.html')

            file = request.files.get('file')
            if file and file.filename and allowed_file(file.filename):
                try:
                    file_size = validate_file_size(file)

                    safe_filename = sanitize_filename(file.filename)
                    unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)

                    # Validate PDF
                    try:
                        reader = PdfReader(file_path)
                        page_count = len(reader.pages)
                        if page_count == 0:
                            os.remove(file_path)
                            flash('Invalid PDF: File has no pages.', 'error')
                            return render_template('pdf2word.html')
                    except Exception as e:
                        os.remove(file_path)
                        flash(f'Invalid PDF file: {str(e)}', 'error')
                        return render_template('pdf2word.html')

                    # Convert PDF to Word
                    word_file_path = convert_pdf_to_word(file_path, app.config['SPLIT_FOLDER'])

                    # Record usage
                    record_usage('pdf2word', file_size=file_size, pages_processed=page_count)

                    # Clean up uploaded PDF
                    try:
                        os.remove(file_path)
                    except:
                        pass

                    return send_file(word_file_path, as_attachment=True,
                                   download_name=f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                                   mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

                except ValueError as e:
                    flash(str(e), 'error')
                except Exception as e:
                    record_usage('pdf2word', success=False, error_message=str(e))
                    flash(f'Error converting PDF: {str(e)}', 'error')
            else:
                flash('Please select a valid PDF file.', 'error')

        return render_template('pdf2word.html')

    # ========== OCR (Premium Feature) ==========

    @app.route('/ocr', methods=['GET', 'POST'])
    @limiter.limit("20 per hour")
    def ocr_pdf():
        """OCR - Extract text from scanned PDFs (Premium feature)"""
        # Check if user is logged in
        if not current_user.is_authenticated:
            return render_template('ocr.html', ocr_results=None)
        
        # Check if user is premium
        if not current_user.is_premium:
            return render_template('ocr.html', ocr_results=None)
        
        if request.method == 'POST':
            # Check usage limit
            can_proceed, error_msg = check_usage_limit()
            if not can_proceed:
                flash(error_msg, 'error')
                return render_template('ocr.html', ocr_results=None)
            
            file = request.files.get('file')
            if file and file.filename and allowed_file(file.filename):
                try:
                    file_size = validate_file_size(file)
                    language = request.form.get('language', 'eng')
                    output_format = request.form.get('output_format', 'searchable_pdf')
                    
                    safe_filename = sanitize_filename(file.filename)
                    unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    # Validate PDF
                    try:
                        reader = PdfReader(file_path)
                        page_count = len(reader.pages)
                        if page_count == 0:
                            os.remove(file_path)
                            flash('Invalid PDF: File has no pages.', 'error')
                            return render_template('ocr.html', ocr_results=None)
                    except Exception as e:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        flash(f'Invalid PDF file: {str(e)}', 'error')
                        return render_template('ocr.html', ocr_results=None)
                    
                    # Perform OCR
                    try:
                        from ocr_engine import OCREngine, create_searchable_pdf
                        
                        ocr = OCREngine(dpi=300, language=language)
                        ocr_results = ocr.extract_text_from_pdf(file_path)
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        
                        # Create searchable PDF
                        output_filename = f"ocr_{timestamp}.pdf"
                        output_path = os.path.join(app.config['SPLIT_FOLDER'], output_filename)
                        create_searchable_pdf(file_path, ocr_results, output_path)
                        
                        # Create text file
                        text_filename = f"ocr_text_{timestamp}.txt"
                        text_path = os.path.join(app.config['SPLIT_FOLDER'], text_filename)
                        with open(text_path, 'w', encoding='utf-8') as f:
                            for result in ocr_results:
                                f.write(f"=== Page {result['page']} ===\n")
                                f.write(result['text'])
                                f.write("\n\n")
                        
                        # Record usage
                        record_usage('ocr', file_size=file_size, pages_processed=page_count)
                        
                        # Clean up uploaded file
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        
                        flash('OCR processing completed successfully!', 'success')
                        return render_template('ocr.html', 
                                             ocr_results=ocr_results,
                                             output_filename=output_filename,
                                             text_filename=text_filename)
                        
                    except ImportError as e:
                        app.logger.error(f'OCR import error: {e}')
                        flash('OCR feature is not available. Missing dependencies.', 'error')
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        return render_template('ocr.html', ocr_results=None)
                    except Exception as e:
                        app.logger.error(f'OCR processing error: {e}')
                        record_usage('ocr', success=False, error_message=str(e))
                        flash(f'OCR processing failed: {str(e)}', 'error')
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        return render_template('ocr.html', ocr_results=None)
                    
                except ValueError as e:
                    flash(str(e), 'error')
                except Exception as e:
                    app.logger.error(f'OCR error: {e}')
                    flash(f'Error processing file: {str(e)}', 'error')
            else:
                flash('Please select a valid PDF file.', 'error')
        
        return render_template('ocr.html', ocr_results=None)

    # ========== AI DOCUMENT INTELLIGENCE (Premium Features) ==========

    @app.route('/ai-tools')
    def ai_tools():
        """AI Tools hub page"""
        return render_template('ai-tools.html')

    @app.route('/ai/summarize', methods=['GET', 'POST'])
    @limiter.limit("20 per hour")
    def ai_summarize():
        """AI-powered PDF summarization"""
        if request.method == 'GET':
            return render_template('ai-summarize.html')
        
        # POST - Process the summarization request
        try:
            # Check if AI service is configured
            from ai_services import get_ai_service, summarize_document
            from document_intelligence import process_pdf_for_ai
            
            ai_service = get_ai_service()
            if not ai_service.is_configured():
                return jsonify({
                    'success': False,
                    'error': 'AI service not configured. Please contact administrator.'
                }), 503
            
            # Check AI credits
            can_use_ai, ai_msg = check_ai_usage_limit()
            if not can_use_ai:
                return jsonify({
                    'success': False,
                    'error': ai_msg,
                    'upgrade_required': True
                }), 403
            
            # Get file and options
            file = request.files.get('file')
            length = request.form.get('length', 'medium')
            format_type = request.form.get('format', 'paragraph')
            
            if not file or not file.filename:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type. Please upload a PDF.'}), 400
            
            # Save and process file
            try:
                file_size = validate_file_size(file)
            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 400
            
            safe_filename = sanitize_filename(file.filename)
            unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            try:
                # Extract text from PDF
                pdf_data = process_pdf_for_ai(file_path)
                
                if not pdf_data['success']:
                    return jsonify({
                        'success': False,
                        'error': pdf_data.get('error', 'Failed to extract text from PDF')
                    }), 400
                
                if not pdf_data['text'] or len(pdf_data['text'].strip()) < 50:
                    return jsonify({
                        'success': False,
                        'error': 'PDF contains too little text to summarize.'
                    }), 400
                
                # Generate summary
                summary_result = summarize_document(
                    pdf_data['text'],
                    length=length,
                    format=format_type
                )
                
                if not summary_result.get('success'):
                    return jsonify({
                        'success': False,
                        'error': summary_result.get('error', 'Summarization failed')
                    }), 500
                
                # Record usage and consume AI credit
                record_usage('ai_summarize', file_size=file_size, pages_processed=pdf_data['page_count'])
                if current_user.is_authenticated:
                    current_user.use_ai_credit()
                
                # Return results
                return jsonify({
                    'success': True,
                    'summary': summary_result.get('summary'),
                    'key_points': summary_result.get('key_points', []),
                    'main_topic': summary_result.get('main_topic'),
                    'document_type': summary_result.get('document_type'),
                    'page_count': pdf_data['page_count'],
                    'original_word_count': pdf_data['word_count'],
                    'summary_word_count': summary_result.get('summary_word_count', 0)
                })
                
            finally:
                # Clean up
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                        
        except ImportError as e:
            app.logger.error(f'AI module import error: {e}')
            return jsonify({
                'success': False,
                'error': 'AI features are not available. Missing dependencies.'
            }), 503
        except Exception as e:
            app.logger.error(f'AI summarization error: {e}')
            return jsonify({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }), 500

    @app.route('/ai/extract-tables', methods=['GET', 'POST'])
    @limiter.limit("20 per hour")
    def ai_extract_tables():
        """Extract tables from PDF to CSV/JSON"""
        if request.method == 'GET':
            return render_template('ai-extract-tables.html')
        
        try:
            from document_intelligence import extract_tables_to_format, process_pdf_for_ai
            from ai_services import get_ai_service, detect_tables_in_text
            
            # Check AI credits
            can_use_ai, ai_msg = check_ai_usage_limit()
            if not can_use_ai:
                return jsonify({
                    'success': False,
                    'error': ai_msg,
                    'upgrade_required': True
                }), 403
            
            # Get file and format
            file = request.files.get('file')
            output_format = request.form.get('format', 'csv')
            
            if not file or not file.filename:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type. Please upload a PDF.'}), 400
            
            # Save and process file
            try:
                file_size = validate_file_size(file)
            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 400
            
            safe_filename = sanitize_filename(file.filename)
            unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            try:
                # Extract tables using pattern matching first
                table_result = extract_tables_to_format(file_path, output_format)
                
                # If no tables found with pattern matching, try AI detection
                if table_result.get('success') and not table_result.get('tables_found'):
                    ai_service = get_ai_service()
                    if ai_service.is_configured():
                        # Get the text first
                        pdf_data = process_pdf_for_ai(file_path)
                        if pdf_data['success'] and pdf_data['text']:
                            ai_tables = detect_tables_in_text(pdf_data['text'])
                            if ai_tables.get('success') and ai_tables.get('tables_found'):
                                table_result = {
                                    'success': True,
                                    'tables_found': True,
                                    'table_count': ai_tables['table_count'],
                                    'tables': ai_tables['tables'],
                                    'formatted_data': json.dumps(ai_tables['tables'], indent=2) if output_format == 'json' else '',
                                    'detection_method': 'ai'
                                }
                
                # Record usage and consume AI credit
                record_usage('ai_extract_tables', file_size=file_size)
                if current_user.is_authenticated:
                    current_user.use_ai_credit()
                
                return jsonify(table_result)
                
            finally:
                # Clean up
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                        
        except ImportError as e:
            app.logger.error(f'Document intelligence import error: {e}')
            return jsonify({
                'success': False,
                'error': 'Table extraction features are not available.'
            }), 503
        except Exception as e:
            app.logger.error(f'Table extraction error: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/ai/process-pdf', methods=['POST'])
    @limiter.limit("30 per hour")
    def ai_process_pdf():
        """Process PDF and extract text for Q&A"""
        try:
            from document_intelligence import process_pdf_for_ai
            
            # Check AI credits
            can_use_ai, ai_msg = check_ai_usage_limit()
            if not can_use_ai:
                return jsonify({
                    'success': False,
                    'error': ai_msg,
                    'upgrade_required': True
                }), 403
            
            file = request.files.get('file')
            if not file or not file.filename:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
            try:
                file_size = validate_file_size(file)
            except ValueError as e:
                return jsonify({'success': False, 'error': str(e)}), 400
            
            safe_filename = sanitize_filename(file.filename)
            unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            try:
                pdf_data = process_pdf_for_ai(file_path)
                
                if not pdf_data['success']:
                    return jsonify({
                        'success': False,
                        'error': pdf_data.get('error', 'Failed to process PDF')
                    }), 400
                
                return jsonify({
                    'success': True,
                    'text': pdf_data['text'],
                    'page_count': pdf_data['page_count'],
                    'word_count': pdf_data['word_count'],
                    'file_name': file.filename
                })
                
            finally:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                        
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Document processing features are not available.'
            }), 503
        except Exception as e:
            app.logger.error(f'PDF processing error: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/ai/qa', methods=['GET', 'POST'])
    @limiter.limit("30 per hour")
    def ai_qa():
        """AI-powered PDF Q&A"""
        if request.method == 'GET':
            return render_template('ai-qa.html')
        
        try:
            from ai_services import get_ai_service, answer_question
            
            ai_service = get_ai_service()
            if not ai_service.is_configured():
                return jsonify({
                    'success': False,
                    'error': 'AI service not configured.'
                }), 503
            
            # Check AI credits
            can_use_ai, ai_msg = check_ai_usage_limit()
            if not can_use_ai:
                return jsonify({
                    'success': False,
                    'error': ai_msg,
                    'upgrade_required': True
                }), 403
            
            # Get question and text from request
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            question = data.get('question', '').strip()
            text = data.get('text', '')
            
            if not question:
                return jsonify({'success': False, 'error': 'Please provide a question'}), 400
            
            if not text:
                return jsonify({'success': False, 'error': 'No document text provided'}), 400
            
            # Answer the question
            qa_result = answer_question(text, question)
            
            if not qa_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': qa_result.get('error', 'Failed to answer question')
                }), 500
            
            # Record usage and consume AI credit
            record_usage('ai_qa')
            if current_user.is_authenticated:
                current_user.use_ai_credit()
            
            return jsonify({
                'success': True,
                'answer': qa_result.get('answer'),
                'confidence': qa_result.get('confidence', 'medium'),
                'relevant_quotes': qa_result.get('relevant_quotes', []),
                'question': question
            })
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'AI features are not available.'
            }), 503
        except Exception as e:
            app.logger.error(f'AI Q&A error: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500

    # ========== PDF PROCESSING FUNCTIONS ==========

    def split_pdf_pages(pdf_path, pages_to_split, output_dir):
        """Split PDF pages and create ZIP file"""
        reader = PdfReader(pdf_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_file_path = os.path.join(output_dir, f"split_pages_{timestamp}.zip")

        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for page_num in pages_to_split:
                if page_num >= len(reader.pages):
                    continue

                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])

                split_filename = f"page_{page_num + 1}.pdf"
                split_file_path = os.path.join(output_dir, split_filename)

                with open(split_file_path, "wb") as output_pdf:
                    writer.write(output_pdf)

                zip_file.write(split_file_path, split_filename)

                try:
                    os.remove(split_file_path)
                except:
                    pass

        return zip_file_path

    def merge_pdf_files(file_paths, output_dir):
        """Merge multiple PDF files into one"""
        writer = PdfWriter()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for pdf_file in file_paths:
            pdf_path = os.path.join(output_dir, pdf_file)
            if not os.path.exists(pdf_path):
                continue

            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            except:
                continue

        merged_file_path = os.path.join(output_dir, f"merged_{timestamp}.pdf")
        with open(merged_file_path, "wb") as output_pdf:
            writer.write(output_pdf)

        for pdf_file in file_paths:
            try:
                os.remove(os.path.join(output_dir, pdf_file))
            except:
                pass

        return merged_file_path

    def compress_pdf_file(pdf_path, compression_level='medium'):
        """Compress PDF by removing unnecessary content"""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)

        compressed_file_path = os.path.join(app.config['SPLIT_FOLDER'], f"compressed_{timestamp}.pdf")
        with open(compressed_file_path, "wb") as output_pdf:
            writer.write(output_pdf)

        return compressed_file_path

    def rotate_pdf_pages(pdf_path, rotation_angle, apply_to='all'):
        """Rotate PDF pages by specified angle"""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        angle = int(rotation_angle)

        for idx, page in enumerate(reader.pages):
            should_rotate = apply_to == 'all'
            if apply_to == 'odd' and (idx + 1) % 2 != 0:
                should_rotate = True
            elif apply_to == 'even' and (idx + 1) % 2 == 0:
                should_rotate = True

            if should_rotate:
                page.rotate(angle)

            writer.add_page(page)

        rotated_file_path = os.path.join(app.config['SPLIT_FOLDER'], f"rotated_{timestamp}.pdf")
        with open(rotated_file_path, "wb") as output_pdf:
            writer.write(output_pdf)

        return rotated_file_path

    def convert_pdf_to_word(pdf_path, output_dir):
        """Convert PDF to Word document using pdf2docx"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        word_file_path = os.path.join(output_dir, f"converted_{timestamp}.docx")

        # Create converter instance
        cv = Converter(pdf_path)

        # Convert PDF to DOCX
        cv.convert(word_file_path, start=0, end=None)
        cv.close()

        return word_file_path

    return app


# ========== APPLICATION INSTANCE ==========

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    with app.app_context():
        db.create_all()  # Create tables if they don't exist

    app.run(host=host, port=port, debug=debug)
