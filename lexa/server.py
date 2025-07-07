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
    from django.conf import settings
    import os

    database_path = settings.DATABASES['default']['NAME']
    database_exists = os.path.exists(database_path)

    # Apply database migrations
    logging.info("Checking database migrations...")
    try:
        if not database_exists:
            logging.info("Database not found, applying migrations...")
            call_command('migrate', verbosity=0)
            logging.info("Migrations applied successfully.")
        else:
            logging.info("Database exists, checking for pending migrations...")
            call_command('migrate', verbosity=0)
            logging.info("Pending migrations applied successfully.")
    except Exception as e:
        logging.error(f"Error applying migrations: {e}")
        # Continue running even if migrations fail, as the app might still function

    # Create superuser (only if needed)
    logging.info("Checking for superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if User.objects.filter(is_superuser=True).exists():
            logging.info("Superuser already exists, skipping creation.")
        else:
            superuser_data = {
                'email': 'admin@example.com',
                'password': 'admin123',  # Use a secure password in production
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'status': 'active',
                'subscription_status': 'active',
                'subscription_plan': 'unlimited',
                'phone': '+213555000000',  # Example Algerian phone
                'address': 'System Admin Address',
                'wilaya': '16',  # Algiers province code
            }

            User.objects.create_superuser(**superuser_data)
            logging.info(f"Superuser '{superuser_data['email']}' created successfully")
            logging.info(f"Login credentials - Email: {superuser_data['email']}, Password: {superuser_data['password']}")
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
                logging.info(f"Admin panel available at: http://127.0.0.1:{port}/admin/")
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