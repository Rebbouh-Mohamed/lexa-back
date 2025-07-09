from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexa.settings')
django.setup()
User = get_user_model()

# Initialize Django
superuser_data = {
    'email': 'admin@example.com',
    'username':'admin',
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