import os
import sys
import django
import logging
from django.core.wsgi import get_wsgi_application
from wsgiref import simple_server
from django.core.management import call_command

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('django_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def setup_database():
    """Handle database setup including migrations and superuser creation"""
    # Apply database migrations
    logging.info("Applying database migrations...")
    try:
        call_command('migrate', verbosity=0)
        logging.info("Migrations applied successfully.")
    except Exception as e:
        logging.error(f"Error applying migrations: {e}")
        # Don't exit - the app might still work
    
    # Create superuser (only if needed)
    logging.info("Checking for superuser...")
    try:
        from django.contrib.auth.models import User
        
        # Check if any superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            logging.info("Superuser already exists, skipping creation.")
        else:
            # Create superuser with default credentials
            # You can modify these values as needed
            username = 'admin'
            email = 'admin@example.com'
            password = 'admin123'  # Change this to a secure password
            
            User.objects.create_superuser(username=username, email=email, password=password)
            logging.info(f"Superuser '{username}' created successfully with password '{password}'")
            
    except Exception as e:
        logging.warning(f"Superuser creation failed: {e}")

def run_server():
    try:
        # Set the Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexa.settings')
        
        # Initialize Django
        django.setup()
        
        # Setup database and superuser
        setup_database()
        
        # Collect static files (if needed)
        try:
            call_command('collectstatic', interactive=False, verbosity=0)
            logging.info("Static files collected.")
        except Exception as e:
            logging.warning(f"Static files collection failed: {e}")
        
        # Get the WSGI application and start the server
        application = get_wsgi_application()
        
        # Try different ports if 8000 is busy
        ports_to_try = [8000, 8001, 8002, 8003]
        server_started = False
        
        for port in ports_to_try:
            try:
                httpd = simple_server.make_server('127.0.0.1', port, application)
                logging.info(f"Django server running on http://127.0.0.1:{port}")
                server_started = True
                break
            except OSError as e:
                if "Address already in use" in str(e):
                    logging.warning(f"Port {port} is busy, trying next port...")
                    continue
                else:
                    raise e
        
        if not server_started:
            logging.error("Could not start server on any available port")
            sys.exit(1)
        
        # Start serving
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped by user")
        except Exception as e:
            logging.error(f"Server error: {e}")
            
    except Exception as e:
        logging.error(f"Failed to start Django server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server()