import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from wsgiref import simple_server
from django.core.management import call_command

def run_server():
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexa.settings')
    # Initialize Django
    django.setup()
    
    # Apply database migrations
    print("Applying database migrations...")
    try:
        call_command('migrate')
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Error applying migrations: {e}")
        sys.exit(1)
    
    # Get the WSGI application and start the server
    application = get_wsgi_application()
    httpd = simple_server.make_server('127.0.0.1', 8000, application)
    print("Django server running on http://127.0.0.1:8000")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")

if __name__ == '__main__':
    run_server()