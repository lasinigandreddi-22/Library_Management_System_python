# 📚 LibraryHub — Library Management System

A production-ready, full-stack web application designed with a modern **Glassmorphic UI** to streamline university library operations, academic asset borrowing, reading cabin reservations, and automated overdue fine calculations.

Built using **Python**, **Django**, **PostgreSQL** (production) / **SQLite** (development), and styled with a custom responsive **CSS Glassmorphism** design system.

---

## 🌟 Project Overview

LibraryHub serves as a centralized campus portal for students, faculty members, and library administrators:
- **Students** can discover books, check real-time stock availability, borrow titles, reserve books, book quiet study cabins, track due dates, and monitor fines.
- **Faculty Members** enjoy dedicated workspace access for curriculum reference and academic catalog searching without transaction restrictions.
- **Administrators** possess full administrative authority to manage book catalogs, maintain student and faculty registries, audit active borrow records, mark returns, and manage fines.

---

## 🚀 Key Modules & Features

### 📖 Module 1: Book Catalog Management
- **Catalog CRUD**: Add new book titles, update volume details (author, category, stock), and delete obsolete entries.
- **Live Stock Tracking**: Dynamic stock counters automatically decrement on book borrow and increment on book return.
- **Smart Catalog Search**: Instant multi-field filtering by title, author, or category with real-time feedback.

### 🎓 Module 2: Student & Faculty Management
- **Role-Aware Separation**:
  - **Student Accounts**: Assigned unique Student IDs, branch tracking, transaction limits, and reading cabin bookings.
  - **Faculty Accounts**: Assigned unique Faculty IDs, department tracking, and dedicated catalog reference privileges.
- **Admin Management**: View, search, update, and manage both student and faculty member profiles.

### 🔄 Module 3: Book Issue & Return (Transaction Auditing)
- **Instant Borrowing**: Students can borrow available books with instant duplicate borrow prevention.
- **Book Return**: One-click return processing with dynamic stock updates and automatic return date stamping.
- **Transaction History**: Comprehensive historical logs for students, faculty, and administrative audits.
- **Book Reservation**: Pre-reserve books for specific dates and hourly time slots.

### 💰 Module 4: Fine Management
- **Automated Overdue Calculation**: Tracks book return dates against calculated due dates (14-day default borrowing window).
- **Fine Ledger**: Auto-generates pending fines (₹5/day overdue) upon late return.
- **Payment Processing**: Administrators can review, filter (Pending / Paid), and record fine clearance payments.

### 🪑 Module 5: Reading Cabin / Slot Booking
- **Quiet Study Cabin Reservation**: Students can book a 1-hour quiet study slot on future dates.
- **Fixed Hourly Slots**:
  - `09:00 AM - 10:00 AM`
  - `10:00 AM - 11:00 AM`
  - `11:00 AM - 12:00 PM`
  - `12:00 PM - 01:00 PM`
  - `02:00 PM - 03:00 PM`
  - `03:00 PM - 04:00 PM`
  - `04:00 PM - 05:00 PM`
- **Double-Booking Prevention**: Database-level `UniqueConstraint` on `(booking_date, time_slot)` for active reservations.
- **Self-Service Cancellation**: Students can cancel their own active bookings with real-time slot release.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.11+, Django 5+ / 6+ |
| **WSGI Server** | Gunicorn (Production) |
| **Production Database** | PostgreSQL (Render Managed) |
| **Development Database**| SQLite3 (Zero setup required) |
| **Static File Asset Engine** | WhiteNoise with Brotli / Gzip compression |
| **Frontend & Styling** | Semantic HTML5, Vanilla CSS3 (Custom Glassmorphism, CSS Variables, Flexbox/Grid) |
| **Deployment Platform** | Render (Web Service + Managed PostgreSQL) |
| **Version Control** | Git & GitHub |

---

## 📁 Project Folder Structure

```text
Library-Management-System/
├── build.sh                      # Render automated build & migration script
├── create_admin.py               # Secure administrative superuser helper
├── manage.py                     # Django management CLI script
├── README.md                     # Comprehensive documentation
├── render.yaml                   # Infrastructure-as-Code for Render deployment
├── requirements.txt              # Production Python package dependencies
├── run_project.bat               # Windows 1-click bootstrap script
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git tracking exclusion rules
│
├── library/                      # Core Django Application
│   ├── admin.py                  # Django Admin model registrations
│   ├── apps.py                   # Application configuration
│   ├── forms.py                  # Forms for student/faculty registration & editing
│   ├── models.py                 # Student, Faculty, Book, BorrowRecord, Fine, etc.
│   ├── tests.py                  # Automated test suite (21 unit tests)
│   ├── urls.py                   # App routing endpoints
│   ├── views.py                  # Role-aware controllers & views
│   └── migrations/               # Database migration files (0001 to 0006)
│
├── library_system/               # Project Root Configuration
│   ├── __init__.py
│   ├── asgi.py                   # ASGI entry point
│   ├── settings.py               # Dynamic settings (Decouple + WhiteNoise + dj-database-url)
│   ├── urls.py                   # Main project URL routing
│   └── wsgi.py                   # WSGI entry point for Gunicorn
│
├── static/                       # Static Assets
│   └── css/
│       └── style.css             # Glassmorphism design system & responsive layout
│
└── templates/                    # HTML Templates
    └── library/
        ├── admin_fines.html
        ├── base.html             # Role-aware navigation header & footer
        ├── book_confirm_delete.html
        ├── book_form.html
        ├── book_reading_room.html
        ├── borrow_history.html
        ├── faculty_confirm_delete.html
        ├── faculty_form.html
        ├── home.html
        ├── login.html
        ├── manage_faculty.html
        ├── manage_students.html
        ├── my_fines.html
        ├── my_reading_room_bookings.html
        ├── my_reservations.html
        ├── register.html
        ├── reserve_book.html
        ├── student_confirm_delete.html
        ├── student_dashboard.html
        └── student_form.html
```

---

## ⚙️ Environment Variables

The project reads settings dynamically via `python-decouple` / environment variables. To configure custom settings locally, copy `.env.example` to `.env`:

| Variable | Default Value | Description |
|---|---|---|
| `SECRET_KEY` | Development fallback key | Secret key for cryptographic signing (must be secret in production) |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated list of permitted hostnames |
| `DATABASE_URL` | None (uses `db.sqlite3`) | PostgreSQL connection URL string for production |
| `CSRF_TRUSTED_ORIGINS` | None | Comma-separated list of origins (e.g. `https://your-app.onrender.com`) |
| `SECURE_SSL_REDIRECT` | `True` (when `DEBUG=False`)| Forces HTTPS redirection in production |

---

## 💻 Local Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
cd <YOUR_REPOSITORY>
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create an Administrator Superuser
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

> [!TIP]
> **Windows Quick-Start**: Windows users can simply double-click `run_project.bat` to automate virtual environment creation, dependency installation, database migrations, and server launch.

---

## 🌐 Live Deployment on Render (with PostgreSQL)

### Step 1: Create a PostgreSQL Database on Render
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **PostgreSQL**.
3. Enter a name (e.g., `libraryhub-postgres`).
4. Select the **Free** instance type.
5. Click **Create Database**.
6. Wait for creation, then copy the **Internal Database URL** (or External Database URL if needed).

### Step 2: Create a Web Service on Render
1. In your Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository containing this project.
3. Configure the following fields:
   - **Name**: `libraryhub` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn library_system.wsgi:application`
   - **Plan**: `Free`

### Step 3: Add Environment Variables
In the Render Web Service settings, go to **Environment** and add:
- `PYTHON_VERSION`: `3.11.9`
- `DEBUG`: `False`
- `SECRET_KEY`: *(Generate a random 50-character string or use Render's generate button)*
- `DATABASE_URL`: *(Paste your Render PostgreSQL connection string)*
- `ALLOWED_HOSTS`: `*.onrender.com`

### Step 4: Deploy & Verify
1. Click **Deploy Web Service**.
2. Render will automatically execute `build.sh`:
   - Upgrades pip and installs packages from `requirements.txt`.
   - Runs `collectstatic` to package all CSS and static files with WhiteNoise.
   - Runs database migrations on your PostgreSQL instance.
   - Launches Gunicorn on your live HTTPS URL.
3. Access your live website at `https://<your-service-name>.onrender.com`.

---

## 📸 Application Screenshots

| Page | Description |
|---|---|
| **Landing Page** | Clean, dark glassmorphic homepage welcoming students and faculty with quick navigation. |
| **Student Dashboard** | Live stats counter, reading cabin booking widget, personal fine status, and book catalog with instant borrow buttons. |
| **Faculty Workspace** | Dedicated reference portal displaying faculty ID, department badge, and clean catalog research views. |
| **Reading Cabin** | Interactive slot booking interface allowing choice of future dates and available hourly study slots. |
| **Admin Fine Portal** | Central fine audit table with status filtering (Pending / Paid) and single-click fine settlement. |

---

## 🧪 Automated Testing & Quality Assurance

The application comes with an automated test suite containing 21 test cases covering authentication, role-based view protections, catalog CRUD, reading cabin constraints, and fine tracking:

```bash
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
.....................
----------------------------------------------------------------------
Ran 21 tests in 95.719s

OK
Destroying test database for alias 'default'...
System check identified no issues (0 silenced).
```

---

## 📄 License & Attribution

This project was developed for academic and institutional library management. Licensed under the [MIT License](LICENSE).
