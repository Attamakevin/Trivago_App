# hotel_app/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from hotel_app import app, db
from hotel_app.models import User, Hotel, Reservation, DepositRequest, WithdrawalRequest, EventAd
from datetime import datetime

@app.route('/')
def home():
    return render_template('home.html')
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from hotel_app import db
from hotel_app.models import User, InvitationCode  # ✅ Only import User now


import random

def generate_captcha():
    """Generate a new captcha code and store it in session"""
    captcha_code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=5))
    session['captcha_code'] = captcha_code
    return captcha_code

# GET routes - display forms
@app.route('/auth')
@app.route('/login', endpoint = 'login')
@app.route('/register', endpoint = 'register')
def auth():
    if request.endpoint == 'register' or request.path == '/register':
        captcha = generate_captcha()
        return render_template('auth.html', form_type='register', captcha=captcha)
    else:
        return render_template('auth.html', form_type='login')

# POST routes - handle form submissions
@app.route('/login', methods=['POST'])
def login_post():
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    if not phone or not password:
        flash('Phone number and password are required', 'error')
        return redirect(url_for('auth'))
    
    user = User.query.filter_by(contact=phone).first()
    if user and check_password_hash(user.password_hash, password):
        if not user.is_active:
            flash('Account not yet activated by admin', 'warning')
            return redirect(url_for('auth'))

        session['user_id'] = user.id
        session['language'] = request.form.get('language', 'en')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid phone number or password', 'error')
        return redirect(url_for('auth'))

@app.route('/register', methods=['POST'])
def register_post():
    phone = request.form.get('phone')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    captcha = request.form.get('captcha')
    invitation_code = request.form.get('invitation_code')
    
    # Basic validation
    if not all([phone, password, confirm_password, captcha, invitation_code]):
        flash('All fields are required', 'error')
        return redirect(url_for('register'))
    
    # Captcha check
    if captcha.strip().upper() != session.get('captcha_code', '').upper():
        flash('Invalid captcha code', 'error')
        return redirect(url_for('register'))

    # Password match check
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('register'))

    # Duplicate phone check
    if User.query.filter_by(contact=phone).first():
        flash('Phone number already registered', 'error')
        return redirect(url_for('register'))
    
    # Validate invitation code
    code_entry = InvitationCode.query.filter_by(code=invitation_code, is_used=False).first()
    if not code_entry:
        flash('Invalid or already used invitation code', 'error')
        return redirect(url_for('register'))

    try:
        # Mark invitation code as used
        code_entry.is_used = True
        
        # Create new user with inactive status
        new_user = User(
            contact=phone,
            password_hash=generate_password_hash(password),
            is_active=False,
            invitation_code=invitation_code
        )
        db.session.add(new_user)
        db.session.commit()

        # Clear captcha from session after successful registration
        session.pop('captcha_code', None)
        
        flash('Registration successful! Your account will be activated by the admin.', 'success')
        return redirect(url_for('auth'))  # Redirect to login form
    
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('register'))

@app.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.all()
    return render_template('dashboard.html', hotels=hotels, user=user)

@app.route('/events')
def events():
    ads = EventAd.query.all()
    return render_template('events.html', ads=ads)

@app.route('/credit')
def credit():
    user = User.query.get(session['user_id'])
    return render_template('credit.html', user=user)

@app.route('/reservations')
def reservations():
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.all()
    return render_template('reservations.html', hotels=hotels, user=user)

@app.route('/reserve/<int:hotel_id>', methods=['POST'])
def reserve(hotel_id):
    user = User.query.get(session['user_id'])
    hotel = Hotel.query.get(hotel_id)

    # Enforce daily limit
    today_reservations = Reservation.query.filter_by(user_id=user.id).filter(
        Reservation.timestamp >= datetime.utcnow().date()).count()
    limit = {'VIP0': 5, 'VIP1': 10, 'VIP2': 15}.get(user.vip_level, 5)

    if today_reservations >= limit:
        return jsonify({'error': 'Daily reservation limit reached'}), 403

    commission = 0.02 * hotel.price * hotel.commission_multiplier
    reservation = Reservation(
        user_id=user.id,
        hotel_id=hotel.id,
        order_number=f"ORD{user.id}{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        commission_earned=commission
    )
    db.session.add(reservation)
    db.session.commit()
    return redirect(url_for('reservations'))

@app.route('/rate/<int:reservation_id>', methods=['POST'])
def rate(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    reservation.rating = request.form['rating']
    reservation.feedback = request.form['feedback']
    user = reservation.user
    user.balance += reservation.commission_earned
    db.session.commit()
    return redirect(url_for('reservations'))

@app.route('/order-history')
def order_history():
    user = User.query.get(session['user_id'])
    all_orders = Reservation.query.filter_by(user_id=user.id).all()
    processing = [r for r in all_orders if r.status == 'Processing']
    completed = [r for r in all_orders if r.status == 'Completed']
    return render_template('order_history.html', all_orders=all_orders, processing=processing, completed=completed)

@app.route('/profile')
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        amount = float(request.form['amount'])
        network = request.form['network']
        deposit = DepositRequest(user_id=user.id, amount=amount, network=network)
        db.session.add(deposit)
        db.session.commit()
        return redirect('https://t.me/your_admin_telegram')
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        amount = float(request.form['amount'])
        network = request.form['network']
        wallet_address = request.form['wallet']
        if not user.withdrawal_password:
            return redirect(url_for('set_withdrawal_password'))
        withdrawal = WithdrawalRequest(user_id=user.id, amount=amount, network=network, wallet_address=wallet_address)
        db.session.add(withdrawal)
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('withdraw.html')

@app.route('/set-withdrawal-password', methods=['GET', 'POST'])
def set_withdrawal_password():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.withdrawal_password = request.form['password']
        db.session.commit()
        return redirect(url_for('withdraw'))
    return render_template('set_password.html')
from functools import wraps
from flask import redirect, url_for, flash, session

from flask_login import current_user
import string
import random
from datetime import datetime


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = User.query.get(session.get('user_id'))
        if not user or user.user_id != 'ADMIN1':  # Replace 'ADMIN1' with actual admin user_id
            flash("Admin access required.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/admin/users')
@admin_required
def view_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User {'activated' if user.is_active else 'deactivated'}", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/withdrawals')
@admin_required
def view_withdrawals():
    withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.id.desc()).all()
    return render_template('admin_withdrawals.html', withdrawals=withdrawals)

@app.route('/admin/deposits')
@admin_required
def view_deposits():
    deposits = DepositRequest.query.order_by(DepositRequest.id.desc()).all()
    return render_template('admin_deposits.html', deposits=deposits)
@app.route('/admin/hotels', methods=['GET', 'POST'])
@admin_required
def manage_hotels():
    if request.method == 'POST':
        name = request.form['name']
        primary_picture = request.form['primary_picture']
        price = float(request.form['price'])
        commission_multiplier = float(request.form.get('commission_multiplier', 1.0))
        days_available = int(request.form.get('days_available', 1))

        new_hotel = Hotel(
            name=name,
            primary_picture=primary_picture,
            price=price,
            commission_multiplier=commission_multiplier,
            days_available=days_available
        )
        db.session.add(new_hotel)
        db.session.commit()
        flash('Hotel added successfully', 'success')
        return redirect(url_for('manage_hotels'))

    hotels = Hotel.query.all()
    return render_template('admin_hotels.html', hotels=hotels)

import string, random

def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/admin/generate-invite', methods=['GET', 'POST'])
@admin_required
def generate_invitation_code():
    if request.method == 'POST':
        num_codes = int(request.form.get('num_codes', 1))
        codes = []

        for _ in range(num_codes):
            code = generate_random_code()
            while InvitationCode.query.filter_by(code=code).first():
                code = generate_random_code()

            invite = InvitationCode(code=code)
            db.session.add(invite)
            codes.append(code)

        db.session.commit()
        flash(f'{len(codes)} code(s) generated.', 'success')
        return render_template('admin_invite.html', codes=codes)

    return render_template('admin_invite.html')
