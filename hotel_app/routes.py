# hotel_app/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from hotel_app import app, db
from hotel_app.models import User, Hotel, Reservation, DepositRequest, WithdrawalRequest, EventAd, Admin, InvitationCode
from datetime import datetime, date
from flask_login import login_required
@app.route('/')
def home():
    return render_template('home.html')
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from hotel_app import db
 # ✅ Only import User now


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
            flash('Account not yet activated', 'warning')
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

# Enhanced deposit route with comprehensive debugging
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    print("=== DEPOSIT ROUTE CALLED ===")
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Debug: Log all form data received
            print("=== DEBUG: DEPOSIT FORM DATA ===")
            print(f"Form data received: {dict(request.form)}")
            
            amount = float(request.form['amount'])
            network = request.form['network']
            transaction_hash = request.form.get('transaction_hash', '').strip()
            
            print(f"Parsed - Amount: {amount}, Network: {network}, TxHash: {transaction_hash}")
            
            if amount <= 0:
                print("ERROR: Invalid amount <= 0")
                flash('Invalid deposit amount', 'error')
                return render_template('deposit.html', user=user)
            
            # Check if we need wallet_address (uncomment if required)
            # wallet_address = request.form.get('wallet_address', '').strip()
            # if not wallet_address:
            #     print("ERROR: Missing wallet_address")
            #     flash('Wallet address is required', 'error')
            #     return render_template('deposit.html', user=user)
            
            print("=== DEBUG: CREATING DEPOSIT REQUEST ===")
            
            # Create deposit request with explicit field logging
            deposit_request = DepositRequest(
                user_id=user.id, 
                amount=amount, 
                network=network,
                # wallet_address=wallet_address,  # Uncomment if needed
                transaction_hash=transaction_hash,
                status='Pending'
            )
            
            print(f"Created deposit_request object:")
            print(f"  - user_id: {deposit_request.user_id}")
            print(f"  - amount: {deposit_request.amount}")
            print(f"  - network: {deposit_request.network}")
            print(f"  - transaction_hash: {deposit_request.transaction_hash}")
            print(f"  - status: {deposit_request.status}")
            
            print("=== DEBUG: SAVING TO DATABASE ===")
            
            # Add to session
            db.session.add(deposit_request)
            print("Added to db.session")
            
            # Commit transaction
            db.session.commit()
            print("Successfully committed to database")
            
            # Verify it was saved
            saved_deposit = DepositRequest.query.filter_by(id=deposit_request.id).first()
            if saved_deposit:
                print(f"VERIFICATION: Deposit saved with ID: {saved_deposit.id}")
                print(f"VERIFICATION: Total deposits in DB: {DepositRequest.query.count()}")
            else:
                print("ERROR: Deposit not found after commit!")
            
            flash('Deposit request submitted successfully. Please wait for admin approval.', 'success')
            return redirect(url_for('profile'))
            
        except ValueError as ve:
            print(f"ValueError: {str(ve)}")
            flash('Invalid deposit amount format', 'error')
            return render_template('deposit.html', user=user)
            
        except Exception as e:
            print(f"=== CRITICAL ERROR IN DEPOSIT ROUTE ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            
            # Import traceback for detailed error info
            import traceback
            print(f"Full traceback:")
            print(traceback.format_exc())
            
            # Rollback the transaction
            db.session.rollback()
            print("Database session rolled back")
            
            flash(f'Error processing deposit: {str(e)}', 'error')
            return render_template('deposit.html', user=user)
    
    return render_template('deposit.html', user=user)
# Updated withdrawal route with wallet address validation
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Validate required form fields exist
            if 'amount' not in request.form:
                flash('Amount is required', 'error')
                return render_template('withdraw.html', user=user)
            
            if 'network' not in request.form:
                flash('Network is required', 'error')
                return render_template('withdraw.html', user=user)
            
            if 'wallet_address' not in request.form:
                print('no wallet address supplied')
                flash('Wallet address is required', 'error')
                return render_template('withdraw.html', user=user)
            
            # Get form data with proper error handling
            amount_str = request.form['amount'].strip()
            network = request.form['network'].strip()
            wallet_address = request.form['wallet_address'].strip()
            withdrawal_password = request.form.get('withdrawal_password', '').strip()
            
            # Validate amount
            if not amount_str:
                flash('Amount cannot be empty', 'error')
                return render_template('withdraw.html', user=user)
            
            try:
                amount = float(amount_str)
            except ValueError:
                flash('Invalid amount format', 'error')
                return render_template('withdraw.html', user=user)
            
            # Validate network
            if not network:
                flash('Network is required', 'error')
                return render_template('withdraw.html', user=user)
            
            # Validate wallet address
            if not wallet_address:
                flash('Wallet address is required', 'error')
                return render_template('withdraw.html', user=user)
            
            # Check if withdrawal password is set
            if not user.withdrawal_password:
                flash('Please set a withdrawal password first', 'error')
                return redirect(url_for('set-withdrawal-password'))
            
            # Validate withdrawal password
            if not withdrawal_password:
                flash('Withdrawal password is required', 'error')
                return render_template('withdraw.html', user=user)
            
            if user.withdrawal_password != withdrawal_password:
                flash('Invalid withdrawal password', 'error')
                return render_template('withdraw.html', user=user)
            
            # Check amount validity
            if amount <= 0:
                flash('Invalid withdrawal amount', 'error')
                return render_template('withdraw.html', user=user)
            
            # Check balance
            if amount > user.balance:
                flash('Insufficient balance', 'error')
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
            
        except KeyError as e:
            flash(f'Missing required field: {str(e)}', 'error')
            return render_template('withdraw.html', user=user)
        except ValueError as e:
            flash(f'Invalid data format: {str(e)}', 'error')
            return render_template('withdraw.html', user=user)
        except Exception as e:
            db.session.rollback()
            # Restore balance if it was already deducted
            try:
                if 'amount' in locals() and amount > 0:
                    user.balance += amount
                    db.session.commit()
            except:
                pass  # If restoration fails, log it in production
            flash(f'Error processing withdrawal: {str(e)}', 'error')
            return render_template('withdraw.html', user=user)
    
    return render_template('withdraw.html', user=user)

@app.route('/set-withdrawal-password', methods=['GET', 'POST'])
def set_withdrawal_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not password:
                flash('Password is required', 'error')
                return render_template('set-withdrawal-password.html')
            
            if confirm_password and password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('set-withdrawal-password.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('set-withdrawal-password.html')
            
            user.withdrawal_password = password
            db.session.commit()
            
            flash('Withdrawal password set successfully', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error setting password: {str(e)}', 'error')
            return render_template('set-withdrawal-password.html')
    
    return render_template('set-withdrawal-password.html', user=user)
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

@app.route('/transaction_details')
def transaction_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    return render_template('transaction_details.html', user=user)



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
    vip_filter = request.args.get('vip_level', '')
    
    users_query = User.query
    if search:
        users_query = users_query.filter(
            User.nickname.contains(search) | 
            User.user.agent_id.contains(search)
        )
    
    if vip_filter:
        users_query = users_query.filter(User.vip_level == vip_filter)
    
    users = users_query.order_by(User.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # VIP levels for filter dropdown
    vip_levels = ['vip0', 'vip1', 'vip2', 'vip3']
    
    return render_template('admin_users.html', 
                         users=users, 
                         search=search, 
                         vip_levels=vip_levels,
                         current_vip_filter=vip_filter)

@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'activated' if user.is_active else 'deactivated'
    flash(f"User {user.nickname} has been {action}.", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/users/<int:user_id>/update_vip', methods=['POST'])
@admin_required
def update_user_vip(user_id):
    user = User.query.get_or_404(user_id)
    new_vip_level = request.form.get('vip_level')
    
    # Validate VIP level
    valid_vip_levels = ['vip0', 'vip1', 'vip2', 'vip3']
    if new_vip_level not in valid_vip_levels:
        flash("Invalid VIP level selected.", "error")
        return redirect(url_for('view_users'))
    
    old_vip_level = user.vip_level
    user.vip_level = new_vip_level
    db.session.commit()
    
    flash(f"User {user.nickname} VIP level updated from {old_vip_level} to {new_vip_level}.", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/users/<int:user_id>/bulk_update', methods=['POST'])
@admin_required
def bulk_update_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get form data
    new_vip_level = request.form.get('vip_level')
    toggle_status = request.form.get('toggle_status')
    
    changes_made = []
    
    # Update VIP level if provided
    if new_vip_level and new_vip_level != user.vip_level:
        valid_vip_levels = ['vip0', 'vip1', 'vip2', 'vip3']
        if new_vip_level in valid_vip_levels:
            old_vip = user.vip_level
            user.vip_level = new_vip_level
            changes_made.append(f"VIP level: {old_vip} → {new_vip_level}")
    
    # Toggle status if requested
    if toggle_status == 'toggle':
        user.is_active = not user.is_active
        status = 'activated' if user.is_active else 'deactivated'
        changes_made.append(f"Status: {status}")
    
    if changes_made:
        db.session.commit()
        flash(f"User {user.nickname} updated: {', '.join(changes_made)}", "success")
    else:
        flash("No changes were made.", "info")
    
    return redirect(url_for('view_users'))

@app.route('/admin/users/bulk_vip_update', methods=['POST'])
@admin_required
def bulk_vip_update():
    user_ids = request.form.getlist('user_ids')
    new_vip_level = request.form.get('bulk_vip_level')
    
    if not user_ids:
        flash("No users selected.", "error")
        return redirect(url_for('view_users'))
    
    valid_vip_levels = ['vip0', 'vip1', 'vip2', 'vip3']
    if new_vip_level not in valid_vip_levels:
        flash("Invalid VIP level selected.", "error")
        return redirect(url_for('view_users'))
    
    try:
        # Update multiple users at once
        updated_count = User.query.filter(User.id.in_(user_ids)).update(
            {User.vip_level: new_vip_level}, 
            synchronize_session=False
        )
        db.session.commit()
        
        flash(f"Successfully updated {updated_count} users to {new_vip_level}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating users: {str(e)}", "error")
    
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

@app.route('/admin/users/<int:user_id>/view', methods=['GET', 'POST'])
@admin_required
def view_user_details(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'adjust_balance':
            adjustment_type = request.form.get('adjustment_type')
            amount = request.form.get('amount')
            reason = request.form.get('reason', 'Admin adjustment')
            
            # Validate inputs
            if not adjustment_type or not amount:
                flash("Please provide adjustment type and amount.", "error")
                return redirect(url_for('view_user_details', user_id=user_id))
            
            try:
                amount = float(amount)
                if amount < 0:
                    flash("Amount must be positive.", "error")
                    return redirect(url_for('view_user_details', user_id=user_id))
            except ValueError:
                flash("Invalid amount format.", "error")
                return redirect(url_for('view_user_details', user_id=user_id))
            
            # Store original balance for logging
            original_balance = user.balance
            
            # Perform balance adjustment
            if adjustment_type == 'add':
                user.balance += amount
                action_description = f"Added ${amount:.2f} to balance"
            elif adjustment_type == 'subtract':
                if user.balance < amount:
                    flash(f"Cannot subtract ${amount:.2f}. User only has ${user.balance:.2f} in balance.", "error")
                    return redirect(url_for('view_user_details', user_id=user_id))
                user.balance -= amount
                action_description = f"Subtracted ${amount:.2f} from balance"
            elif adjustment_type == 'set':
                user.balance = amount
                action_description = f"Set balance to ${amount:.2f}"
            else:
                flash("Invalid adjustment type.", "error")
                return redirect(url_for('view_user_details', user_id=user_id))
            
            try:
                db.session.commit()
                flash(f"Balance adjustment successful! {action_description}. New balance: ${user.balance:.2f}", "success")
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error adjusting balance: {str(e)}", "error")
            
            return redirect(url_for('view_user_details', user_id=user_id))
        
        elif action == 'toggle_status':
            user.is_active = not user.is_active
            db.session.commit()
            status = 'activated' if user.is_active else 'deactivated'
            flash(f"User {user.nickname} has been {status}.", "success")
            return redirect(url_for('view_user_details', user_id=user_id))
        
        # Add other actions (send_message, reset_password) here as needed
    
    # GET request - display user details
    deposits = DepositRequest.query.filter_by(user_id=user_id).order_by(DepositRequest.id.desc()).all()
    withdrawals = WithdrawalRequest.query.filter_by(user_id=user_id).order_by(WithdrawalRequest.id.desc()).all()
    
    # VIP levels for the update form
    vip_levels = ['vip0', 'vip1', 'vip2', 'vip3']
    
    return render_template('admin_user_details.html', 
                         user=user, 
                         deposits=deposits, 
                         withdrawals=withdrawals,
                         vip_levels=vip_levels)

# API endpoint for AJAX VIP updates (optional)
@app.route('/admin/api/users/<int:user_id>/vip', methods=['PUT'])
@admin_required
def api_update_user_vip(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    new_vip_level = data.get('vip_level')
    valid_vip_levels = ['vip0', 'vip1', 'vip2', 'vip3']
    
    if new_vip_level not in valid_vip_levels:
        return jsonify({'error': 'Invalid VIP level'}), 400
    
    old_vip_level = user.vip_level
    user.vip_level = new_vip_level
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'VIP level updated from {old_vip_level} to {new_vip_level}',
        'old_vip': old_vip_level,
        'new_vip': new_vip_level
    })

# Helper route to get VIP level statistics
@app.route('/admin/users/vip_stats')
@admin_required
def vip_statistics():
    vip_stats = db.session.query(
        User.vip_level,
        db.func.count(User.id).label('count')
    ).group_by(User.vip_level).all()
    
    stats_dict = {level: 0 for level in ['vip0', 'vip1', 'vip2', 'vip3']}
    for stat in vip_stats:
        if stat.vip_level in stats_dict:
            stats_dict[stat.vip_level] = stat.count
    
    return jsonify(stats_dict)
# IMPROVED ADMIN ROUTES FOR DEPOSITS AND WITHDRAWALS

# VIEW DEPOSITS - Main listing page with better error handling and debugging
@app.route('/admin/deposits')
@admin_required
def view_deposits():
    """View all deposit requests - Admin only"""
    try:
        logger.debug("Accessing view_deposits route")
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')  # Optional status filter
        
        # Debug: Check if DepositRequest model exists and has data
        total_deposits = DepositRequest.query.count()
        logger.debug(f"Total deposits in database: {total_deposits}")
        
        # Build query with optional filters
        deposits_query = DepositRequest.query
        
        # Apply status filter if provided
        if status_filter and status_filter in ['Pending', 'Approved', 'Rejected']:
            deposits_query = deposits_query.filter(DepositRequest.status == status_filter)
            logger.debug(f"Filtering by status: {status_filter}")
        
        # Get deposits with pagination
        deposits = deposits_query.order_by(DepositRequest.created_at.desc()).paginate(
            page=page,
            per_page=20,
            error_out=False
        )
        
        logger.debug(f"Deposits found for page {page}: {len(deposits.items)}")
        
        # Debug: Log first few deposits with user info
        for i, deposit in enumerate(deposits.items[:3]):
            user = User.query.get(deposit.user_id) if deposit.user_id else None
            logger.debug(f"Deposit {i}: ID={deposit.id}, Status={deposit.status}, Amount=${deposit.amount}, User={user.nickname if user else 'Unknown'}")
        
        # If no deposits found, let's check what's in the database
        if not deposits.items:
            all_deposits = DepositRequest.query.all()
            logger.debug(f"Raw deposits query returned: {len(all_deposits)} items")
            for dep in all_deposits[:5]:  # Log first 5 for debugging
                user = User.query.get(dep.user_id) if dep.user_id else None
                logger.debug(f"Deposit ID: {dep.id}, Amount: {dep.amount}, Status: {dep.status}, User ID: {dep.user_id}, User: {user.nickname if user else 'Unknown'}")
        
        return render_template('admin_deposits.html', deposits=deposits, current_status=status_filter)
        
    except Exception as e:
        logger.error(f"Error in view_deposits: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Error loading deposits: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# APPROVE DEPOSIT - Individual deposit approval (IMPROVED)
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
            # Start transaction
            try:
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
                    
                    # Commit all changes together
                    db.session.commit()
                    flash(f"Deposit of ${deposit.amount} approved for user {user.nickname}.", "success")
                else:
                    logger.error(f"User {deposit.user_id} not found")
                    db.session.rollback()
                    flash("User not found", "error")
                    
            except Exception as db_error:
                logger.error(f"Database error during approval: {str(db_error)}")
                db.session.rollback()
                flash(f"Database error: {str(db_error)}", "error")
                
        else:
            logger.warning(f"Deposit {deposit_id} already processed with status: {deposit.status}")
            flash("Deposit has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing deposit: {str(e)}", "error")
    
    return redirect(url_for('view_deposits'))

# REJECT DEPOSIT (IMPROVED)
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
            try:
                deposit.status = 'Rejected'
                deposit.processed_at = datetime.utcnow()
                deposit.processed_by = admin.id
                deposit.admin_notes = request.form.get('admin_notes', '')
                
                db.session.commit()
                flash(f"Deposit of ${deposit.amount} rejected.", "success")
                
            except Exception as db_error:
                logger.error(f"Database error during rejection: {str(db_error)}")
                db.session.rollback()
                flash(f"Database error: {str(db_error)}", "error")
        else:
            logger.warning(f"Deposit {deposit_id} already processed with status: {deposit.status}")
            flash("Deposit has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing deposit: {str(e)}", "error")
    
    return redirect(url_for('view_deposits'))

# VIEW WITHDRAWALS - Main listing page (IMPROVED)
@app.route('/admin/withdrawals')
@admin_required
def view_withdrawals():
    """View all withdrawal requests - Admin only"""
    try:
        logger.debug("Accessing view_withdrawals route")
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')  # Optional status filter
        
        # Debug: Check if WithdrawalRequest model exists and has data
        total_withdrawals = WithdrawalRequest.query.count()
        logger.debug(f"Total withdrawals in database: {total_withdrawals}")
        
        # Build query with optional filters
        withdrawals_query = WithdrawalRequest.query
        
        # Apply status filter if provided
        if status_filter and status_filter in ['Pending', 'Approved', 'Rejected']:
            withdrawals_query = withdrawals_query.filter(WithdrawalRequest.status == status_filter)
            logger.debug(f"Filtering by status: {status_filter}")
        
        # Get withdrawals with pagination
        withdrawals = withdrawals_query.order_by(WithdrawalRequest.created_at.desc()).paginate(
            page=page,
            per_page=20,
            error_out=False
        )
        
        logger.debug(f"Withdrawals found for page {page}: {len(withdrawals.items)}")
        
        # Debug: Log first few withdrawals with user info
        for i, withdrawal in enumerate(withdrawals.items[:3]):
            user = User.query.get(withdrawal.user_id) if withdrawal.user_id else None
            logger.debug(f"Withdrawal {i}: ID={withdrawal.id}, Status={withdrawal.status}, Amount=${withdrawal.amount}, User={user.nickname if user else 'Unknown'}")
        
        # If no withdrawals found, let's check what's in the database
        if not withdrawals.items:
            all_withdrawals = WithdrawalRequest.query.all()
            logger.debug(f"Raw withdrawals query returned: {len(all_withdrawals)} items")
            for wd in all_withdrawals[:5]:  # Log first 5 for debugging
                user = User.query.get(wd.user_id) if wd.user_id else None
                logger.debug(f"Withdrawal ID: {wd.id}, Amount: {wd.amount}, Status: {wd.status}, User ID: {wd.user_id}, User: {user.nickname if user else 'Unknown'}")
        
        return render_template('admin_withdrawals.html', withdrawals=withdrawals, current_status=status_filter)
        
    except Exception as e:
        logger.error(f"Error in view_withdrawals: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Error loading withdrawals: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# APPROVE WITHDRAWAL - Individual withdrawal approval (IMPROVED)
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
            try:
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
                
            except Exception as db_error:
                logger.error(f"Database error during withdrawal approval: {str(db_error)}")
                db.session.rollback()
                flash(f"Database error: {str(db_error)}", "error")
        else:
            logger.warning(f"Withdrawal {withdrawal_id} already processed with status: {withdrawal.status}")
            flash("Withdrawal has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing withdrawal: {str(e)}", "error")
    
    return redirect(url_for('view_withdrawals'))

# REJECT WITHDRAWAL (IMPROVED)
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
            try:
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
                    db.session.rollback()
                    flash("User not found", "error")
                    
            except Exception as db_error:
                logger.error(f"Database error during withdrawal rejection: {str(db_error)}")
                db.session.rollback()
                flash(f"Database error: {str(db_error)}", "error")
        else:
            logger.warning(f"Withdrawal {withdrawal_id} already processed with status: {withdrawal.status}")
            flash("Withdrawal has already been processed.", "warning")
    
    except Exception as e:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing withdrawal: {str(e)}", "error")
    
    return redirect(url_for('view_withdrawals'))

# ADDITIONAL DEBUGGING ROUTES - Add these temporarily to check your data
@app.route('/admin/debug/data')
@admin_required
def debug_data():
    """Debugging route to check database contents"""
    try:
        # Check deposits
        deposits = DepositRequest.query.all()
        deposit_info = []
        for d in deposits:
            user = User.query.get(d.user_id)
            deposit_info.append({
                'id': d.id,
                'amount': float(d.amount) if d.amount else 0,
                'status': d.status,
                'user_id': d.user_id,
                'user_nickname': user.nickname if user else 'Unknown',
                'created_at': d.created_at.strftime('%Y-%m-%d %H:%M:%S') if d.created_at else None,
                'processed_at': d.processed_at.strftime('%Y-%m-%d %H:%M:%S') if d.processed_at else None
            })
        
        # Check withdrawals
        withdrawals = WithdrawalRequest.query.all()
        withdrawal_info = []
        for w in withdrawals:
            user = User.query.get(w.user_id)
            withdrawal_info.append({
                'id': w.id,
                'amount': float(w.amount) if w.amount else 0,
                'status': w.status,
                'user_id': w.user_id,
                'user_nickname': user.nickname if user else 'Unknown',
                'created_at': w.created_at.strftime('%Y-%m-%d %H:%M:%S') if w.created_at else None,
                'processed_at': w.processed_at.strftime('%Y-%m-%d %H:%M:%S') if w.processed_at else None,
                'wallet_address': getattr(w, 'wallet_address', 'N/A')
            })
        
        # Check users
        users = User.query.all()
        user_info = []
        for u in users[:10]:  # First 10 users
            user_info.append({
                'id': u.id,
                'nickname': u.nickname,
                'email': u.email,
                'balance': float(u.balance) if u.balance else 0,
                'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(u, 'created_at') and u.created_at else None
            })
        
        return jsonify({
            'deposits': deposit_info,
            'withdrawals': withdrawal_info,
            'users': user_info,
            'total_deposits': len(deposits),
            'total_withdrawals': len(withdrawals),
            'total_users': len(users),
            'pending_deposits': len([d for d in deposits if d.status == 'Pending']),
            'pending_withdrawals': len([w for w in withdrawals if w.status == 'Pending'])
        })
        
    except Exception as e:
        logger.error(f"Debug data error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/admin/debug/models')
@admin_required
def debug_models():
    """Check if models are properly defined"""
    try:
        # Check DepositRequest model structure
        deposit_columns = []
        if hasattr(DepositRequest, '__table__'):
            deposit_columns = [col.name for col in DepositRequest.__table__.columns]
        
        # Check WithdrawalRequest model structure
        withdrawal_columns = []
        if hasattr(WithdrawalRequest, '__table__'):
            withdrawal_columns = [col.name for col in WithdrawalRequest.__table__.columns]
            
        # Check User model structure
        user_columns = []
        if hasattr(User, '__table__'):
            user_columns = [col.name for col in User.__table__.columns]
        
        return jsonify({
            'deposit_model_columns': deposit_columns,
            'withdrawal_model_columns': withdrawal_columns,
            'user_model_columns': user_columns,
            'deposit_model_exists': hasattr(DepositRequest, '__table__'),
            'withdrawal_model_exists': hasattr(WithdrawalRequest, '__table__'),
            'user_model_exists': hasattr(User, '__table__')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

# BATCH OPERATIONS - Useful for admin efficiency
@app.route('/admin/deposits/bulk-action', methods=['POST'])
@admin_required
def bulk_deposit_action():
    """Handle bulk actions on deposits"""
    try:
        action = request.form.get('action')
        deposit_ids = request.form.getlist('deposit_ids')
        admin_notes = request.form.get('bulk_admin_notes', '')
        
        if not action or not deposit_ids:
            flash('Please select an action and at least one deposit.', 'error')
            return redirect(url_for('view_deposits'))
        
        admin = Admin.query.get(session.get('admin_id'))
        if not admin:
            flash('Admin session invalid', 'error')
            return redirect(url_for('admin_login'))
        
        processed_count = 0
        error_count = 0
        
        for deposit_id in deposit_ids:
            try:
                deposit = DepositRequest.query.get(int(deposit_id))
                if not deposit or deposit.status != 'Pending':
                    continue
                
                if action == 'approve':
                    deposit.status = 'Approved'
                    deposit.processed_at = datetime.utcnow()
                    deposit.processed_by = admin.id
                    deposit.admin_notes = admin_notes
                    
                    # Update user balance
                    user = User.query.get(deposit.user_id)
                    if user:
                        user.balance += deposit.amount
                        processed_count += 1
                    else:
                        error_count += 1
                        
                elif action == 'reject':
                    deposit.status = 'Rejected'
                    deposit.processed_at = datetime.utcnow()
                    deposit.processed_by = admin.id
                    deposit.admin_notes = admin_notes
                    processed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
                error_count += 1
        
        db.session.commit()
        
        if processed_count > 0:
            flash(f'Successfully {action}d {processed_count} deposits.', 'success')
        if error_count > 0:
            flash(f'{error_count} deposits had errors and were not processed.', 'warning')
            
    except Exception as e:
        logger.error(f"Bulk deposit action error: {str(e)}")
        db.session.rollback()
        flash(f'Error processing bulk action: {str(e)}', 'error')
    
    return redirect(url_for('view_deposits'))

@app.route('/admin/withdrawals/bulk-action', methods=['POST'])
@admin_required
def bulk_withdrawal_action():
    """Handle bulk actions on withdrawals"""
    try:
        action = request.form.get('action')
        withdrawal_ids = request.form.getlist('withdrawal_ids')
        admin_notes = request.form.get('bulk_admin_notes', '')
        
        if not action or not withdrawal_ids:
            flash('Please select an action and at least one withdrawal.', 'error')
            return redirect(url_for('view_withdrawals'))
        
        admin = Admin.query.get(session.get('admin_id'))
        if not admin:
            flash('Admin session invalid', 'error')
            return redirect(url_for('admin_login'))
        
        processed_count = 0
        error_count = 0
        
        for withdrawal_id in withdrawal_ids:
            try:
                withdrawal = WithdrawalRequest.query.get(int(withdrawal_id))
                if not withdrawal or withdrawal.status != 'Pending':
                    continue
                
                if action == 'approve':
                    withdrawal.status = 'Approved'
                    withdrawal.processed_at = datetime.utcnow()
                    withdrawal.processed_by = admin.id
                    withdrawal.admin_notes = admin_notes
                    processed_count += 1
                    
                elif action == 'reject':
                    withdrawal.status = 'Rejected'
                    withdrawal.processed_at = datetime.utcnow()
                    withdrawal.processed_by = admin.id
                    withdrawal.admin_notes = admin_notes
                    
                    # Refund amount to user balance
                    user = User.query.get(withdrawal.user_id)
                    if user:
                        user.balance += withdrawal.amount
                        processed_count += 1
                    else:
                        error_count += 1
                        
            except Exception as e:
                logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
                error_count += 1
        
        db.session.commit()
        
        if processed_count > 0:
            flash(f'Successfully {action}d {processed_count} withdrawals.', 'success')
        if error_count > 0:
            flash(f'{error_count} withdrawals had errors and were not processed.', 'warning')
            
    except Exception as e:
        logger.error(f"Bulk withdrawal action error: {str(e)}")
        db.session.rollback()
        flash(f'Error processing bulk action: {str(e)}', 'error')
    
    return redirect(url_for('view_withdrawals'))
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
# Optional: Create a logout decorator for sensitive routes
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('profile'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Logout route - clears user session and redirects to login page
    Supports both GET and POST requests for flexibility
    """
    try:
        # Get user info before clearing session (for logging purposes)
        user_id = session.get('user_id')
        username = session.get('username', 'Unknown')
        
        # Clear all session data
        session.clear()
        
        # Optional: Add flash message
        flash('You have been successfully logged out.', 'success')
        
        # Optional: Log the logout action
        if user_id:
            print(f"User {username} (ID: {user_id}) logged out successfully")
            # You can also log to your database here if you have a logging system
        
        # Handle AJAX requests
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Logged out successfully',
                'redirect': url_for('login')
            })
        
        # Redirect to login page
        return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        # Even if there's an error, clear the session and redirect
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('login'))
