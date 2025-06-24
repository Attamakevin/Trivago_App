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
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        amount = float(request.form['amount'])
        network = request.form['network']
        deposit = DepositRequest(user_id=user.id, amount=amount, network=network)
        db.session.add(deposit)
        db.session.commit()
        # return redirect('https://t.me/your_admin_telegram')
    return render_template('deposit.html', user=user)

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
    return render_template('withdraw.html', user=user)

@app.route('/set-withdrawal-password', methods=['GET', 'POST'])
def set_withdrawal_password():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.withdrawal_password = request.form['password']
        db.session.commit()
        return redirect(url_for('withdraw'))
    return render_template('set_password.html')

from functools import wraps
from flask import session, flash, redirect, url_for, request, render_template
import string
import random
from hotel_app.models import Admin
# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id:
            flash("Admin login required.", "danger")
            return redirect(url_for('admin_login'))
        
        admin = Admin.query.get(admin_id)
        if not admin or not admin.is_active:
            session.pop('admin_id', None)
            flash("Admin access denied.", "danger")
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return wrapper

# Separate admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password) and admin.is_active:
            session['admin_id'] = admin.id
            admin.last_login = datetime.utcnow()
            db.session.commit()
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'danger')
    
    return render_template('admin_login.html')

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Admin logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get statistics for dashboard
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_deposits = DepositRequest.query.count()
    pending_deposits = DepositRequest.query.filter_by(status='pending').count()
    total_withdrawals = WithdrawalRequest.query.count()
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    total_hotels = Hotel.query.count()
    total_bookings = Booking.query.count() if 'Booking' in globals() else 0
    
    # Recent activities
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_deposits = DepositRequest.query.order_by(DepositRequest.id.desc()).limit(5).all()
    recent_withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.id.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_deposits': total_deposits,
        'pending_deposits': pending_deposits,
        'total_withdrawals': total_withdrawals,
        'pending_withdrawals': pending_withdrawals,
        'total_hotels': total_hotels,
        'total_bookings': total_bookings,
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         recent_users=recent_users,
                         recent_deposits=recent_deposits,
                         recent_withdrawals=recent_withdrawals)

# User Management
@app.route('/admin/users')
@admin_required
def view_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    users_query = User.query
    if search:
        users_query = users_query.filter(
            User.nickname.contains(search) | 
            User.user.agent_id.contains(search)
        )
    
    users = users_query.order_by(User.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_users.html', users=users, search=search)

@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'activated' if user.is_active else 'deactivated'
    flash(f"User {user.nickname} has been {action}.", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    username = user.nickname
    
    # You might want to handle related records (deposits, withdrawals, etc.)
    # before deleting the user
    
    db.session.delete(user)
    db.session.commit()
    flash(f"User {username} has been deleted.", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/users/<int:user_id>/view')
@admin_required
def view_user_details(user_id):
    user = User.query.get_or_404(user_id)
    deposits = DepositRequest.query.filter_by(user_id=user_id).order_by(DepositRequest.id.desc()).all()
    withdrawals = WithdrawalRequest.query.filter_by(user_id=user_id).order_by(WithdrawalRequest.id.desc()).all()
    
    return render_template('admin_user_details.html', 
                         user=user, 
                         deposits=deposits, 
                         withdrawals=withdrawals)

# Deposit Management
@app.route('/admin/deposits')
@admin_required
def view_deposits():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    deposits_query = DepositRequest.query
    if status_filter:
        deposits_query = deposits_query.filter_by(status=status_filter)
    
    deposits = deposits_query.order_by(DepositRequest.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_deposits.html', deposits=deposits, status_filter=status_filter)

@app.route('/admin/deposits/<int:deposit_id>/approve', methods=['POST'])
@admin_required
def approve_deposit(deposit_id):
    deposit = DepositRequest.query.get_or_404(deposit_id)
    
    if deposit.status == 'pending':
        deposit.status = 'approved'
        # Update user balance
        user = User.query.get(deposit.user_id)
        user.balance += deposit.amount
        
        db.session.commit()
        flash(f"Deposit of ${deposit.amount} approved for user {user.username}.", "success")
    else:
        flash("Deposit has already been processed.", "warning")
    
    return redirect(url_for('view_deposits'))

@app.route('/admin/deposits/<int:deposit_id>/reject', methods=['POST'])
@admin_required
def reject_deposit(deposit_id):
    deposit = DepositRequest.query.get_or_404(deposit_id)
    
    if deposit.status == 'pending':
        deposit.status = 'rejected'
        db.session.commit()
        flash(f"Deposit of ${deposit.amount} rejected.", "success")
    else:
        flash("Deposit has already been processed.", "warning")
    
    return redirect(url_for('view_deposits'))

# Withdrawal Management
@app.route('/admin/withdrawals')
@admin_required
def view_withdrawals():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    withdrawals_query = WithdrawalRequest.query
    if status_filter:
        withdrawals_query = withdrawals_query.filter_by(status=status_filter)
    
    withdrawals = withdrawals_query.order_by(WithdrawalRequest.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_withdrawals.html', withdrawals=withdrawals, status_filter=status_filter)

@app.route('/admin/withdrawals/<int:withdrawal_id>/approve', methods=['POST'])
@admin_required
def approve_withdrawal(withdrawal_id):
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    
    if withdrawal.status == 'pending':
        withdrawal.status = 'approved'
        db.session.commit()
        flash(f"Withdrawal of ${withdrawal.amount} approved.", "success")
    else:
        flash("Withdrawal has already been processed.", "warning")
    
    return redirect(url_for('view_withdrawals'))

@app.route('/admin/withdrawals/<int:withdrawal_id>/reject', methods=['POST'])
@admin_required
def reject_withdrawal(withdrawal_id):
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    
    if withdrawal.status == 'pending':
        withdrawal.status = 'rejected'
        # Refund the amount to user's balance
        user = User.query.get(withdrawal.user_id)
        user.balance += withdrawal.amount
        
        db.session.commit()
        flash(f"Withdrawal of ${withdrawal.amount} rejected and amount refunded.", "success")
    else:
        flash("Withdrawal has already been processed.", "warning")
    
    return redirect(url_for('view_withdrawals'))

# Hotel Management
@app.route('/admin/hotels', methods=['GET', 'POST'])
@admin_required
def manage_hotels():
    if request.method == 'POST':
        name = request.form['name']
        primary_picture = request.form['primary_picture']
        price = float(request.form['price'])
        commission_multiplier = float(request.form.get('commission_multiplier', 1.0))
        days_available = int(request.form.get('days_available', 1))
        description = request.form.get('description', '')
        location = request.form.get('location', '')

        new_hotel = Hotel(
            name=name,
            primary_picture=primary_picture,
            price=price,
            commission_multiplier=commission_multiplier,
            days_available=days_available,
            description=description,
            location=location
        )
        db.session.add(new_hotel)
        db.session.commit()
        flash('Hotel added successfully', 'success')
        return redirect(url_for('manage_hotels'))

    page = request.args.get('page', 1, type=int)
    hotels = Hotel.query.order_by(Hotel.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin_hotels.html', hotels=hotels)

@app.route('/admin/hotels/<int:hotel_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    
    if request.method == 'POST':
        hotel.name = request.form['name']
        hotel.primary_picture = request.form['primary_picture']
        hotel.price = float(request.form['price'])
        hotel.commission_multiplier = float(request.form.get('commission_multiplier', 1.0))
        hotel.days_available = int(request.form.get('days_available', 1))
        hotel.description = request.form.get('description', '')
        hotel.location = request.form.get('location', '')
        
        db.session.commit()
        flash('Hotel updated successfully', 'success')
        return redirect(url_for('manage_hotels'))
    
    return render_template('admin_edit_hotel.html', hotel=hotel)

@app.route('/admin/hotels/<int:hotel_id>/delete', methods=['POST'])
@admin_required
def delete_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    hotel_name = hotel.name
    
    db.session.delete(hotel)
    db.session.commit()
    flash(f'Hotel "{hotel_name}" deleted successfully', 'success')
    return redirect(url_for('manage_hotels'))

# Invitation Code Management
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
        flash(f'{len(codes)} invitation code(s) generated successfully.', 'success')
        return render_template('admin_invite.html', codes=codes)

    # Show existing codes
    page = request.args.get('page', 1, type=int)
    codes = InvitationCode.query.order_by(InvitationCode.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin_invite.html', codes=codes)

@app.route('/admin/invite-codes/<int:code_id>/delete', methods=['POST'])
@admin_required
def delete_invitation_code(code_id):
    code = InvitationCode.query.get_or_404(code_id)
    code_value = code.code
    
    db.session.delete(code)
    db.session.commit()
    flash(f'Invitation code "{code_value}" deleted successfully', 'success')
    return redirect(url_for('generate_invitation_code'))

# Admin Settings
@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    admin = Admin.query.get(session['admin_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            admin.username = request.form['username']
            admin.email = request.form['email']
            db.session.commit()
            flash('Profile updated successfully', 'success')
            
        elif action == 'change_password':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if not admin.check_password(current_password):
                flash('Current password is incorrect', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'danger')
            else:
                admin.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully', 'success')
    
    return render_template('admin_settings.html', admin=admin)

# Create admin function (run this once to create the first admin)
def create_admin():
    """
    Run this function once to create the first admin user.
    You can run this in a Python shell or create a CLI command.
    """
    admin = Admin(
        username='admin',
        email='admin@example.com'
    )
    admin.set_password('admin123')  # Change this password!
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("Please change the password after first login!")

# Middleware to prevent regular users from accessing admin routes
@app.before_request
def check_admin_routes():
    if request.endpoint and request.endpoint.startswith('admin_') and request.endpoint != 'admin_login':
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        
@admin_required
def admin_settings():
    admin = current_user  # Assuming current_user is the admin
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'profile':
            admin.username = request.form.get('username')
            admin.email = request.form.get('email')
            admin.full_name = request.form.get('full_name')
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        elif form_type == 'password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(admin.password, current_password):
                flash('Current password is incorrect!', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match!', 'error')
            else:
                admin.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Password changed successfully!', 'success')
                
        elif form_type == 'system':
            # Handle system settings (you might want to store these in a settings table)
            flash('System settings updated successfully!', 'success')
    
    return render_template('admin_settings.html', admin=admin)
@admin_required
def view_user_details(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'adjust_balance':
            adjustment_type = request.form.get('adjustment_type')
            amount = float(request.form.get('amount', 0))
            reason = request.form.get('reason', '')
            
            if adjustment_type == 'add':
                user.balance += amount
            elif adjustment_type == 'subtract':
                user.balance -= amount
            elif adjustment_type == 'set':
                user.balance = amount
            
            db.session.commit()
            flash(f'Balance adjusted successfully! New balance: ${user.balance:.2f}', 'success')
            
        elif action == 'toggle_status':
            user.is_active = not user.is_active
            db.session.commit()
            flash(f'User {"activated" if user.is_active else "deactivated"} successfully!', 'success')
            
        elif action == 'reset_password':
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.password = generate_password_hash(temp_password)
            db.session.commit()
            flash(f'Password reset successfully! Temporary password: {temp_password}', 'success')
            
        elif action == 'send_message':
            # Handle message sending (implement according to your message system)
            flash('Message sent successfully!', 'success')
    
    return render_template('admin_user_details.html', user=user)
@admin_required
def clear_logs():
    # Implement log clearing logic
    return jsonify({'success': True, 'message': 'Logs cleared successfully'})

@admin_required  
def reset_sessions():
    # Implement session reset logic
    return jsonify({'success': True, 'message': 'All sessions reset successfully'})