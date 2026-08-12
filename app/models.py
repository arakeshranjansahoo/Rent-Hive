"""
RentHive Database Models
Version: 2.0
"""
from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User model for owners and tenants"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='tenant')  # 'owner' or 'tenant'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    tenant_profile = db.relationship('Tenant', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Property(db.Model):
    """Property model"""
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # 'apartment', 'house', 'pg', etc.
    total_rooms = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rooms = db.relationship('Room', backref='property', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Property {self.name}>'


class Room(db.Model):
    """Room model"""
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False, index=True)
    room_number = db.Column(db.String(50), nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    rent_amount = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # 'single', 'double', 'triple', 'studio'
    status = db.Column(db.String(20), default='vacant', index=True)  # 'vacant', 'occupied', 'maintenance'
    amenities = db.Column(db.Text, nullable=True)  # JSON or comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tenants = db.relationship('Tenant', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    meter_readings = db.relationship('MeterReading', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Room {self.room_number}>'


class Tenant(db.Model):
    """Tenant model - extended user profile"""
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True, index=True)
    id_proof_type = db.Column(db.String(50), nullable=True)  # 'aadhar', 'pan', 'passport', etc.
    id_proof_number = db.Column(db.String(100), nullable=True)
    id_proof_file = db.Column(db.String(255), nullable=True)  # File path
    emergency_contact = db.Column(db.String(15), nullable=True)
    emergency_contact_name = db.Column(db.String(120), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    move_in_date = db.Column(db.Date, nullable=True)
    move_out_date = db.Column(db.Date, nullable=True)
    lease_start = db.Column(db.Date, nullable=True)
    lease_end = db.Column(db.Date, nullable=True)
    deposit_paid = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bills = db.relationship('Bill', backref='tenant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tenant {self.user.full_name}>'


class Bill(db.Model):
    """Bill/Invoice model"""
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False, index=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    bill_month = db.Column(db.String(7), nullable=False, index=True)  # Format: YYYY-MM
    
    # Charges
    rent_amount = db.Column(db.Float, nullable=False)
    electricity_units = db.Column(db.Float, default=0.0)
    electricity_amount = db.Column(db.Float, default=0.0)
    water_amount = db.Column(db.Float, default=0.0)
    maintenance_amount = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    other_charges_description = db.Column(db.Text, nullable=True)
    
    # Totals
    total_amount = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'partial', 'paid', 'overdue'
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # 'cash', 'upi', 'bank_transfer', etc.
    
    # PDF
    pdf_file = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Bill {self.bill_number}>'


class MeterReading(db.Model):
    """Electricity/Water meter readings"""
    __tablename__ = 'meter_readings'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False, index=True)
    meter_type = db.Column(db.String(20), nullable=False, index=True)  # 'electricity', 'water'
    reading_date = db.Column(db.Date, nullable=False, index=True)
    previous_reading = db.Column(db.Float, nullable=False)
    current_reading = db.Column(db.Float, nullable=False)
    units_consumed = db.Column(db.Float, nullable=False)
    rate_per_unit = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(255), nullable=True)  # Manual photo path
    verified = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MeterReading {self.meter_type} - Room {self.room_id}>'


class Notification(db.Model):
    """Notification model for alerts and reminders"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'bill', 'payment', 'maintenance', 'general'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'
