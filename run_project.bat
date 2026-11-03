@echo off
echo ======================================================================
echo          📚 Bootstrapping Library Management System 📚
echo ======================================================================
echo.

:: Step 1: Initialize Virtual Environment
if not exist .venv (
    echo Creating virtual environment [.venv]...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment found.
)

:: Step 2: Activate Environment
echo Activating virtual environment...
call .venv\Scripts\activate

:: Step 3: Install Dependencies
echo Installing project dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

:: Step 4: Run Migrations
echo Applying database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Failed to run migrations.
    pause
    exit /b 1
)

:: Step 5: Check Admin Superuser
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings'); django.setup(); from django.contrib.auth.models import User; print('[INFO] Superuser found.') if User.objects.filter(is_superuser=True).exists() else print('[INFO] No superuser found. Create one anytime with: python manage.py createsuperuser')"

:: Step 6: Populate Seed Data (if catalog empty)
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings'); django.setup(); from library.models import Book; Book.objects.bulk_create([Book(title='To Kill a Mockingbird', author='Harper Lee', category='Fiction', quantity=5), Book(title='1984', author='George Orwell', category='Dystopian', quantity=3), Book(title='The Great Gatsby', author='F. Scott Fitzgerald', category='Classic', quantity=4), Book(title='A Brief History of Time', author='Stephen Hawking', category='Science', quantity=2), Book(title='Introduction to Algorithms', author='Cormen, Leiserson, Rivest', category='Computer Science', quantity=6)]) if not Book.objects.exists() else None"

:: Step 7: Run Automated Tests
echo Running unit tests to verify stability...
python manage.py test
if errorlevel 1 (
    echo [WARNING] Test suite encountered warnings or errors. Check console above.
) else (
    echo [SUCCESS] All unit tests passed!
)
echo.

:: Step 8: Start server
echo ======================================================================
echo [READY] Launching local Django server at: http://127.0.0.1:8000/
echo ======================================================================
echo.
python manage.py runserver
