# 🏠 RentHive — Rental Management System

A comprehensive web-based rental property management system built with Flask + PostgreSQL, featuring owner and tenant dashboards, billing management, meter readings, and PDF invoice generation.

## 📋 Table of Contents
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Quick Start (Local)](#-quick-start-local)
- [Configuration](#-configuration)
- [Database & Migrations](#-database--migrations)
- [Deploy to Vercel](#-deploy-to-vercel)
- [Deploy to Render](#-deploy-to-render)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [License](#-license)

## ✨ Features

### For Property Owners
- 📊 Comprehensive dashboard with statistics
- 🏢 Property and room management
- 👥 Tenant management with secure document uploads
- 💰 Automated bill generation with PDF receipts
- 📈 Revenue tracking and analytics
- ⚡ Meter reading management (electricity/water)
- 🔔 Email notification system

### For Tenants
- 📱 Personal dashboard
- 📄 View and download bills
- 💳 Payment history tracking
- 📊 Meter reading history
- 👤 Profile management

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: PostgreSQL (production) / SQLite (local dev fallback)
- **ORM**: SQLAlchemy + Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: Flask-Login + Werkzeug password hashing
- **Forms**: Flask-WTF (CSRF-protected)
- **Production server**: Gunicorn

### Frontend
- **UI Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.4

### PDF Generation
- **Library**: ReportLab

## 📥 Quick Start (Local)

### Prerequisites
- Python 3.11+
- pip
- PostgreSQL (recommended) **or** use the built-in SQLite fallback

### Steps
```bash
# 1. Clone
git clone https://github.com/<your-username>/RentHive.git
cd RentHive

# 2. Create venv
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install deps
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and set SECRET_KEY (and DATABASE_URL if using Postgres locally)

# 5. Initialize database (creates tables via migrations)
flask --app run db init      # only the first time
flask --app run db migrate -m "initial"
flask --app run db upgrade

# 6. (Optional) Seed demo data
flask --app run seed_db

# 7. Run
python run.py
```

App will be available at `http://localhost:5000`.

### Default seed credentials
| Role   | Username | Password    |
|--------|----------|-------------|
| Owner  | owner    | password123 |
| Tenant | tenant   | password123 |

## ⚙️ Configuration

All configuration is loaded from environment variables (see `.env.example`).

| Variable            | Required | Description |
|---------------------|----------|-------------|
| `SECRET_KEY`        | yes      | Long random string for Flask sessions. Generate with `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `FLASK_ENV`         | yes      | `development` or `production` |
| `DATABASE_URL`      | yes (prod) | PostgreSQL connection string. `postgres://` is auto-normalized. |
| `PORT`              | no       | Default `5000` |
| `MAX_CONTENT_LENGTH`| no       | Default `16777216` (16 MB) |
| `UPLOAD_FOLDER`     | no       | Default `uploads` |
| `BILLS_FOLDER`      | no       | Default `bills` |
| `MAIL_SERVER` / `MAIL_USERNAME` / `MAIL_PASSWORD` | no | SMTP for outbound email |
| `LOG_LEVEL`         | no       | Default `INFO` |

> ⚠️ Never commit the real `.env`. The `.gitignore` excludes it.

## 🗄️ Database & Migrations

The app uses PostgreSQL in production. SQLite is supported **only** as a local-development fallback when `DATABASE_URL` is unset and `FLASK_ENV=development`.

### Local Postgres
```bash
# Create DB
createdb renthive
export DATABASE_URL=postgresql://localhost/renthive

# Apply migrations
flask --app run db upgrade
```

### Initial migration workflow (first-time setup)
```bash
export FLASK_APP=run.py
flask db init                       # creates migrations/ folder (one time)
flask db migrate -m "initial schema"
flask db upgrade
```

### Subsequent schema changes
```bash
flask db migrate -m "describe change"
flask db upgrade
```

## 🚀 Deploy to Vercel

**Recommended for**: Fast deployment, no server management, global CDN, free tier availability.

See **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** for detailed step-by-step instructions.

### Quick Summary:

1. **Set up PostgreSQL database** (Supabase, Railway, or Neon — all have free tiers)
2. **Push repo to GitHub**
3. **Connect to Vercel**:
   - https://vercel.com/new
   - Import from GitHub
   - Click "Deploy"
4. **Set environment variables** in Vercel dashboard:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<generate-new>`
   - `DATABASE_URL=postgresql://...`
5. **Initialize database**:
   ```bash
   vercel env pull
   python deploy_init.py
   ```
6. **Verify deployment**:
   ```bash
   python verify_deployment.py
   ```
7. **Test**: Visit your Vercel URL and register a test account

**Deployment files included**:
- `vercel.json` — Vercel configuration
- `api/index.py` — Serverless entry point
- `deploy_init.py` — Database initialization
- `verify_deployment.py` — Deployment verification

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) to track progress.

## 🚀 Deploy to Render

### Option A — One-click Blueprint (recommended)
1. Push this repo to GitHub.
2. In Render dashboard, click **New +** → **Blueprint**.
3. Select this repository — Render reads `render.yaml` and provisions:
   - Web service (`renthive`)
   - PostgreSQL database (`renthive-db`)
4. After the Web Service is created, set the `SECRET_KEY` env var in the dashboard.
5. Render will run `gunicorn run:app` per the `Procfile`.

### Option B — Manual setup
1. Create a new **PostgreSQL** instance in Render; copy its **Internal Connection String**.
2. Create a new **Web Service** from this repo:
   - **Runtime**: Python
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --workers 2 --timeout 120 --access-logfile - --error-logfile -`
3. Set environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<long-random-string>`
   - `DATABASE_URL=<Internal Connection String from step 1>`
4. Apply migrations once the service is up:
   ```bash
   # From the Render dashboard → Shell tab
   flask --app run db upgrade
   ```
5. Health check: visit `https://<service>.onrender.com/` (redirects to login).

### Production checklist
- ✅ `SECRET_KEY` set
- ✅ `DATABASE_URL` set to Postgres
- ✅ `FLASK_ENV=production`
- ✅ `SESSION_COOKIE_SECURE=True` is enforced
- ✅ HTTPS termination handled by Render

## 📁 Project Structure

```
RentHive/
├── app/
│   ├── __init__.py          # App factory + CSRF + security headers
│   ├── models.py            # SQLAlchemy models
│   ├── forms.py             # WTForms (CSRF-protected)
│   ├── utils.py             # PDF generation
│   │
│   ├── routes/
│   │   ├── auth.py          # Login / register / logout
│   │   ├── main.py          # Dashboards
│   │   ├── properties.py    # Property / room / tenant management
│   │   └── billing.py       # Bills / payments / meter readings
│   │
│   ├── services/
│   │   └── notification.py  # SMTP email
│   │
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS / JS
│
├── config.py               # Environment-driven configuration
├── run.py                  # Dev entry point (Flask CLI)
├── wsgi.py                 # Production entry point (Gunicorn)
├── requirements.txt        # Pinned dependencies
├── Procfile                # Render start command
├── runtime.txt             # Python version pin
├── render.yaml              # Render Blueprint
├── .env.example            # Environment template
├── .gitignore
├── LICENSE                 # MIT
└── README.md
```

## 🔐 Security

- **Passwords**: Werkzeug PBKDF2 hashing
- **CSRF**: Flask-WTF enabled on every form
- **Sessions**: HttpOnly + SameSite=Lax cookies; Secure flag forced in production
- **Security headers**: CSP, X-Frame-Options DENY, X-Content-Type-Options nosniff, HSTS in production
- **File uploads**: extension whitelist (`png`, `jpg`, `jpeg`, `pdf`), UUID-named files (no path traversal)
- **Open-redirect protection**: `next` URL is validated against the request host
- **Secrets**: all credentials loaded from environment; no hardcoded secrets
- **Reverse-proxy aware**: `ProxyFix` middleware trusts Render's X-Forwarded-* headers

## 📝 License

MIT — see [LICENSE](LICENSE).

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Open a Pull Request