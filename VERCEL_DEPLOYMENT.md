# RentHive Vercel Deployment Guide

> **Complete instructions for deploying RentHive to Vercel with PostgreSQL database**

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Prepare Your Repository](#step-1-prepare-your-repository)
3. [Step 2: Set Up PostgreSQL Database](#step-2-set-up-postgresql-database)
4. [Step 3: Deploy to Vercel](#step-3-deploy-to-vercel)
5. [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
6. [Step 5: Initialize Database](#step-5-initialize-database)
7. [Step 6: Verify Deployment](#step-6-verify-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- GitHub account with the RentHive repository
- Vercel account (free at https://vercel.com)
- PostgreSQL database (Supabase, Railway, or Neon - all have free tiers)
- Node.js and npm installed locally (for Vercel CLI)

---

## Step 1: Prepare Your Repository

The deployment files are already included:

```
RentHive/
├── vercel.json              # Vercel configuration ✅
├── api/
│   └── index.py            # Serverless entry point ✅
├── deploy_init.py          # Database initialization script ✅
├── wsgi.py                 # WSGI entry point (for reference)
├── config.py               # Config with production settings ✅
├── requirements.txt        # All dependencies ✅
└── runtime.txt             # Python version ✅
```

**If using GitHub:**
```bash
# Push changes to GitHub
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

---

## Step 2: Set Up PostgreSQL Database

Choose **ONE** of these options (all have free tiers):

### Option A: Supabase (Recommended for beginners)
1. Go to https://supabase.com
2. Click "Start your project"
3. Create a new project
4. Go to Project Settings → Database
5. Copy the "Connection string" (looks like: `postgresql://...`)
6. Keep this for Step 4

### Option B: Railway.app
1. Go to https://railway.app
2. Create new project → PostgreSQL
3. Go to PostgreSQL plugin → Connect tab
4. Copy the PostgreSQL connection string
5. Keep this for Step 4

### Option C: Neon (Free tier with 500MB)
1. Go to https://neon.tech
2. Sign up and create a project
3. Go to Connection details
4. Copy the "Connection string"
5. Keep this for Step 4

---

## Step 3: Deploy to Vercel

### Option A: Using Vercel Web Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Select "Import Git Repository"
4. Paste your GitHub repository URL
5. Click "Import"
6. Configure project:
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `.`
   - Click "Deploy"

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to RentHive directory
cd RentHive

# Deploy
vercel --prod
```

**Note:** After deployment, you'll get a URL like: `https://renthive-abc123.vercel.app`

---

## Step 4: Configure Environment Variables

### In Vercel Dashboard:

1. Go to your Vercel project
2. Click "Settings" → "Environment Variables"
3. Add the following variables:

#### REQUIRED Variables:

**`FLASK_ENV`**
```
Value: production
```

**`SECRET_KEY`**
```
# Generate using Python:
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Copy the generated string and paste it
Value: <paste-generated-key-here>
```

**`DATABASE_URL`**
```
# From your PostgreSQL provider (Supabase/Railway/Neon)
Value: postgresql://username:password@host:port/database
```

#### OPTIONAL Variables:

**`LOG_LEVEL`** (default: INFO)
```
Value: INFO
```

**`MAX_CONTENT_LENGTH`** (default: 16MB)
```
Value: 16777216
```

**Email Settings** (for notifications, optional):
```
MAIL_SERVER: smtp.gmail.com
MAIL_PORT: 587
MAIL_USE_TLS: True
MAIL_USERNAME: your-email@gmail.com
MAIL_PASSWORD: your-app-password
```

### Important: Save and Redeploy

1. After adding variables, click "Save"
2. Go to "Deployments"
3. Click the latest deployment menu → "Redeploy"
4. This will rebuild with the new environment variables

---

## Step 5: Initialize Database

After the redeploy completes, initialize the database:

### Using Vercel CLI:

```bash
# Set environment variables locally
vercel env pull

# Run initialization script
python deploy_init.py
```

### Or Using GitHub Workflow (Recommended):

Create `.github/workflows/init-db.yml`:

```yaml
name: Initialize Production Database
on:
  workflow_dispatch:  # Manual trigger

jobs:
  init-db:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - env:
          FLASK_ENV: production
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python deploy_init.py
```

Then trigger via GitHub Actions tab.

---

## Step 6: Verify Deployment

### Test the Application:

1. Open your Vercel app URL: `https://renthive-abc123.vercel.app`
2. You should see the RentHive login page
3. Click "Register Now" to create an account
4. Enter a username, email, password
5. Choose role (Owner or Tenant)
6. Click "Register"

### If Registration Works:
✅ **Database is connected and working!**

### Verify Database Data Persists:

1. Logout
2. Try to login with the account you just created
3. Should succeed (proves data was saved to PostgreSQL)

---

## Troubleshooting

### Issue: "502 Bad Gateway" or blank page

**Solution:**
1. Check Vercel deployment logs:
   - Dashboard → Deployments → Click deployment → "Logs"
2. Look for "SECRET_KEY must be set" or "DATABASE_URL must be set"
3. Add missing environment variables and redeploy

### Issue: "no such table: users" error

**Solution:**
The database tables haven't been initialized. Run:
```bash
vercel env pull
python deploy_init.py
```

### Issue: Database connection timeout

**Solution:**
1. Verify DATABASE_URL is correct
2. Check PostgreSQL provider (Supabase/Railway) - database should be running
3. Verify IP whitelist if your provider has one
4. For Supabase: Go to Settings → Network → Check that it allows all IPs

### Issue: "CSRF token missing" on form submission

**Solution:**
This usually means the SECRET_KEY changed. Ensure:
1. SECRET_KEY is set in Vercel environment variables
2. It's consistent across deployments
3. Clear browser cache and cookies
4. Try in incognito mode

### Issue: File uploads not working

**Solution:**
Vercel's serverless functions have ephemeral storage. Files uploaded during a request are lost.
To fix, you need:
1. Configure cloud storage (AWS S3, Supabase Storage, or similar)
2. Update app code to use cloud storage instead of local filesystem

For now, uploads will work within a single request but won't persist.

---

## Post-Deployment

### Enable Custom Domain (Optional):

1. Vercel Dashboard → Project Settings → Domains
2. Click "Add" and follow the instructions
3. Point your domain's DNS to Vercel

### Set Up Database Backups:

Ask your PostgreSQL provider (Supabase/Railway) about automated backups.

### Monitor Application:

1. Vercel Dashboard → Analytics tab
2. Track request counts, errors, response times
3. Set up email alerts for deployment failures

### Auto-Redeploy on Git Push:

Vercel automatically redeploys when you push to GitHub. No additional setup needed!

---

## Security Checklist

- ✅ Never commit `.env` file to Git
- ✅ Use strong SECRET_KEY (generate with `secrets.token_urlsafe(48)`)
- ✅ DATABASE_URL contains password - keep it secret (only in Vercel env vars)
- ✅ FLASK_ENV is set to 'production'
- ✅ Vercel has "Preview Deployments" disabled for main branch (optional security)
- ✅ All database traffic uses HTTPS

---

## Next Steps

After successful deployment:

1. **Share your app**: Give users the Vercel URL
2. **Monitor**: Check Vercel Analytics for issues
3. **Backup**: Set up database backups with your PostgreSQL provider
4. **Scale**: Upgrade to paid PostgreSQL plan if you outgrow free tier
5. **Features**: Add email/SMS notifications, advanced billing features, etc.

---

## Support

For Vercel-specific issues: https://vercel.com/docs/frameworks/flask

For RentHive issues: Check the main README.md and project documentation
