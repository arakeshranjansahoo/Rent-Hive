"""
RentHive Forms
Version: 6.0 - Security Enhanced Validation
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, FloatField, IntegerField, DateField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange, Regexp, InputRequired
from wtforms.fields import DateField as WTFormsDateField
from app.models import User
import re


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=120),
        Regexp(r'^[a-zA-Z\s\'-]+$', message='Name can only contain letters, spaces, hyphens, and apostrophes')
    ])
    phone = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^\+?[0-9\s\-]+$', message='Invalid phone number format')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=128)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    role = SelectField('Role', choices=[
        ('owner', 'Property Owner'),
        ('tenant', 'Tenant')
    ], validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class PropertyForm(FlaskForm):
    """Property creation/edit form"""
    name = StringField('Property Name', validators=[
        DataRequired(),
        Length(min=2, max=200),
        Regexp(r'^[a-zA-Z0-9\s\-\'\.,]+$', message='Invalid property name')
    ])
    address = TextAreaField('Address', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ])
    city = StringField('City', validators=[
        DataRequired(),
        Length(min=2, max=100),
        Regexp(r'^[a-zA-Z\s\-]+$', message='Invalid city name')
    ])
    state = StringField('State', validators=[
        DataRequired(),
        Length(min=2, max=100),
        Regexp(r'^[a-zA-Z\s\-]+$', message='Invalid state name')
    ])
    pincode = StringField('Pincode', validators=[
        DataRequired(),
        Length(min=5, max=10),
        Regexp(r'^[0-9]+$', message='Invalid pincode')
    ])
    property_type = SelectField('Property Type',
                                choices=[
                                    ('apartment', 'Apartment'),
                                    ('house', 'Independent House'),
                                    ('pg', 'PG/Hostel'),
                                    ('commercial', 'Commercial')
                                ],
                                validators=[DataRequired()])
    total_rooms = IntegerField('Total Rooms', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000)
    ])
    submit = SubmitField('Save Property')


class RoomForm(FlaskForm):
    """Room creation/edit form"""
    room_number = StringField('Room Number', validators=[
        DataRequired(),
        Length(min=1, max=50),
        Regexp(r'^[a-zA-Z0-9\-]+$', message='Room number can only contain letters, numbers, and hyphens')
    ])
    floor = IntegerField('Floor', validators=[Optional(), NumberRange(min=0, max=100)])
    rent_amount = FloatField('Monthly Rent', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000000)
    ])
    deposit_amount = FloatField('Security Deposit', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000000)
    ])
    room_type = SelectField('Room Type',
                           choices=[
                               ('single', 'Single Occupancy'),
                               ('double', 'Double Occupancy'),
                               ('triple', 'Triple Occupancy'),
                               ('studio', 'Studio Apartment')
                           ],
                           validators=[DataRequired()])
    status = SelectField('Status',
                        choices=[
                            ('vacant', 'Vacant'),
                            ('occupied', 'Occupied'),
                            ('maintenance', 'Under Maintenance')
                        ],
                        validators=[DataRequired()])
    amenities = TextAreaField('Amenities (comma separated)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Room')


class TenantForm(FlaskForm):
    """Tenant profile form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=120),
        Regexp(r'^[a-zA-Z\s\'-]+$', message='Name can only contain letters, spaces, hyphens, and apostrophes')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    phone = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^\+?[0-9\s\-]+$', message='Invalid phone number format')
    ])
    id_proof_type = SelectField('ID Proof Type',
                               choices=[
                                   ('aadhar', 'Aadhar Card'),
                                   ('pan', 'PAN Card'),
                                   ('passport', 'Passport'),
                                   ('driving_license', 'Driving License'),
                                   ('voter_id', 'Voter ID')
                               ],
                               validators=[DataRequired()])
    id_proof_number = StringField('ID Proof Number', validators=[
        DataRequired(),
        Length(min=3, max=100),
        Regexp(r'^[a-zA-Z0-9\s\-]+$', message='Invalid ID number format')
    ])
    id_proof_file = FileField('Upload ID Proof', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDFs only!')
    ])
    emergency_contact = StringField('Emergency Contact', validators=[
        Optional(),
        Length(min=10, max=15),
        Regexp(r'^\+?[0-9\s\-]+$', message='Invalid phone number format')
    ])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[
        Optional(),
        Length(max=120),
        Regexp(r'^[a-zA-Z\s\'-]*$', message='Invalid name format')
    ])
    occupation = StringField('Occupation', validators=[
        Optional(),
        Length(max=100),
        Regexp(r'^[a-zA-Z\s\-]+$', message='Invalid occupation format')
    ])
    move_in_date = DateField('Move-in Date', validators=[Optional()])
    lease_start = DateField('Lease Start Date', validators=[DataRequired()])
    lease_end = DateField('Lease End Date', validators=[DataRequired()])
    deposit_paid = FloatField('Deposit Paid', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000000)
    ])


class BillForm(FlaskForm):
    """Bill creation form"""
    bill_month = StringField('Bill Month (YYYY-MM)', validators=[
        DataRequired(),
        Length(min=7, max=7),
        Regexp(r'^\d{4}-(0[1-9]|1[0-2])$', message='Invalid bill month format (use YYYY-MM)')
    ])
    rent_amount = FloatField('Rent Amount', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000000)
    ])
    electricity_units = FloatField('Electricity Units', validators=[
        Optional(),
        NumberRange(min=0, max=100000)
    ])
    electricity_rate = FloatField('Rate per Unit', validators=[
        Optional(),
        NumberRange(min=0, max=100)
    ])
    water_amount = FloatField('Water Charges', validators=[
        Optional(),
        NumberRange(min=0, max=100000)
    ])
    maintenance_amount = FloatField('Maintenance Charges', validators=[
        Optional(),
        NumberRange(min=0, max=100000)
    ])
    other_charges = FloatField('Other Charges', validators=[
        Optional(),
        NumberRange(min=0, max=100000)
    ])
    other_charges_description = TextAreaField('Other Charges Description', validators=[
        Optional(),
        Length(max=500)
    ])
    due_date = DateField('Due Date', validators=[DataRequired()])


class MeterReadingForm(FlaskForm):
    """Meter reading form"""
    meter_type = SelectField('Meter Type',
                            choices=[
                                ('electricity', 'Electricity'),
                                ('water', 'Water')
                            ],
                            validators=[DataRequired()])
    reading_date = DateField('Reading Date', validators=[DataRequired()])
    previous_reading = FloatField('Previous Reading', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000000)
    ])
    current_reading = FloatField('Current Reading', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000000)
    ])
    rate_per_unit = FloatField('Rate per Unit', validators=[
        DataRequired(),
        NumberRange(min=0, max=100)
    ])
    photo = FileField('Meter Photo (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

    def validate_current_reading(self, current_reading):
        if self.previous_reading.data is not None and current_reading.data < self.previous_reading.data:
            raise ValidationError('Current reading cannot be less than previous reading.')


class PaymentForm(FlaskForm):
    """Payment recording form"""
    amount_paid = FloatField('Amount Paid', validators=[
        DataRequired(),
        NumberRange(min=0.01, max=1000000)
    ])
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method',
                                choices=[
                                    ('cash', 'Cash'),
                                    ('upi', 'UPI'),
                                    ('bank_transfer', 'Bank Transfer'),
                                    ('cheque', 'Cheque'),
                                    ('card', 'Card')
                                ],
                                validators=[DataRequired()])
