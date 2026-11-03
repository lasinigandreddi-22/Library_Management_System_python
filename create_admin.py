import os
import sys
import django
from getpass import getpass

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not username or not password:
    print("--- Create / Update Admin Superuser ---")
    try:
        if not username:
            username = input("Username: ").strip()
        if not email:
            email = input("Email address (optional): ").strip()
        if not password:
            password = getpass("Password: ")
            confirm = getpass("Password (again): ")
            if password != confirm:
                print("Error: Passwords do not match.")
                sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(1)

if not username or not password:
    print("Error: Username and password are required.")
    sys.exit(1)

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()

if created:
    print(f"SUCCESS: Superuser '{username}' created successfully.")
else:
    print(f"SUCCESS: Superuser '{username}' password and staff privileges updated successfully.")
