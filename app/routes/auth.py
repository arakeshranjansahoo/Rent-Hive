"""
RentHive Authentication Routes
Version: 7.0 - Security Enhanced with Logging and Open-Redirect Protection
"""
import logging
from urllib.parse import urlparse, urljoin

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user

from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _is_safe_url(target: str) -> bool:
    """Validate `next` URL to prevent open-redirect attacks."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            logger.info("User %s logged in successfully", user.username)
            flash(f'Welcome back, {user.full_name}!', 'success')

            # Safely redirect to `next` if it's a local URL
            next_page = request.args.get('next')
            if next_page and _is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            logger.warning("Failed login attempt for username: %s", form.username.data)
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form, title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        logger.info("New user registered: %s", user.username)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Register')


@auth_bp.route('/logout')
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

