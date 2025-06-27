# hotel_app/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from hotel_app import app, db
from hotel_app.models import User, Hotel, Reservation, DepositRequest, WithdrawalRequest, EventAd
from datetime import datetime, date
from flask_login import login_required
@app.route('/')
def home():
    return render_template('home.html')
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from hotel_app import db
from hotel_app.models import User, InvitationCode  # ✅ Only import User now


import random
import logging
from datetime import datetime
from flask import request, render_template, redirect, url_for, flash, session, jsonify

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

import string

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.all()
    
    # Calculate today's reservations for daily limit checking
    today_reservations = Reservation.query.filter_by(user_id=user.id).filter(
        Reservation.timestamp >= datetime.combine(date.today(), datetime.min.time())).count()
    
    return render_template('dashboard.html', 
                         hotels=hotels, 
                         user=user, 
                         today_reservations=today_reservations)

@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    ads = EventAd.query.all()
    return render_template('events.html', ads=ads)

@app.route('/credit')
def credit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('credit.html', user=user)

# Updated reservation route with automatic completion
@app.route('/reserve/<int:hotel_id>', methods=['GET', 'POST'])
def reserve(hotel_id):
    if 'user_id' not in session:
        if request.method == 'GET':
            return redirect(url_for('login'))
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        hotel = Hotel.query.get_or_404(hotel_id)

        # Check daily reservation limit
        today_reservations = Reservation.query.filter_by(user_id=user.id).filter(
            Reservation.timestamp >= datetime.combine(date.today(), datetime.min.time())).count()
        
        limits = {'VIP0': 5, 'VIP1': 10, 'VIP2': 15}
        daily_limit = limits.get(user.vip_level, 5)

        if today_reservations >= daily_limit:
            if request.method == 'GET':
                flash(f'Daily reservation limit reached ({daily_limit} reservations per day for {user.vip_level})', 'error')
                return redirect(url_for('reservations'))
            return jsonify({
                'error': f'Daily reservation limit reached ({daily_limit} reservations per day for {user.vip_level})'
            }), 403

        # Calculate commission
        commission = 0.02 * hotel.price * hotel.commission_multiplier
        
        # Generate unique order number
        order_number = f"ORD{user.id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create reservation with immediate completion and commission payment
        reservation = Reservation(
            user_id=user.id,
            hotel_id=hotel.id,
            order_number=order_number,
            commission_earned=commission,
            status='Completed',  # Set to completed immediately
            timestamp=datetime.utcnow(),
            commission_paid=True,  # Mark commission as paid immediately
            commission_paid_at=datetime.utcnow()  # Set payment timestamp
        )
        
        # Add commission to user balance immediately
        print(f"DEBUG: Adding commission {commission} to user {user.id}")
        print(f"DEBUG: User balance before: {user.balance}")
        
        user.balance += commission
        
        print(f"DEBUG: User balance after: {user.balance}")
        
        # Add both user and reservation to session
        db.session.add(reservation)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Refresh to get updated data
        
        print(f"DEBUG: User balance after commit: {user.balance}")
        
        if request.method == 'GET':
            flash('Reservation completed successfully and commission added to your balance!', 'success')
            return redirect(url_for('reservations'))
        
        return jsonify({
            'success': True,
            'message': 'Reservation completed successfully and commission added to your balance!',
            'reservation_id': reservation.id,
            'order_number': order_number,
            'commission_earned': commission,
            'new_balance': user.balance
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR in reserve function: {str(e)}")
        if request.method == 'GET':
            flash(f'Error creating reservation: {str(e)}', 'error')
            return redirect(url_for('reservations'))
        return jsonify({'error': str(e)}), 500

@app.route('/reservations')
def reservations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.all()
    
    # Since commissions are now paid immediately, we don't need to process unpaid ones
    # But keep this logic for any legacy reservations that might exist
    unpaid_reservations = Reservation.query.filter_by(
        user_id=user.id, 
        status='Completed', 
        commission_paid=False
    ).all()
    
    # Process any legacy unpaid commissions
    total_new_commission = 0
    for reservation in unpaid_reservations:
        print(f"DEBUG: Processing legacy commission {reservation.commission_earned} for user {user.id}")
        print(f"DEBUG: User balance before: {user.balance}")
        
        user.balance += reservation.commission_earned
        reservation.commission_paid = True
        reservation.commission_paid_at = datetime.utcnow()
        total_new_commission += reservation.commission_earned
        
        print(f"DEBUG: User balance after: {user.balance}")
    
    # Commit any legacy commission updates
    if unpaid_reservations:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        print(f"DEBUG: User balance after commit: {user.balance}")
    
    # Get user's reservations with hotel details
    user_reservations = db.session.query(Reservation, Hotel).join(
        Hotel, Reservation.hotel_id == Hotel.id
    ).filter(Reservation.user_id == user.id).order_by(Reservation.timestamp.desc()).all()
    
    # Format reservations for template
    formatted_reservations = []
    for reservation, hotel in user_reservations:
        formatted_reservations.append({
            'id': reservation.id,
            'hotel_name': hotel.name,
            'location': f"{hotel.name} Location",
            'price': hotel.price,
            'commission': reservation.commission_earned,
            'status': reservation.status.lower(),
            'created_at': reservation.timestamp,
            'rated': reservation.rating is not None,
            'commission_paid': reservation.commission_paid
        })
    
    # Calculate user stats for display
    total_commission = sum([r.commission_earned for r in Reservation.query.filter_by(user_id=user.id, commission_paid=True).all()])
    trial_bonus = 250.00
    deposit_balance = 540.00
    active_bookings = len([r for r in formatted_reservations if r['status'] in ['processing', 'confirmed']])
    
    user_stats = {
        'total_commission': total_commission,
        'trial_bonus': trial_bonus,
        'deposit_balance': deposit_balance,
        'active_bookings': active_bookings
    }
    
    print(f"Final user balance being sent to template: {user.balance}")
    
    return render_template('reservations.html', hotels=hotels, user=user, reservations=formatted_reservations, user_stats=user_stats)

@app.route('/rate/<int:reservation_id>', methods=['POST'])
def rate(reservation_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        user = User.query.get(session['user_id'])
        
        if reservation.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if reservation.status.lower() != 'completed':
            return jsonify({'error': 'Can only rate completed reservations'}), 400
            
        if reservation.rating is not None:
            return jsonify({'error': 'Reservation already rated'}), 400
        
        # Get rating and feedback
        if request.is_json:
            rating = request.json.get('rating', 5)
            feedback = request.json.get('feedback', '')
        else:
            rating = int(request.form.get('rating', 5))
            feedback = request.form.get('feedback', '')
        
        # Update reservation with rating
        reservation.rating = rating
        reservation.feedback = feedback
        
        # Since commission is now paid immediately upon reservation creation,
        # we don't need to add it again here. Just commit the rating.
        db.session.add(reservation)
        db.session.commit()
        
        print(f"DEBUG: Rating submitted for reservation {reservation_id}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Rating submitted successfully',
                'current_balance': user.balance  # Show current balance, no new commission added
            })
        else:
            flash('Rating submitted successfully', 'success')
            return redirect(url_for('reservations'))
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR in rate function: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Error submitting rating: {str(e)}', 'error')
            return redirect(url_for('reservations'))

# Optional: Keep admin route for any manual processing needs
@app.route('/admin/process-commissions')
def process_commissions():
    """Admin route to process any legacy pending commissions"""
    if 'admin' not in session:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Only process legacy commissions that somehow didn't get paid
    unpaid_reservations = Reservation.query.filter_by(
        status='Completed', 
        commission_paid=False
    ).all()
    
    processed_count = 0
    total_commission = 0
    
    for reservation in unpaid_reservations:
        user = User.query.get(reservation.user_id)
        user.balance += reservation.commission_earned
        reservation.commission_paid = True
        reservation.commission_paid_at = datetime.utcnow()
        
        db.session.add(user)
        
        processed_count += 1
        total_commission += reservation.commission_earned
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Processed {processed_count} legacy reservations',
        'processed_reservations': processed_count,
        'total_commission_paid': total_commission
    })

# Optional: Add a function to simulate processing delay if needed
def create_reservation_with_delay(user_id, hotel_id, commission, order_number):
    """Alternative function if you want to simulate processing time"""
    import threading
    import time
    
    def complete_reservation():
        time.sleep(5)  # Simulate 5-second processing delay
        
        reservation = Reservation.query.filter_by(order_number=order_number).first()
        user = User.query.get(user_id)
        
        if reservation and user:
            reservation.status = 'Completed'
            reservation.commission_paid = True
            reservation.commission_paid_at = datetime.utcnow()
            
            user.balance += commission
            
            db.session.add(user)
            db.session.add(reservation)
            db.session.commit()
            
            print(f"Background: Reservation {order_number} completed and commission paid")
    
    # Start background thread
    thread = threading.Thread(target=complete_reservation)
    thread.daemon = True
    thread.start()
@app.route('/order-history')
def order_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get all reservations with hotel details
    reservations_query = db.session.query(Reservation, Hotel).join(
        Hotel, Reservation.hotel_id == Hotel.id
    ).filter(Reservation.user_id == user.id).order_by(Reservation.timestamp.desc())
    
    all_reservations = reservations_query.all()
    
    # Separate by status
    processing = [(r, h) for r, h in all_reservations if r.status.lower() in ['processing', 'confirmed']]
    completed = [(r, h) for r, h in all_reservations if r.status.lower() == 'completed']
    cancelled = [(r, h) for r, h in all_reservations if r.status.lower() == 'cancelled']
    
    return render_template('order_history.html', 
                         all_orders=all_reservations, 
                         processing=processing, 
                         completed=completed,
                         cancelled=cancelled)

from sqlalchemy import func

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the user from the database
    user = User.query.get(session['user_id'])
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # More efficient queries using aggregation
    reservation_stats = db.session.query(
        func.count(Reservation.id).label('total_reservations'),
        func.count(Reservation.id).filter(Reservation.status == 'Completed').label('completed_reservations'),
        func.coalesce(func.sum(Reservation.commission_earned), 0).label('total_commission')
    ).filter_by(user_id=user.id).first()
    
    # Calculate completion rate
    total_reservations = reservation_stats.total_reservations or 0
    completed_reservations = reservation_stats.completed_reservations or 0
    completion_rate = (completed_reservations / total_reservations * 100) if total_reservations > 0 else 0
    total_commission = reservation_stats.total_commission or 0
    print(f"User balance: {user.balance} {user.user_id}")
    
    return render_template('profile.html', 
                         user=user,
                         total_reservations=total_reservations,
                         completed_reservations=completed_reservations,
                         completion_rate=completion_rate,
                         total_commission=total_commission)

# Updated deposit route with wallet address validation
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            network = request.form['network']
            wallet_address = request.form['wallet_address'].strip()
            transaction_hash = request.form.get('transaction_hash', '').strip()
            
            if amount <= 0:
                flash('Invalid deposit amount', 'error')
                return render_template('deposit.html', user=user)
            
            if not wallet_address:
                flash('Wallet address is required', 'error')
                return render_template('deposit.html', user=user)
            
            # Validate wallet address format
            if not DepositRequest.validate_wallet_address(wallet_address, network):
                flash(f'Invalid wallet address format for {network} network', 'error')
                return render_template('deposit.html', user=user)
            
            # Create deposit request
            deposit_request = DepositRequest(
                user_id=user.id, 
                amount=amount, 
                network=network,
                wallet_address=wallet_address,
                transaction_hash=transaction_hash,
                status='Pending'
            )
            
            db.session.add(deposit_request)
            db.session.commit()
            
            flash('Deposit request submitted successfully. Please wait for admin approval.', 'success')
            return redirect(url_for('profile'))
            
        except ValueError:
            flash('Invalid deposit amount format', 'error')
        except Exception as e:
            flash(f'Error processing deposit: {str(e)}', 'error')
    
    return render_template('deposit.html', user=user)

# Updated withdrawal route with wallet address validation
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            network = request.form['network']
            wallet_address = request.form['wallet_address'].strip()
            withdrawal_password = request.form.get('withdrawal_password')
            
            # Check if withdrawal password is set
            if not user.withdrawal_password:
                flash('Please set a withdrawal password first', 'error')
                return redirect(url_for('set_withdrawal_password'))
            
            # Validate withdrawal password
            if user.withdrawal_password != withdrawal_password:
                flash('Invalid withdrawal password', 'error')
                return render_template('withdraw.html', user=user)
            
            # Check balance
            if amount > user.balance:
                flash('Insufficient balance', 'error')
                return render_template('withdraw.html', user=user)
            
            if amount <= 0:
                flash('Invalid withdrawal amount', 'error')
                return render_template('withdraw.html', user=user)
            
            if not wallet_address:
                flash('Wallet address is required', 'error')
                return render_template('withdraw.html', user=user)
            
            # Validate wallet address format
            if not WithdrawalRequest.validate_wallet_address(wallet_address, network):
                flash(f'Invalid wallet address format for {network} network', 'error')
                return render_template('withdraw.html', user=user)
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest(
                user_id=user.id, 
                amount=amount, 
                network=network,
                wallet_address=wallet_address,
                status='Pending'
            )
            
            # Temporarily reduce balance (will be restored if withdrawal is rejected)
            user.balance -= amount
            
            db.session.add(withdrawal_request)
            db.session.commit()
            
            flash('Withdrawal request submitted successfully. Please wait for approval.', 'success')
            return redirect(url_for('profile'))
            
        except ValueError:
            flash('Invalid withdrawal amount format', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing withdrawal: {str(e)}', 'error')
    
    return render_template('withdraw.html', user=user)

@app.route('/set-withdrawal-password', methods=['GET', 'POST'])
def set_withdrawal_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            password = request.form['password']
            confirm_password = request.form.get('confirm_password', '')
            
            if confirm_password and password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('set_password.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('set_password.html')
            
            user.withdrawal_password = password
            db.session.commit()
            
            flash('Withdrawal password set successfully', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            flash(f'Error setting password: {str(e)}', 'error')
    
    return render_template('set_password.html')

# API endpoints for AJAX calls from the frontend
@app.route('/api/user-stats')
def api_user_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    today_reservations = Reservation.query.filter_by(user_id=user.id).filter(
        Reservation.timestamp >= datetime.combine(date.today(), datetime.min.time())).count()
    
    limits = {'VIP0': 5, 'VIP1': 10, 'VIP2': 15}
    daily_limit = limits.get(user.vip_level, 5)
    
    # Calculate total commission
    total_commission = sum([r.commission_earned for r in Reservation.query.filter_by(user_id=user.id).all()])
    
    # Count active bookings
    active_bookings = Reservation.query.filter_by(user_id=user.id).filter(
        Reservation.status.in_(['Processing', 'Confirmed'])).count()
    
    return jsonify({
        'balance': user.balance,
        'total_commission': total_commission,
        'trial_bonus': 250.00,  # Static value as per your template
        'deposit_balance': 540.00,  # Static value as per your template
        'today_reservations': today_reservations,
        'daily_limit': daily_limit,
        'vip_level': user.vip_level,
        'active_bookings': active_bookings
    })

@app.route('/api/complete-reservation/<int:reservation_id>', methods=['POST'])
def complete_reservation(reservation_id):
    """Admin endpoint to mark reservations as completed"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        reservation.status = 'Completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reservation marked as completed'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate-reservation-processing')
def simulate_reservation_processing():
    """Simulate reservation status updates for testing"""
    try:
        # Get processing/confirmed reservations
        active_reservations = Reservation.query.filter(
            Reservation.status.in_(['Processing', 'Confirmed'])).all()
        
        updated_count = 0
        for reservation in active_reservations:
            # Randomly update status
            if random.random() < 0.2:  # 20% chance to update
                if reservation.status == 'Processing':
                    reservation.status = random.choice(['Confirmed', 'Completed'])
                elif reservation.status == 'Confirmed':
                    reservation.status = 'Completed'
                updated_count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'updated': updated_count})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Helper route to get reservation details for modals
@app.route('/api/reservation/<int:reservation_id>')
def get_reservation_details(reservation_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        reservation, hotel = db.session.query(Reservation, Hotel).join(
            Hotel, Reservation.hotel_id == Hotel.id
        ).filter(Reservation.id == reservation_id, 
                Reservation.user_id == session['user_id']).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        return jsonify({
            'id': reservation.id,
            'hotel_name': hotel.name,
            'price': hotel.price,
            'commission': reservation.commission_earned,
            'status': reservation.status,
            'order_number': reservation.order_number,
            'timestamp': reservation.timestamp.isoformat(),
            'rating': reservation.rating,
            'feedback': reservation.feedback
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/membership')
def membership():
    user = User.query.get(session['user_id'])
    return render_template('membership.html', user=user)

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        if 'language' in request.form:
            session['language'] = request.form['language']
        elif 'nickname' in request.form:
            user.nickname = request.form['nickname']
            db.session.commit()
            flash('Nickname updated successfully!', 'success')
        elif 'password' in request.form:
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Passwords do not match!', 'error')
    return render_template('settings.html', user=user)

@app.route('/customer_service')
def customer_service():
    return render_template('customer_service.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_text = request.form.get('feedback_text', '').strip()
        if not feedback_text:
            flash('Feedback cannot be empty', 'error')
        else:
            # Here you would save the feedback to the database
            # For now, just flash a success message
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('feedback'))
    return render_template('feedback.html')

@app.route('/help_center')
def help_center():
    return render_template('help_center.html')

@app.route('/bind_wallet')
def bind_wallet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('bind_wallet.html', user=user)



# Admin Setup Functions
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

## VIEW DEPOSITS - Main listing page
@app.route('/admin/deposits')
@admin_required
def view_deposits():
    """View all deposit requests - Admin only"""
    try:
        logger.debug("Accessing view_deposits route")
        page = request.args.get('page', 1, type=int)
        
        # Debug: Check if DepositRequest model exists and has data
        total_deposits = DepositRequest.query.count()
        logger.debug(f"Total deposits in database: {total_deposits}")
        
        deposits = DepositRequest.query.order_by(DepositRequest.created_at.desc()).paginate(
            page=page,
            per_page=20,
            error_out=False
        )
        
        logger.debug(f"Deposits found for page {page}: {len(deposits.items)}")
        
        # Debug: Log first few deposits
        for i, deposit in enumerate(deposits.items[:3]):
            logger.debug(f"Deposit {i}: ID={deposit.id}, Status={deposit.status}, Amount=${deposit.amount}")
        
        return render_template('admin_deposits.html', deposits=deposits)
        
    except Exception as e:
        logger.error(f"Error in view_deposits: {str(e)}")
        flash(f'Error loading deposits: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# APPROVE DEPOSIT - Individual deposit approval
@app.route('/admin/deposits/<int:deposit_id>/approve', methods=['POST'])
@admin_required
def approve_deposit(deposit_id):
    try:
        logger.debug(f"Approving deposit {deposit_id}")
        logger.debug(f"Request form data: {dict(request.form)}")
        
        # Validate the request
        if not request.form:
            logger.warning("No form data received")
            flash("Invalid request data", "error")
            return redirect(url_for('view_deposits'))
        
        deposit = DepositRequest.query.get_or_404(deposit_id)
        logger.debug(f"Found deposit: {deposit.id}, Status: {deposit.status}")
        
        admin = Admin.query.get(session.get('admin_id'))
        
        if not admin:
            logger.error("Admin not found in session")
            flash("Admin session invalid", "error")
            return redirect(url_for('admin_login'))
        
        if deposit.status == 'Pending':
            deposit.status = 'Approved'
            deposit.processed_at = datetime.utcnow()
            deposit.processed_by = admin.id
            deposit.admin_notes = request.form.get('admin_notes', '')
            
            # Update user balance
            user = User.query.get(deposit.user_id)
            if user:
                old_balance = user.balance
                user.balance += deposit.amount
                logger.debug(f"Updated user {user.id} balance from ${old_balance} to ${user.balance}")
                
                db.session.commit()
                flash(f"Deposit of ${deposit.amount} approved for user {user.nickname}.", "success")
            else:
                logger.error(f"User {deposit.user_id} not found")
                flash("User not found", "error")
        else:
            logger.warning(f"Deposit {deposit_id} already processed with status: {deposit.status}")
            flash("Deposit has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing deposit: {str(e)}", "error")
    
    return redirect(url_for('view_deposits'))

# REJECT DEPOSIT
@app.route('/admin/deposits/<int:deposit_id>/reject', methods=['POST'])
@admin_required
def reject_deposit(deposit_id):
    try:
        logger.debug(f"Rejecting deposit {deposit_id}")
        logger.debug(f"Request form data: {dict(request.form)}")
        
        # Validate the request
        if not request.form:
            logger.warning("No form data received")
            flash("Invalid request data", "error")
            return redirect(url_for('view_deposits'))
        
        deposit = DepositRequest.query.get_or_404(deposit_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if not admin:
            logger.error("Admin not found in session")
            flash("Admin session invalid", "error")
            return redirect(url_for('admin_login'))
        
        if deposit.status == 'Pending':
            deposit.status = 'Rejected'
            deposit.processed_at = datetime.utcnow()
            deposit.processed_by = admin.id
            deposit.admin_notes = request.form.get('admin_notes', '')
            
            db.session.commit()
            flash(f"Deposit of ${deposit.amount} rejected.", "success")
        else:
            logger.warning(f"Deposit {deposit_id} already processed with status: {deposit.status}")
            flash("Deposit has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing deposit: {str(e)}", "error")
    
    return redirect(url_for('view_deposits'))

# VIEW WITHDRAWALS - Main listing page
@app.route('/admin/withdrawals')
@admin_required
def view_withdrawals():
    """View all withdrawal requests - Admin only"""
    try:
        logger.debug("Accessing view_withdrawals route")
        page = request.args.get('page', 1, type=int)
        
        # Debug: Check if WithdrawalRequest model exists and has data
        total_withdrawals = WithdrawalRequest.query.count()
        logger.debug(f"Total withdrawals in database: {total_withdrawals}")
        
        withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).paginate(
            page=page,
            per_page=20,
            error_out=False
        )
        
        logger.debug(f"Withdrawals found for page {page}: {len(withdrawals.items)}")
        
        return render_template('admin_withdrawals.html', withdrawals=withdrawals)
        
    except Exception as e:
        logger.error(f"Error in view_withdrawals: {str(e)}")
        flash(f'Error loading withdrawals: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# APPROVE WITHDRAWAL - Individual withdrawal approval
@app.route('/admin/withdrawals/<int:withdrawal_id>/approve', methods=['POST'])
@admin_required
def approve_withdrawal(withdrawal_id):
    try:
        logger.debug(f"Approving withdrawal {withdrawal_id}")
        logger.debug(f"Request form data: {dict(request.form)}")
        
        # Validate the request
        if not request.form:
            logger.warning("No form data received")
            flash("Invalid request data", "error")
            return redirect(url_for('view_withdrawals'))
        
        withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if not admin:
            logger.error("Admin not found in session")
            flash("Admin session invalid", "error")
            return redirect(url_for('admin_login'))
        
        if withdrawal.status == 'Pending':
            withdrawal.status = 'Approved'
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.processed_by = admin.id
            withdrawal.admin_notes = request.form.get('admin_notes', '')
            withdrawal.transaction_hash = request.form.get('transaction_hash', '')
            
            # Safely handle transaction_fee conversion
            try:
                transaction_fee = float(request.form.get('transaction_fee', 0))
                withdrawal.transaction_fee = transaction_fee
            except (ValueError, TypeError):
                withdrawal.transaction_fee = 0.0
            
            db.session.commit()
            flash(f"Withdrawal of ${withdrawal.amount} approved.", "success")
        else:
            logger.warning(f"Withdrawal {withdrawal_id} already processed with status: {withdrawal.status}")
            flash("Withdrawal has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing withdrawal: {str(e)}", "error")
    
    return redirect(url_for('view_withdrawals'))

# REJECT WITHDRAWAL
@app.route('/admin/withdrawals/<int:withdrawal_id>/reject', methods=['POST'])
@admin_required
def reject_withdrawal(withdrawal_id):
    try:
        logger.debug(f"Rejecting withdrawal {withdrawal_id}")
        logger.debug(f"Request form data: {dict(request.form)}")
        
        # Validate the request
        if not request.form:
            logger.warning("No form data received")
            flash("Invalid request data", "error")
            return redirect(url_for('view_withdrawals'))
        
        withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if not admin:
            logger.error("Admin not found in session")
            flash("Admin session invalid", "error")
            return redirect(url_for('admin_login'))
        
        if withdrawal.status == 'Pending':
            withdrawal.status = 'Rejected'
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.processed_by = admin.id
            withdrawal.admin_notes = request.form.get('admin_notes', '')
            withdrawal.rejection_reason = request.form.get('rejection_reason', '')
            
            # Refund the amount to user's balance
            user = User.query.get(withdrawal.user_id)
            if user:
                old_balance = user.balance
                user.balance += withdrawal.amount
                logger.debug(f"Refunded user {user.id} balance from ${old_balance} to ${user.balance}")
                
                db.session.commit()
                flash(f"Withdrawal of ${withdrawal.amount} rejected and amount refunded.", "success")
            else:
                logger.error(f"User {withdrawal.user_id} not found")
                flash("User not found", "error")
        else:
            logger.warning(f"Withdrawal {withdrawal_id} already processed with status: {withdrawal.status}")
            flash("Withdrawal has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing withdrawal: {str(e)}", "error")
    
    return redirect(url_for('view_withdrawals'))

# API endpoint for wallet validation
@app.route('/api/validate-wallet', methods=['POST'])
def validate_wallet_address():
    """API endpoint to validate wallet address format"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        address = data.get('address', '').strip()
        network = data.get('network', '').upper()
        
        if not address or not network:
            return jsonify({'valid': False, 'message': 'Address and network are required'})
        
        is_valid = DepositRequest.validate_wallet_address(address, network)
        
        return jsonify({
            'valid': is_valid,
            'message': f'Valid {network} address' if is_valid else f'Invalid {network} address format'
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500
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
# Add this test route temporarily to debug your deposit system
@app.route('/admin/test-deposits')
@admin_required
def test_deposits():
    """Test route to debug deposit issues"""
    try:
        # Check if models exist
        from your_app import DepositRequest, User, Admin  # Replace 'your_app' with your actual app module
        
        # Get basic stats
        total_deposits = DepositRequest.query.count()
        pending_deposits = DepositRequest.query.filter_by(status='Pending').count()
        
        # Get sample data
        sample_deposits = DepositRequest.query.limit(5).all()
        
        debug_info = {
            'total_deposits': total_deposits,
            'pending_deposits': pending_deposits,
            'sample_deposits': []
        }
        
        for deposit in sample_deposits:
            debug_info['sample_deposits'].append({
                'id': deposit.id,
                'amount': deposit.amount,
                'status': deposit.status,
                'user_id': deposit.user_id,
                'created_at': deposit.created_at.strftime('%Y-%m-%d %H:%M') if deposit.created_at else 'N/A'
            })
        
        return f"""
        <h2>Deposit Debug Info</h2>
        <p><strong>Total Deposits:</strong> {debug_info['total_deposits']}</p>
        <p><strong>Pending Deposits:</strong> {debug_info['pending_deposits']}</p>
        <h3>Sample Deposits:</h3>
        <ul>
        """ + "\n".join([f"<li>ID: {d['id']}, Amount: ${d['amount']}, Status: {d['status']}, Date: {d['created_at']}</li>" for d in debug_info['sample_deposits']]) + """
        </ul>
        <p><a href="/admin/deposits">Go to Deposits Page</a></p>
        """
        
    except Exception as e:
        return f"<h2>Error:</h2><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

# Also add this route to check if your admin_required decorator is working
@app.route('/admin/test-auth')
def test_auth():
    """Test admin authentication"""
    if 'admin_id' in session:
        admin = Admin.query.get(session['admin_id'])
        return f"<h2>Admin Auth Test</h2><p>Logged in as Admin ID: {session['admin_id']}</p><p>Admin: {admin.username if admin else 'Not found'}</p>"
    else:
        return "<h2>Admin Auth Test</h2><p>Not logged in as admin</p>"