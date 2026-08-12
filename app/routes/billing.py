"""
RentHive Billing Routes
Version: 6.0 - Security Hardened with Logging
"""
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Bill, Room, Tenant, MeterReading, Property
from app.forms import BillForm, MeterReadingForm, PaymentForm
from app.utils import generate_bill_pdf
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, date
from sqlalchemy import func

logger = logging.getLogger(__name__)

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')


@billing_bp.route('/bills')
@login_required
def list_bills():
    """List all bills"""
    if current_user.role == 'owner':
        # Owner sees all bills for their properties
        bills = Bill.query.join(Room).join(Property).filter(
            Property.owner_id == current_user.id
        ).order_by(Bill.created_at.desc()).all()
    else:
        # Tenant sees only their bills
        tenant = Tenant.query.filter_by(user_id=current_user.id).first()
        if not tenant:
            flash('Tenant profile not found.', 'warning')
            return redirect(url_for('main.dashboard'))
        bills = Bill.query.filter_by(tenant_id=tenant.id).order_by(Bill.created_at.desc()).all()
    
    return render_template('billing/list_bills.html',
                          title='Bills',
                          bills=bills)


@billing_bp.route('/bills/<int:bill_id>')
@login_required
def view_bill(bill_id):
    """View bill details"""
    bill = Bill.query.get_or_404(bill_id)
    
    # Authorization check
    if current_user.role == 'owner':
        if bill.room.property.owner_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('main.dashboard'))
    else:
        if bill.tenant.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    return render_template('billing/view_bill.html',
                          title=f'Bill {bill.bill_number}',
                          bill=bill)


@billing_bp.route('/rooms/<int:room_id>/create-bill', methods=['GET', 'POST'])
@login_required
def create_bill(room_id):
    """Create new bill for room"""
    if current_user.role != 'owner':
        flash('Access denied. Owner privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    room = Room.query.get_or_404(room_id)
    property = room.property
    
    if property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get active tenant
    tenant = Tenant.query.filter_by(room_id=room_id).first()
    if not tenant:
        flash('No tenant assigned to this room.', 'warning')
        return redirect(url_for('properties.view_room', room_id=room_id))
    
    form = BillForm()
    
    # Pre-fill rent amount
    if request.method == 'GET':
        form.rent_amount.data = room.rent_amount
        form.bill_month.data = datetime.now().strftime('%Y-%m')
        # Set due date to 5th of next month
        next_month = datetime.now().month % 12 + 1
        year = datetime.now().year if next_month > 1 else datetime.now().year + 1
        form.due_date.data = date(year, next_month, 5)
    
    if form.validate_on_submit():
        # Calculate electricity amount
        electricity_amount = 0
        if form.electricity_units.data and form.electricity_rate.data:
            electricity_amount = form.electricity_units.data * form.electricity_rate.data
        
        # Calculate total
        total_amount = (
            form.rent_amount.data +
            electricity_amount +
            (form.water_amount.data or 0) +
            (form.maintenance_amount.data or 0) +
            (form.other_charges.data or 0)
        )
        
        # Generate bill number
        bill_number = f"BILL-{datetime.now().strftime('%Y%m')}-{room_id}-{datetime.now().strftime('%d%H%M%S')}"
        
        bill = Bill(
            tenant_id=tenant.id,
            room_id=room_id,
            bill_number=bill_number,
            bill_month=form.bill_month.data,
            rent_amount=form.rent_amount.data,
            electricity_units=form.electricity_units.data or 0,
            electricity_amount=electricity_amount,
            water_amount=form.water_amount.data or 0,
            maintenance_amount=form.maintenance_amount.data or 0,
            other_charges=form.other_charges.data or 0,
            other_charges_description=form.other_charges_description.data,
            total_amount=total_amount,
            balance=total_amount,
            due_date=form.due_date.data
        )
        
        db.session.add(bill)
        db.session.commit()

        logger.info(f"Bill {bill.bill_number} created for tenant {tenant.id}, amount: {total_amount}")

        # Generate PDF
        try:
            pdf_filename = generate_bill_pdf(bill)
            bill.pdf_file = pdf_filename
            db.session.commit()
            logger.info(f"PDF generated for bill {bill.bill_number}")
        except Exception as e:
            logger.error(f"PDF generation failed for bill {bill.bill_number}: {str(e)}")
            flash(f'Bill created but PDF generation failed: {str(e)}', 'warning')
        
        flash(f'Bill {bill.bill_number} created successfully!', 'success')
        return redirect(url_for('billing.view_bill', bill_id=bill.id))
    
    return render_template('billing/create_bill.html',
                          title='Create Bill',
                          form=form,
                          room=room,
                          tenant=tenant)


@billing_bp.route('/bills/<int:bill_id>/payment', methods=['GET', 'POST'])
@login_required
def record_payment(bill_id):
    """Record payment for bill"""
    bill = Bill.query.get_or_404(bill_id)
    
    # Authorization
    if current_user.role == 'owner':
        if bill.room.property.owner_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('main.dashboard'))
    else:
        flash('Access denied. Owner privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = PaymentForm()
    
    if request.method == 'GET':
        form.amount_paid.data = bill.balance
        form.payment_date.data = date.today()
    
    if form.validate_on_submit():
        if form.amount_paid.data > bill.balance:
            flash('Payment amount cannot exceed balance.', 'danger')
        else:
            bill.amount_paid += form.amount_paid.data
            bill.balance -= form.amount_paid.data
            bill.payment_date = form.payment_date.data
            bill.payment_method = form.payment_method.data

            # Update status
            if bill.balance == 0:
                bill.status = 'paid'
            elif bill.balance < bill.total_amount:
                bill.status = 'partial'

            db.session.commit()
            logger.info(f"Payment recorded: Bill {bill.bill_number}, amount {form.amount_paid.data}, method {form.payment_method.data}")
            flash('Payment recorded successfully!', 'success')
            return redirect(url_for('billing.view_bill', bill_id=bill.id))
    
    return render_template('billing/record_payment.html',
                          title='Record Payment',
                          form=form,
                          bill=bill)


@billing_bp.route('/bills/<int:bill_id>/download')
@login_required
def download_bill(bill_id):
    """Download bill PDF"""
    bill = Bill.query.get_or_404(bill_id)
    
    # Authorization
    if current_user.role == 'owner':
        if bill.room.property.owner_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('main.dashboard'))
    else:
        if bill.tenant.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    if not bill.pdf_file or not os.path.exists(os.path.join('bills', bill.pdf_file)):
        # Generate PDF if not exists
        try:
            pdf_filename = generate_bill_pdf(bill)
            bill.pdf_file = pdf_filename
            db.session.commit()
        except Exception as e:
            flash(f'PDF generation failed: {str(e)}', 'danger')
            return redirect(url_for('billing.view_bill', bill_id=bill.id))
    
    return send_file(
        os.path.join('bills', bill.pdf_file),
        as_attachment=True,
        download_name=f'{bill.bill_number}.pdf'
    )


@billing_bp.route('/meter-readings')
@login_required
def list_meter_readings():
    """List meter readings"""
    if current_user.role == 'owner':
        readings = MeterReading.query.join(Room).join(Property).filter(
            Property.owner_id == current_user.id
        ).order_by(MeterReading.reading_date.desc()).all()
    else:
        tenant = Tenant.query.filter_by(user_id=current_user.id).first()
        if not tenant or not tenant.room_id:
            flash('No room assigned.', 'warning')
            return redirect(url_for('main.dashboard'))
        readings = MeterReading.query.filter_by(room_id=tenant.room_id).order_by(
            MeterReading.reading_date.desc()
        ).all()
    
    return render_template('billing/list_readings.html',
                          title='Meter Readings',
                          readings=readings)


@billing_bp.route('/rooms/<int:room_id>/meter-reading/add', methods=['GET', 'POST'])
@login_required
def add_meter_reading(room_id):
    """Add meter reading"""
    if current_user.role != 'owner':
        flash('Access denied. Owner privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    room = Room.query.get_or_404(room_id)
    property = room.property
    
    if property.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = MeterReadingForm()
    
    if form.validate_on_submit():
        # Calculate units and amount
        units_consumed = form.current_reading.data - form.previous_reading.data
        amount = units_consumed * form.rate_per_unit.data
        
        # Handle photo upload - secure with UUID
        photo_filename = None
        if form.photo.data:
            file = form.photo.data
            filename = secure_filename(file.filename)
            if filename:
                # Generate unique filename with UUID to prevent path traversal
                ext = os.path.splitext(filename)[1].lower()
                unique_id = uuid.uuid4().hex
                photo_filename = f"{unique_id}{ext}"
                upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), photo_filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                file.save(upload_path)
        
        reading = MeterReading(
            room_id=room_id,
            meter_type=form.meter_type.data,
            reading_date=form.reading_date.data,
            previous_reading=form.previous_reading.data,
            current_reading=form.current_reading.data,
            units_consumed=units_consumed,
            rate_per_unit=form.rate_per_unit.data,
            amount=amount,
            photo=photo_filename,
            notes=form.notes.data
        )
        
        db.session.add(reading)
        db.session.commit()
        
        flash('Meter reading added successfully!', 'success')
        return redirect(url_for('billing.list_meter_readings'))
    
    return render_template('billing/add_meter_reading.html',
                          title='Add Meter Reading',
                          form=form,
                          room=room)
