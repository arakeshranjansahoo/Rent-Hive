"""
RentHive Main Routes (Dashboards)
Version: 4.0
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Property, Room, Tenant, Bill, MeterReading
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - role-based redirect"""
    if current_user.role == 'owner':
        return redirect(url_for('main.owner_dashboard'))
    else:
        return redirect(url_for('main.tenant_dashboard'))


@main_bp.route('/dashboard/owner')
@login_required
def owner_dashboard():
    """Owner dashboard with statistics"""
    if current_user.role != 'owner':
        flash('Access denied. Owner privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get statistics
    total_properties = Property.query.filter_by(owner_id=current_user.id).count()
    total_rooms = Room.query.join(Property).filter(Property.owner_id == current_user.id).count()
    occupied_rooms = Room.query.join(Property).filter(
        Property.owner_id == current_user.id,
        Room.status == 'occupied'
    ).count()
    
    # Revenue statistics
    current_month = datetime.now().strftime('%Y-%m')
    monthly_revenue = db.session.query(func.sum(Bill.total_amount)).join(Room).join(Property).filter(
        Property.owner_id == current_user.id,
        Bill.bill_month == current_month
    ).scalar() or 0
    
    pending_payments = db.session.query(func.sum(Bill.balance)).join(Room).join(Property).filter(
        Property.owner_id == current_user.id,
        Bill.status.in_(['pending', 'partial', 'overdue'])
    ).scalar() or 0
    
    # Recent bills
    recent_bills = Bill.query.join(Room).join(Property).filter(
        Property.owner_id == current_user.id
    ).order_by(Bill.created_at.desc()).limit(5).all()
    
    # Properties list
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    
    # Occupancy rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    stats = {
        'total_properties': total_properties,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': total_rooms - occupied_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
        'monthly_revenue': round(monthly_revenue, 2),
        'pending_payments': round(pending_payments, 2)
    }
    
    return render_template('dashboard/owner.html', 
                          title='Owner Dashboard',
                          stats=stats,
                          properties=properties,
                          recent_bills=recent_bills)


@main_bp.route('/dashboard/tenant')
@login_required
def tenant_dashboard():
    """Tenant dashboard"""
    if current_user.role != 'tenant':
        flash('Access denied. Tenant account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get tenant profile
    tenant = Tenant.query.filter_by(user_id=current_user.id).first()
    
    if not tenant:
        flash('Please complete your tenant profile.', 'warning')
        return render_template('dashboard/tenant.html', 
                             title='Tenant Dashboard',
                             tenant=None)
    
    # Get current room
    room = tenant.room if tenant.room_id else None
    
    # Get bills
    all_bills = Bill.query.filter_by(tenant_id=tenant.id).order_by(Bill.created_at.desc()).all()
    pending_bills = [b for b in all_bills if b.status in ['pending', 'partial', 'overdue']]
    paid_bills = [b for b in all_bills if b.status == 'paid']
    
    # Total pending amount
    total_pending = sum(b.balance for b in pending_bills)
    
    # Recent meter readings
    recent_readings = []
    if room:
        recent_readings = MeterReading.query.filter_by(room_id=room.id).order_by(
            MeterReading.reading_date.desc()
        ).limit(5).all()
    
    stats = {
        'total_bills': len(all_bills),
        'pending_bills': len(pending_bills),
        'paid_bills': len(paid_bills),
        'total_pending': round(total_pending, 2)
    }
    
    return render_template('dashboard/tenant.html',
                          title='Tenant Dashboard',
                          tenant=tenant,
                          room=room,
                          stats=stats,
                          pending_bills=pending_bills[:5],
                          recent_readings=recent_readings)


@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', title='My Profile')
