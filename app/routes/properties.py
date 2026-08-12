"""
RentHive Properties Routes
Version: 7.0 - Security Hardened with Logging
"""
import logging
import os
import secrets
import string
import uuid
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Property, Room, Tenant, User
from app.forms import PropertyForm, RoomForm, TenantForm

logger = logging.getLogger(__name__)

properties_bp = Blueprint('properties', __name__, url_prefix='/properties')


@properties_bp.route('/')
@login_required
def list_properties():
    """List all properties (owner only)"""
    if current_user.role != 'owner':
        flash('Access denied. Owner privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('property/list_properties.html', 
                          title='My Properties',
                          properties=properties)


@properties_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_property():
    """Add new property"""
    if current_user.role != 'owner':
        flash('Access denied. Owner privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            owner_id=current_user.id,
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            pincode=form.pincode.data,
            property_type=form.property_type.data,
            total_rooms=form.total_rooms.data
        )
        db.session.add(property)
        db.session.commit()

        logger.info(f"Property created: {property.name} (ID: {property.id}) by owner {current_user.id}")

        flash(f'Property "{property.name}" added successfully!', 'success')
        return redirect(url_for('properties.view_property', property_id=property.id))
    
    return render_template('property/add_property.html', 
                          title='Add Property',
                          form=form)


@properties_bp.route('/<int:property_id>')
@login_required
def view_property(property_id):
    """View property details"""
    property = Property.query.get_or_404(property_id)
    
    if current_user.role == 'owner' and property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    rooms = Room.query.filter_by(property_id=property_id).all()
    
    # Statistics
    total_rooms = len(rooms)
    occupied = len([r for r in rooms if r.status == 'occupied'])
    vacant = len([r for r in rooms if r.status == 'vacant'])
    
    return render_template('property/view_property.html',
                          title=property.name,
                          property=property,
                          rooms=rooms,
                          stats={'total': total_rooms, 'occupied': occupied, 'vacant': vacant})


@properties_bp.route('/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    """Edit property"""
    property = Property.query.get_or_404(property_id)
    
    if current_user.role != 'owner' or property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = PropertyForm(obj=property)
    if form.validate_on_submit():
        property.name = form.name.data
        property.address = form.address.data
        property.city = form.city.data
        property.state = form.state.data
        property.pincode = form.pincode.data
        property.property_type = form.property_type.data
        property.total_rooms = form.total_rooms.data
        
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('properties.view_property', property_id=property.id))
    
    return render_template('property/edit_property.html',
                          title='Edit Property',
                          form=form,
                          property=property)


@properties_bp.route('/<int:property_id>/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room(property_id):
    """Add room to property"""
    property = Property.query.get_or_404(property_id)
    
    if current_user.role != 'owner' or property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            property_id=property_id,
            room_number=form.room_number.data,
            floor=form.floor.data,
            rent_amount=form.rent_amount.data,
            deposit_amount=form.deposit_amount.data,
            room_type=form.room_type.data,
            status=form.status.data,
            amenities=form.amenities.data
        )
        db.session.add(room)
        db.session.commit()
        
        flash(f'Room {room.room_number} added successfully!', 'success')
        return redirect(url_for('properties.view_property', property_id=property_id))
    
    return render_template('property/add_room.html',
                          title='Add Room',
                          form=form,
                          property=property)


@properties_bp.route('/rooms/<int:room_id>')
@login_required
def view_room(room_id):
    """View room details"""
    room = Room.query.get_or_404(room_id)
    property = room.property
    
    if current_user.role == 'owner' and property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    tenants = Tenant.query.filter_by(room_id=room_id).all()
    
    return render_template('property/room_details.html',
                          title=f'Room {room.room_number}',
                          room=room,
                          property=property,
                          tenants=tenants)


@properties_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    """Edit room"""
    room = Room.query.get_or_404(room_id)
    property = room.property
    
    if current_user.role != 'owner' or property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = RoomForm(obj=room)
    if form.validate_on_submit():
        room.room_number = form.room_number.data
        room.floor = form.floor.data
        room.rent_amount = form.rent_amount.data
        room.deposit_amount = form.deposit_amount.data
        room.room_type = form.room_type.data
        room.status = form.status.data
        room.amenities = form.amenities.data
        
        db.session.commit()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('properties.view_room', room_id=room.id))
    
    return render_template('property/edit_room.html',
                          title='Edit Room',
                          form=form,
                          room=room,
                          property=property)


@properties_bp.route('/rooms/<int:room_id>/tenants/add', methods=['GET', 'POST'])
@login_required
def add_tenant(room_id):
    """Add tenant to room"""
    room = Room.query.get_or_404(room_id)
    property = room.property
    
    if current_user.role != 'owner' or property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = TenantForm()
    if form.validate_on_submit():
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash(f'A user with email "{form.email.data}" already exists. Please use a different email or contact the administrator.', 'warning')
            return render_template('property/add_tenant.html',
                                  title='Add Tenant',
                                  form=form,
                                  room=room,
                                  property=property)
        
        # Create user account for tenant
        # Generate a random, one-time password — owner should share it securely
        alphabet = string.ascii_letters + string.digits
        temporary_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        user = User(
            username=form.email.data.split('@')[0],
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data,
            role='tenant',
        )
        user.set_password(temporary_password)
        db.session.add(user)
        db.session.flush()
        
        # Handle file upload - secure with UUID
        id_proof_filename = None
        if form.id_proof_file.data:
            file = form.id_proof_file.data
            filename = secure_filename(file.filename)
            if filename:
                # Generate unique filename with UUID to prevent path traversal
                ext = os.path.splitext(filename)[1].lower()
                unique_id = uuid.uuid4().hex
                id_proof_filename = f"{unique_id}{ext}"
                upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), id_proof_filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                file.save(upload_path)
        
        # Create tenant profile
        tenant = Tenant(
            user_id=user.id,
            room_id=room_id,
            id_proof_type=form.id_proof_type.data,
            id_proof_number=form.id_proof_number.data,
            id_proof_file=id_proof_filename,
            emergency_contact=form.emergency_contact.data,
            emergency_contact_name=form.emergency_contact_name.data,
            occupation=form.occupation.data,
            move_in_date=form.move_in_date.data,
            lease_start=form.lease_start.data,
            lease_end=form.lease_end.data,
            deposit_paid=form.deposit_paid.data
        )
        db.session.add(tenant)
        
        # Update room status
        room.status = 'occupied'
        
        db.session.commit()
        
        flash(
            f'Tenant {user.full_name} added successfully! '
            f'Username: {user.username}. Share the temporary password securely with the tenant.',
            'success',
        )
        return redirect(url_for('properties.view_room', room_id=room_id))
    
    return render_template('property/add_tenant.html',
                          title='Add Tenant',
                          form=form,
                          room=room,
                          property=property)
