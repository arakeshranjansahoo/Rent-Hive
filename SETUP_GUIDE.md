# 🚀 RentHive Setup Guide

This guide will walk you through setting up RentHive from scratch.

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] pip package manager
- [ ] Git (optional, for cloning)
- [ ] Text editor or IDE (VS Code, PyCharm, etc.)
- [ ] Command line/terminal access

## 🔧 Detailed Setup Instructions

### Step 1: Download/Clone the Project

```bash
# Option 1: Clone with Git
git clone <repository-url>
cd RentHive

# Option 2: Download and extract ZIP
# Then navigate to the extracted folder
cd RentHive
```

### Step 2: Set Up Python Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your command prompt
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your terminal
```

### Step 3: Install Required Packages

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - Flask and extensions
# - Database tools
# - PDF generation
# - Form validation
# - And more...
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your preferred editor
# Windows: notepad .env
# macOS/Linux: nano .env
```

**Minimum required configuration:**
```env
SECRET_KEY=change-this-to-a-random-secret-key
FLASK_ENV=development
DATABASE_URL=sqlite:///renthive.db
```

**Optional email configuration (for notifications):**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 5: Initialize the Database

```bash
# Initialize database tables
python run.py init_db

# You should see: "✓ Database tables created successfully!"
```

### Step 6: Create Sample Data (Optional but Recommended)

```bash
# Create sample owner and tenant accounts
python run.py seed_db

# You should see:
# ✓ Sample users created!
#   Owner - username: owner, password: password123
#   Tenant - username: tenant, password: password123
```

### Step 7: Run the Application

```bash
python run.py

# You should see:
# * Running on http://0.0.0.0:5000
# * Debug mode: on
```

### Step 8: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## 🎯 First Steps After Setup

### 1. Login as Owner
- Username: `owner`
- Password: `password123`

### 2. Add Your First Property
1. Click "Add Property" button
2. Fill in property details:
   - Name: e.g., "Sunset Apartments"
   - Type: Select property type
   - Address: Full address
   - City, State, Pincode
   - Total Rooms: Number of rooms
3. Click "Save Property"

### 3. Add Rooms to Property
1. Navigate to your property
2. Click "Add Room"
3. Fill in room details:
   - Room Number: e.g., "101"
   - Floor: e.g., 1
   - Rent Amount: Monthly rent
   - Deposit Amount: Security deposit
   - Room Type: Select type
   - Status: Vacant/Occupied
4. Click "Save Room"

### 4. Add a Tenant
1. Navigate to a room
2. Click "Add Tenant"
3. Fill in tenant details:
   - Personal information
   - ID proof
   - Lease dates
   - Deposit paid
4. Click "Save Tenant"

### 5. Generate Your First Bill
1. Navigate to a room with tenant
2. Click "Create Bill"
3. Fill in bill details:
   - Bill month
   - Rent amount (pre-filled)
   - Electricity usage
   - Other charges
   - Due date
4. Click "Generate Bill"
5. PDF will be auto-generated!

## 🗄️ Database Options

### SQLite (Default - Development)
Already configured! No additional setup needed.

```env
DATABASE_URL=sqlite:///renthive.db
```

### PostgreSQL (Production Recommended)

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE renthive;
CREATE USER renthive_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE renthive TO renthive_user;
```

3. Update .env:
```env
DATABASE_URL=postgresql://renthive_user:your_password@localhost/renthive
```

4. Re-initialize database:
```bash
python run.py init_db
```

### MySQL (Alternative)

1. Install MySQL
2. Create database:
```sql
CREATE DATABASE renthive;
CREATE USER 'renthive_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON renthive.* TO 'renthive_user'@'localhost';
FLUSH PRIVILEGES;
```

3. Install MySQL Python connector:
```bash
pip install pymysql
```

4. Update .env:
```env
DATABASE_URL=mysql+pymysql://renthive_user:your_password@localhost/renthive
```

5. Re-initialize database:
```bash
python run.py init_db
```

## 🔧 Troubleshooting

### Issue: "Module not found" error
**Solution:** Ensure virtual environment is activated and all packages are installed
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall packages
pip install -r requirements.txt
```

### Issue: Database connection error
**Solution:** Check DATABASE_URL in .env file
```bash
# For SQLite, ensure path is correct
DATABASE_URL=sqlite:///renthive.db

# For PostgreSQL/MySQL, verify credentials
```

### Issue: Port 5000 already in use
**Solution:** Change port in run.py or kill process using port 5000
```python
# In run.py, change port:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Issue: Static files not loading
**Solution:** Clear browser cache or use hard refresh
```
Windows/Linux: Ctrl + F5
macOS: Cmd + Shift + R
```

### Issue: PDF generation fails
**Solution:** Ensure reportlab is properly installed
```bash
pip uninstall reportlab
pip install reportlab==4.0.7
```

## 📧 Email Configuration (Optional)

### Using Gmail

1. Enable 2-factor authentication on Gmail
2. Generate app password:
   - Go to Google Account → Security
   - 2-Step Verification → App passwords
   - Generate password for "Mail"

3. Update .env:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=generated-app-password
```

### Using Other Email Providers

Update MAIL_SERVER and MAIL_PORT accordingly:

**Outlook:**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
```

**Yahoo:**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
```

## 🧪 Running in Production

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

### Using nginx as Reverse Proxy

1. Install nginx
2. Configure nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/RentHive/app/static;
    }
}
```

### Environment Configuration

Update .env for production:
```env
FLASK_ENV=production
SECRET_KEY=use-a-strong-random-key-here
DATABASE_URL=postgresql://user:pass@localhost/renthive
```

## 📱 Accessing from Mobile Devices

To access from your phone on the same network:

1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   
   # macOS/Linux
   ifconfig
   ```

2. Access from mobile:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [WTForms Documentation](https://wtforms.readthedocs.io/)

## 💡 Tips for Development

1. **Keep virtual environment activated** while working
2. **Restart server** after making changes to Python files
3. **Clear browser cache** if CSS/JS changes don't appear
4. **Check console logs** for JavaScript errors
5. **Use Flask debug mode** for helpful error messages

## 📞 Need Help?

- Check README.md for feature documentation
- Review code comments for implementation details
- Open an issue on GitHub
- Contact support team

---

Happy Rental Management! 🏠
