# RentHive Vercel Deployment Checklist

Use this checklist to ensure your deployment is successful.

## Pre-Deployment

- [ ] Repository is pushed to GitHub
- [ ] All files are committed (`git status` shows clean)
- [ ] No secrets are in `.env` file (it's in .gitignore)
- [ ] requirements.txt is up to date
- [ ] Local testing works: `python run.py`

## Database Setup

- [ ] PostgreSQL provider chosen (Supabase / Railway / Neon)
- [ ] PostgreSQL database created
- [ ] Connection string obtained (DATABASE_URL format)
- [ ] Connection tested (database is accessible)

## Vercel Configuration

### Step 1: Create Vercel Project
- [ ] Vercel account created (https://vercel.com)
- [ ] Project imported from GitHub
- [ ] Deployment completes without errors

### Step 2: Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

**REQUIRED:**
- [ ] `FLASK_ENV` = `production`
- [ ] `SECRET_KEY` = `<generated-secret>` (use `python -c "import secrets; print(secrets.token_urlsafe(48))"`)
- [ ] `DATABASE_URL` = `postgresql://...` (from your PostgreSQL provider)

**OPTIONAL (but recommended):**
- [ ] `LOG_LEVEL` = `INFO`
- [ ] `MAX_CONTENT_LENGTH` = `16777216`

### Step 3: Redeploy with Environment Variables
- [ ] Environment variables saved in Vercel
- [ ] Project redeployed (Deployments → Redeploy latest)
- [ ] Redeploy completes successfully

## Database Initialization

- [ ] Run locally: `vercel env pull`
- [ ] Run: `python deploy_init.py`
- [ ] Script completes with "✅ Database initialization complete!"
- [ ] Script shows tables created (users, properties, rooms, etc.)

## Verification

- [ ] Visit your Vercel URL: `https://<project>.vercel.app`
- [ ] Page loads (no 502 Bad Gateway)
- [ ] See login/register page
- [ ] Click "Register Now"
- [ ] Create a test account
- [ ] Click "Register"
- [ ] Account successfully created (data saved to database)
- [ ] Logout
- [ ] Login with test account
- [ ] Login successful (data persists in database)

### Advanced Verification (Optional)

- [ ] Run: `python verify_deployment.py`
- [ ] All checks pass (green checkmarks)
- [ ] Can navigate to dashboard
- [ ] Can add property (owners)
- [ ] Can view bills (tenants)

## Post-Deployment

- [ ] Set up custom domain (optional)
- [ ] Configure database backups with provider
- [ ] Set up Vercel deployment notifications
- [ ] Share Vercel URL with users
- [ ] Monitor first 24 hours in Vercel Analytics
- [ ] Document deployment URL and credentials

## Troubleshooting

If something fails, check:

1. **Vercel Deployment Logs**
   - Dashboard → Deployments → Click failed deployment → Logs
   - Look for error messages

2. **Missing Environment Variables**
   ```bash
   Error: SECRET_KEY must be set
   Fix: Add SECRET_KEY in Vercel environment variables
   ```

3. **Database Connection Failed**
   ```bash
   Error: could not translate host name "..." to address
   Fix: Verify DATABASE_URL is correct
   ```

4. **No Tables Found**
   ```bash
   Error: (sqlite3.OperationalError) no such table: users
   Fix: Run python deploy_init.py
   ```

5. **502 Bad Gateway**
   - Check Vercel logs for error details
   - Verify all environment variables are set
   - Redeploy after fixing variables

## Support Resources

- Vercel Docs: https://vercel.com/docs/frameworks/flask
- Flask Docs: https://flask.palletsprojects.com
- PostgreSQL Providers:
  - Supabase: https://supabase.com/docs
  - Railway: https://docs.railway.app
  - Neon: https://neon.tech/docs
- RentHive Docs: See VERCEL_DEPLOYMENT.md

---

**Status:** ✅ Ready for Deployment  
**Date Prepared:** 2026-08-13  
**Framework:** Flask + SQLAlchemy  
**Database:** PostgreSQL  
**Hosting:** Vercel Serverless Functions
