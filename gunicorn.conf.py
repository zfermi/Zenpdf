"""
Gunicorn configuration file for ZenPDF
Fixes reentrant logging errors during worker shutdown
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
# Reduced for Railway's memory limits (512MB free tier)
# Use environment variable to override, default to 2 workers for low memory environments
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000  # Recycle workers after 1000 requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Avoid reentrant logging issues
capture_output = False  # Don't capture stdout/stderr of workers
enable_stdio_inheritance = False  # Don't inherit stdio from parent

# Process naming
proc_name = 'zenpdf'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Pre-fork hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("ZenPDF server is ready. Spawning workers")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    # Completely suppress logging during shutdown to avoid reentrant calls
    pass

def worker_abort(worker):
    """Called when a worker times out and receives SIGABRT."""
    # Completely suppress logging during shutdown to avoid reentrant calls
    pass

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    pass

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass

def child_exit(server, worker):
    """Called just after a worker has been exited, in the master process."""
    # Suppress detailed logging during worker exit to avoid reentrant calls
    pass

def worker_exit(server, worker):
    """Called just after a worker has been exited, in the worker process."""
    pass

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    pass

def on_exit(server):
    """Called just before exiting Gunicorn."""
    pass
