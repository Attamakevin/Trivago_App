# hotel_app/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from hotel_app import app, db
from hotel_app.models import User, Hotel, Reservation, DepositRequest, WithdrawalRequest, EventAd, Admin, InvitationCode
from datetime import datetime, date
from flask_login import login_required
from functools import wraps
import string
import random
import logging
@app.route('/')
def home():
    return render_template('home.html')
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from hotel_app import db
 # ✅ Only import User now


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
                return redirect(url_for('set_withdrawal_password'))
            
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
                return render_template('set_password.html')
            
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
            db.session.rollback()
            flash(f'Error setting password: {str(e)}', 'error')
            return render_template('set_password.html')
    
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

# Admin Routes - Complete and Organized
from functools import wraps
from flask import session, flash, redirect, url_for, request, render_template, jsonify
from datetime import datetime
import string
import random
import logging

# Assuming these imports based on the code structure
from hotel_app.models import Admin, User, DepositRequest, WithdrawalRequest, Hotel, InvitationCode, UserHotelAssignment, Reservation
from hotel_app import app, db

logger = logging.getLogger(__name__)

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

# ============= AUTHENTICATION ROUTES =============

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

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Admin logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

# ============= DASHBOARD =============

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        # Get statistics for dashboard
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_deposits = DepositRequest.query.count()
        pending_deposits = DepositRequest.query.filter_by(status='pending').count()
        total_withdrawals = WithdrawalRequest.query.count()
        pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
        total_hotels = Hotel.query.count()
        active_hotels = Hotel.query.filter_by(is_active=True).count()
        total_reservations = Reservation.query.count()
        
        # Recent activities
        recent_users = User.query.order_by(User.id.desc()).limit(5).all()
        recent_deposits = DepositRequest.query.order_by(DepositRequest.id.desc()).limit(5).all()
        recent_withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.id.desc()).limit(5).all()
        recent_reservations = Reservation.query.order_by(Reservation.id.desc()).limit(5).all()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'total_deposits': total_deposits,
            'pending_deposits': pending_deposits,
            'total_withdrawals': total_withdrawals,
            'pending_withdrawals': pending_withdrawals,
            'total_hotels': total_hotels,
            'active_hotels': active_hotels,
            'total_reservations': total_reservations,
        }
        
        return render_template('admin_dashboard.html', 
                             stats=stats,
                             recent_users=recent_users,
                             recent_deposits=recent_deposits,
                             recent_withdrawals=recent_withdrawals,
                             recent_reservations=recent_reservations)
    
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        flash('Error loading dashboard data', 'error')
        return render_template('admin_dashboard.html', stats={})

# ============= USER MANAGEMENT =============

@app.route('/admin/users')
@admin_required
def view_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    vip_filter = request.args.get('vip_level', '')
    session_filter = request.args.get('session', '')
    
    users_query = User.query
    
    if search:
        users_query = users_query.filter(
            User.nickname.contains(search) | 
            User.user_id.contains(search) |
            User.contact.contains(search)
        )
    
    if vip_filter:
        users_query = users_query.filter(User.vip_level == vip_filter)
    
    if session_filter:
        users_query = users_query.filter(User.current_session == session_filter)
    
    users = users_query.order_by(User.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    vip_levels = ['VIP0', 'VIP1', 'VIP2', 'VIP3']
    session_types = ['first', 'second']
    
    return render_template('admin_users.html', 
                         users=users, 
                         search=search, 
                         vip_levels=vip_levels,
                         session_types=session_types,
                         current_vip_filter=vip_filter,
                         current_session_filter=session_filter)

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
    
    valid_vip_levels = ['VIP0', 'VIP1', 'VIP2', 'VIP3']
    if new_vip_level not in valid_vip_levels:
        flash("Invalid VIP level selected.", "error")
        return redirect(url_for('view_users'))
    
    old_vip_level = user.vip_level
    user.vip_level = new_vip_level
    db.session.commit()
    
    flash(f"User {user.nickname} VIP level updated from {old_vip_level} to {new_vip_level}.", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/users/<int:user_id>/reset_session', methods=['POST'])
@admin_required
def reset_user_session(user_id):
    user = User.query.get_or_404(user_id)
    new_session = request.form.get('session_type', 'first')
    
    if new_session not in ['first', 'second']:
        flash("Invalid session type.", "error")
        return redirect(url_for('view_users'))
    
    user.reset_session_by_admin(new_session)
    flash(f"User {user.nickname} session reset to {new_session}.", "success")
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
            
            original_balance = user.balance
            
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
        
        elif action == 'pay_commission':
            admin = Admin.query.get(session.get('admin_id'))
            amount = request.form.get('amount')
            
            if amount:
                try:
                    amount = float(amount)
                    if admin.pay_user_commission(user_id, amount):
                        flash(f"Commission of ${amount:.2f} paid to user.", "success")
                    else:
                        flash("No unpaid commissions found.", "warning")
                except ValueError:
                    flash("Invalid amount format.", "error")
            else:
                # Pay all unpaid commissions
                if admin.pay_user_commission(user_id):
                    flash("All unpaid commissions have been paid.", "success")
                else:
                    flash("No unpaid commissions found.", "warning")
            
            return redirect(url_for('view_user_details', user_id=user_id))
    
    # GET request - display user details
    deposits = DepositRequest.query.filter_by(user_id=user_id).order_by(DepositRequest.id.desc()).all()
    withdrawals = WithdrawalRequest.query.filter_by(user_id=user_id).order_by(WithdrawalRequest.id.desc()).all()
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.id.desc()).all()
    hotel_assignments = UserHotelAssignment.query.filter_by(user_id=user_id).all()
    
    vip_levels = ['VIP0', 'VIP1', 'VIP2', 'VIP3']
    session_types = ['first', 'second']
    
    # Get commission summary
    commission_summary = user.get_commission_summary()
    
    return render_template('admin_user_details.html', 
                         user=user, 
                         deposits=deposits, 
                         withdrawals=withdrawals,
                         reservations=reservations,
                         hotel_assignments=hotel_assignments,
                         vip_levels=vip_levels,
                         session_types=session_types,
                         commission_summary=commission_summary)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    username = user.nickname
    
    try:
        # Delete related records first
        UserHotelAssignment.query.filter_by(user_id=user_id).delete()
        Reservation.query.filter_by(user_id=user_id).delete()
        DepositRequest.query.filter_by(user_id=user_id).delete()
        WithdrawalRequest.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        flash(f"User {username} and all related data have been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "error")
    
    return redirect(url_for('view_users'))

# ============= DEPOSIT MANAGEMENT =============

@app.route('/admin/deposits')
@admin_required
def view_deposits():
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        
        deposits_query = DepositRequest.query
        
        if status_filter and status_filter in ['pending', 'approved', 'rejected']:
            deposits_query = deposits_query.filter(DepositRequest.status == status_filter)
        
        deposits = deposits_query.order_by(DepositRequest.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin_deposits.html', deposits=deposits, current_status=status_filter)
        
    except Exception as e:
        logger.error(f"Error in view_deposits: {str(e)}")
        flash(f'Error loading deposits: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/deposits/<int:deposit_id>/approve', methods=['POST'])
@admin_required
def approve_deposit(deposit_id):
    try:
        deposit = DepositRequest.query.get_or_404(deposit_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if deposit.status != 'pending':
            flash("Deposit has already been processed.", "warning")
            return redirect(url_for('view_deposits'))
        
        deposit.status = 'approved'
        deposit.processed_at = datetime.utcnow()
        deposit.processed_by = admin.id
        deposit.admin_notes = request.form.get('admin_notes', '')
        
        # Update user balance
        user = User.query.get(deposit.user_id)
        if user:
            user.balance += deposit.amount
            db.session.commit()
            flash(f"Deposit of ${deposit.amount} approved for user {user.nickname}.", "success")
        else:
            db.session.rollback()
            flash("User not found", "error")
            
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing deposit: {str(e)}", "error")
    
    return redirect(url_for('view_deposits'))

@app.route('/admin/deposits/<int:deposit_id>/reject', methods=['POST'])
@admin_required
def reject_deposit(deposit_id):
    try:
        deposit = DepositRequest.query.get_or_404(deposit_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if deposit.status != 'pending':
            flash("Deposit has already been processed.", "warning")
            return redirect(url_for('view_deposits'))
        
        deposit.status = 'rejected'
        deposit.processed_at = datetime.utcnow()
        deposit.processed_by = admin.id
        deposit.admin_notes = request.form.get('admin_notes', '')
        
        db.session.commit()
        flash(f"Deposit of ${deposit.amount} rejected.", "success")
                
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing deposit: {str(e)}", "error")
    
    return redirect(url_for('view_deposits'))

# ============= WITHDRAWAL MANAGEMENT =============

@app.route('/admin/withdrawals')
@admin_required
def view_withdrawals():
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        
        withdrawals_query = WithdrawalRequest.query
        
        if status_filter and status_filter in ['pending', 'approved', 'rejected']:
            withdrawals_query = withdrawals_query.filter(WithdrawalRequest.status == status_filter)
        
        withdrawals = withdrawals_query.order_by(WithdrawalRequest.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin_withdrawals.html', withdrawals=withdrawals, current_status=status_filter)
        
    except Exception as e:
        logger.error(f"Error in view_withdrawals: {str(e)}")
        flash(f'Error loading withdrawals: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/withdrawals/<int:withdrawal_id>/approve', methods=['POST'])
@admin_required
def approve_withdrawal(withdrawal_id):
    try:
        withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if withdrawal.status != 'pending':
            flash("Withdrawal has already been processed.", "warning")
            return redirect(url_for('view_withdrawals'))
        
        withdrawal.status = 'approved'
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.processed_by = admin.id
        withdrawal.admin_notes = request.form.get('admin_notes', '')
        withdrawal.transaction_hash = request.form.get('transaction_hash', '')
        
        # Handle transaction fee
        try:
            transaction_fee = float(request.form.get('transaction_fee', 0))
            withdrawal.transaction_fee = transaction_fee
        except (ValueError, TypeError):
            withdrawal.transaction_fee = 0.0
        
        db.session.commit()
        flash(f"Withdrawal of ${withdrawal.amount} approved.", "success")
                
    except Exception as e:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing withdrawal: {str(e)}", "error")
    
    return redirect(url_for('view_withdrawals'))

@app.route('/admin/withdrawals/<int:withdrawal_id>/reject', methods=['POST'])
@admin_required
def reject_withdrawal(withdrawal_id):
    try:
        withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
        admin = Admin.query.get(session.get('admin_id'))
        
        if withdrawal.status != 'pending':
            flash("Withdrawal has already been processed.", "warning")
            return redirect(url_for('view_withdrawals'))
        
        withdrawal.status = 'rejected'
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.processed_by = admin.id
        withdrawal.admin_notes = request.form.get('admin_notes', '')
        withdrawal.rejection_reason = request.form.get('rejection_reason', '')
        
        # Refund the amount to user's balance
        user = User.query.get(withdrawal.user_id)
        if user:
            user.balance += withdrawal.amount
            db.session.commit()
            flash(f"Withdrawal of ${withdrawal.amount} rejected and amount refunded.", "success")
        else:
            db.session.rollback()
            flash("User not found", "error")
                    
    except Exception as e:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        db.session.rollback()
        flash(f"Error processing withdrawal: {str(e)}", "error")
    
    return redirect(url_for('view_withdrawals'))

# ============= HOTEL MANAGEMENT =============

@app.route('/admin/hotels', methods=['GET', 'POST'])
@admin_required
def manage_hotels():
    if request.method == 'POST':
        try:
            name = request.form['name']
            primary_picture = request.form['primary_picture']
            price = float(request.form['price'])
            commission_multiplier = float(request.form.get('commission_multiplier', 1.0))
            days_available = int(request.form.get('days_available', 1))
            description = request.form.get('description', '')
            location = request.form.get('location', '')
            category = request.form.get('category', 'regular')
            rating = int(request.form.get('rating', 5))

            new_hotel = Hotel(
                name=name,
                primary_picture=primary_picture,
                price=price,
                commission_multiplier=commission_multiplier,
                days_available=days_available,
                description=description,
                location=location,
                category=category,
                rating=rating
            )
            db.session.add(new_hotel)
            db.session.commit()
            flash('Hotel added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding hotel: {str(e)}', 'error')
        
        return redirect(url_for('manage_hotels'))

    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '')
    
    hotels_query = Hotel.query
    if category_filter:
        hotels_query = hotels_query.filter_by(category=category_filter)
    
    hotels = hotels_query.order_by(Hotel.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['regular', 'luxury']
    
    return render_template('admin_hotels.html', hotels=hotels, categories=categories, current_category=category_filter)

@app.route('/admin/hotels/<int:hotel_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    
    if request.method == 'POST':
        try:
            hotel.name = request.form['name']
            hotel.primary_picture = request.form['primary_picture']
            hotel.price = float(request.form['price'])
            hotel.commission_multiplier = float(request.form.get('commission_multiplier', 1.0))
            hotel.days_available = int(request.form.get('days_available', 1))
            hotel.description = request.form.get('description', '')
            hotel.location = request.form.get('location', '')
            hotel.category = request.form.get('category', 'regular')
            hotel.rating = int(request.form.get('rating', 5))
            hotel.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            flash('Hotel updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating hotel: {str(e)}', 'error')
        
        return redirect(url_for('manage_hotels'))
    
    return render_template('admin_edit_hotel.html', hotel=hotel)

@app.route('/admin/hotels/<int:hotel_id>/toggle', methods=['POST'])
@admin_required
def toggle_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    hotel.is_active = not hotel.is_active
    db.session.commit()
    
    action = 'activated' if hotel.is_active else 'deactivated'
    flash(f"Hotel {hotel.name} has been {action}.", "success")
    return redirect(url_for('manage_hotels'))

@app.route('/admin/hotels/<int:hotel_id>/delete', methods=['POST'])
@admin_required
def delete_hotel(hotel_id):
    try:
        hotel = Hotel.query.get_or_404(hotel_id)
        hotel_name = hotel.name
        
        # Delete related records first
        UserHotelAssignment.query.filter_by(hotel_id=hotel_id).delete()
        Reservation.query.filter_by(hotel_id=hotel_id).delete()
        
        # Delete hotel
        db.session.delete(hotel)
        db.session.commit()
        flash(f'Hotel "{hotel_name}" and all related data deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting hotel: {str(e)}', 'error')
    
    return redirect(url_for('manage_hotels'))

# ============= HOTEL ASSIGNMENT MANAGEMENT =============

@app.route('/admin/hotel-assignments')
@admin_required
def view_hotel_assignments():
    page = request.args.get('page', 1, type=int)
    user_filter = request.args.get('user_id', '')
    session_filter = request.args.get('session_type', '')
    
    assignments_query = UserHotelAssignment.query
    
    if user_filter:
        assignments_query = assignments_query.filter_by(user_id=user_filter)
    
    if session_filter:
        assignments_query = assignments_query.filter_by(session_type=session_filter)
    
    assignments = assignments_query.order_by(UserHotelAssignment.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    users = User.query.filter_by(is_active=True).all()
    session_types = ['first', 'second']
    
    return render_template('admin_hotel_assignments.html', 
                         assignments=assignments, 
                         users=users, 
                         session_types=session_types,
                         current_user_filter=user_filter,
                         current_session_filter=session_filter)

@app.route('/admin/hotel-assignments/create', methods=['GET', 'POST'])
@admin_required
def create_hotel_assignment():
    if request.method == 'POST':
        try:
            user_id = int(request.form['user_id'])
            hotel_id = int(request.form['hotel_id'])
            session_type = request.form['session_type']
            custom_commission = float(request.form['custom_commission'])
            
            admin = Admin.query.get(session.get('admin_id'))
            
            # Check if assignment already exists
            existing = UserHotelAssignment.query.filter_by(
                user_id=user_id,
                hotel_id=hotel_id,
                session_type=session_type
            ).first()
            
            if existing:
                flash("Assignment already exists for this user-hotel-session combination.", "warning")
                return redirect(url_for('create_hotel_assignment'))
            
            assignment = UserHotelAssignment(
                user_id=user_id,
                hotel_id=hotel_id,
                session_type=session_type,
                custom_commission=custom_commission,
                assigned_by=admin.id
            )
            
            db.session.add(assignment)
            db.session.commit()
            flash('Hotel assignment created successfully', 'success')
            return redirect(url_for('view_hotel_assignments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating assignment: {str(e)}', 'error')
    
    users = User.query.filter_by(is_active=True).all()
    hotels = Hotel.query.filter_by(is_active=True).all()
    session_types = ['first', 'second']
    
    return render_template('admin_create_hotel_assignment.html', 
                         users=users, 
                         hotels=hotels, 
                         session_types=session_types)

@app.route('/admin/hotel-assignments/<int:assignment_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_hotel_assignment(assignment_id):
    assignment = UserHotelAssignment.query.get_or_404(assignment_id)
    
    if request.method == 'POST':
        try:
            assignment.custom_commission = float(request.form['custom_commission'])
            db.session.commit()
            flash('Hotel assignment updated successfully', 'success')
            return redirect(url_for('view_hotel_assignments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating assignment: {str(e)}', 'error')
    
    return render_template('admin_edit_hotel_assignment.html', assignment=assignment)

@app.route('/admin/hotel-assignments/<int:assignment_id>/delete', methods=['POST'])
@admin_required
def delete_hotel_assignment(assignment_id):
    try:
        assignment = UserHotelAssignment.query.get_or_404(assignment_id)
        db.session.delete(assignment)
        db.session.commit()
        flash('Hotel assignment deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting assignment: {str(e)}', 'error')
    
    return redirect(url_for('view_hotel_assignments'))
# ============= BULK HOTEL ASSIGNMENT ROUTES =============

@app.route('/admin/bulk-hotel-assignment', methods=['GET', 'POST'])
@admin_required
def bulk_hotel_assignment():
    if request.method == 'POST':
        try:
            # Get form data
            user_ids = request.form.getlist('user_ids')
            hotel_ids = request.form.getlist('hotel_ids')
            session_type = request.form.get('session_type', 'first')
            custom_commission = float(request.form.get('custom_commission', 0))
            replace_existing = request.form.get('replace_existing') == 'on'
            
            if not user_ids or not hotel_ids:
                flash("Please select at least one user and one hotel.", "error")
                return redirect(url_for('bulk_hotel_assignment'))
            
            admin = Admin.query.get(session.get('admin_id'))
            assignments_created = 0
            assignments_updated = 0
            assignments_skipped = 0
            
            # Process each user-hotel combination
            for user_id in user_ids:
                for hotel_id in hotel_ids:
                    user_id = int(user_id)
                    hotel_id = int(hotel_id)
                    
                    # Check if assignment already exists
                    existing = UserHotelAssignment.query.filter_by(
                        user_id=user_id,
                        hotel_id=hotel_id,
                        session_type=session_type
                    ).first()
                    
                    if existing:
                        if replace_existing:
                            existing.custom_commission = custom_commission
                            existing.assigned_by = admin.id
                            existing.updated_at = datetime.utcnow()
                            assignments_updated += 1
                        else:
                            assignments_skipped += 1
                    else:
                        # Create new assignment
                        assignment = UserHotelAssignment(
                            user_id=user_id,
                            hotel_id=hotel_id,
                            session_type=session_type,
                            custom_commission=custom_commission,
                            assigned_by=admin.id
                        )
                        db.session.add(assignment)
                        assignments_created += 1
            
            db.session.commit()
            
            # Log the bulk operation
            log_admin_action(
                "Bulk Hotel Assignment",
                f"Created: {assignments_created}, Updated: {assignments_updated}, Skipped: {assignments_skipped}"
            )
            
            flash(f"Bulk assignment completed! Created: {assignments_created}, Updated: {assignments_updated}, Skipped: {assignments_skipped}", "success")
            return redirect(url_for('view_hotel_assignments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error in bulk assignment: {str(e)}', 'error')
    
    # GET request - show the form
    users = User.query.filter_by(is_active=True).order_by(User.nickname).all()
    hotels = Hotel.query.filter_by(is_active=True).order_by(Hotel.name).all()
    session_types = ['first', 'second']
    
    # Get price ranges for filtering
    min_price = db.session.query(db.func.min(Hotel.price)).filter_by(is_active=True).scalar() or 0
    max_price = db.session.query(db.func.max(Hotel.price)).filter_by(is_active=True).scalar() or 1000
    
    # Get hotel categories
    categories = db.session.query(Hotel.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('admin_bulk_hotel_assignment.html',
                         users=users,
                         hotels=hotels,
                         session_types=session_types,
                         min_price=min_price,
                         max_price=max_price,
                         categories=categories)

@app.route('/admin/api/hotels-by-criteria')
@admin_required
def get_hotels_by_criteria():
    """API endpoint to get hotels based on price range and other criteria"""
    try:
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        category = request.args.get('category', '')
        rating = request.args.get('rating', type=int)
        
        hotels_query = Hotel.query.filter_by(is_active=True)
        
        # Apply price range filter
        if min_price is not None:
            hotels_query = hotels_query.filter(Hotel.price >= min_price)
        if max_price is not None:
            hotels_query = hotels_query.filter(Hotel.price <= max_price)
        
        # Apply category filter
        if category:
            hotels_query = hotels_query.filter(Hotel.category == category)
        
        # Apply rating filter
        if rating is not None:
            hotels_query = hotels_query.filter(Hotel.rating >= rating)
        
        hotels = hotels_query.order_by(Hotel.name).all()
        
        hotels_data = []
        for hotel in hotels:
            hotels_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'price': hotel.price,
                'category': hotel.category,
                'rating': hotel.rating,
                'location': hotel.location,
                'commission_multiplier': hotel.commission_multiplier
            })
        
        return jsonify({
            'hotels': hotels_data,
            'count': len(hotels_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/users-by-criteria')
@admin_required
def get_users_by_criteria():
    """API endpoint to get users based on VIP level and other criteria"""
    try:
        vip_level = request.args.get('vip_level', '')
        session_type = request.args.get('session_type', '')
        min_balance = request.args.get('min_balance', type=float)
        max_balance = request.args.get('max_balance', type=float)
        
        users_query = User.query.filter_by(is_active=True)
        
        # Apply VIP level filter
        if vip_level:
            users_query = users_query.filter(User.vip_level == vip_level)
        
        # Apply session type filter
        if session_type:
            users_query = users_query.filter(User.current_session == session_type)
        
        # Apply balance range filter
        if min_balance is not None:
            users_query = users_query.filter(User.balance >= min_balance)
        if max_balance is not None:
            users_query = users_query.filter(User.balance <= max_balance)
        
        users = users_query.order_by(User.nickname).all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'nickname': user.nickname,
                'user_id': user.user_id,
                'vip_level': user.vip_level,
                'current_session': user.current_session,
                'balance': user.balance
            })
        
        return jsonify({
            'users': users_data,
            'count': len(users_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/bulk-assignment-preview', methods=['POST'])
@admin_required
def bulk_assignment_preview():
    """Preview bulk assignment before execution"""
    try:
        # Get criteria from form
        min_price = request.form.get('min_price', type=float)
        max_price = request.form.get('max_price', type=float)
        category = request.form.get('category', '')
        rating = request.form.get('rating', type=int)
        vip_level = request.form.get('vip_level', '')
        session_type = request.form.get('session_type', 'first')
        user_session_filter = request.form.get('user_session_filter', '')
        
        # Get hotels based on criteria
        hotels_query = Hotel.query.filter_by(is_active=True)
        
        if min_price is not None:
            hotels_query = hotels_query.filter(Hotel.price >= min_price)
        if max_price is not None:
            hotels_query = hotels_query.filter(Hotel.price <= max_price)
        if category:
            hotels_query = hotels_query.filter(Hotel.category == category)
        if rating is not None:
            hotels_query = hotels_query.filter(Hotel.rating >= rating)
        
        hotels = hotels_query.order_by(Hotel.name).all()
        
        # Get users based on criteria
        users_query = User.query.filter_by(is_active=True)
        
        if vip_level:
            users_query = users_query.filter(User.vip_level == vip_level)
        if user_session_filter:
            users_query = users_query.filter(User.current_session == user_session_filter)
        
        users = users_query.order_by(User.nickname).all()
        
        # Calculate existing assignments
        existing_assignments = 0
        if users and hotels:
            user_ids = [u.id for u in users]
            hotel_ids = [h.id for h in hotels]
            
            existing_assignments = UserHotelAssignment.query.filter(
                UserHotelAssignment.user_id.in_(user_ids),
                UserHotelAssignment.hotel_id.in_(hotel_ids),
                UserHotelAssignment.session_type == session_type
            ).count()
        
        preview_data = {
            'users_count': len(users),
            'hotels_count': len(hotels),
            'total_assignments': len(users) * len(hotels),
            'existing_assignments': existing_assignments,
            'new_assignments': (len(users) * len(hotels)) - existing_assignments,
            'users': users[:10],  # Preview first 10 users
            'hotels': hotels[:10],  # Preview first 10 hotels
            'session_type': session_type,
            'criteria': {
                'min_price': min_price,
                'max_price': max_price,
                'category': category,
                'rating': rating,
                'vip_level': vip_level,
                'user_session_filter': user_session_filter
            }
        }
        
        return render_template('admin_bulk_assignment_preview.html', preview=preview_data)
        
    except Exception as e:
        flash(f'Error generating preview: {str(e)}', 'error')
        return redirect(url_for('bulk_hotel_assignment'))

@app.route('/admin/execute-bulk-assignment', methods=['POST'])
@admin_required
def execute_bulk_assignment():
    """Execute the bulk assignment based on criteria"""
    try:
        # Get criteria from form
        min_price = request.form.get('min_price', type=float)
        max_price = request.form.get('max_price', type=float)
        category = request.form.get('category', '')
        rating = request.form.get('rating', type=int)
        vip_level = request.form.get('vip_level', '')
        session_type = request.form.get('session_type', 'first')
        user_session_filter = request.form.get('user_session_filter', '')
        custom_commission = float(request.form.get('custom_commission', 0))
        replace_existing = request.form.get('replace_existing') == 'on'
        
        # Get hotels based on criteria
        hotels_query = Hotel.query.filter_by(is_active=True)
        
        if min_price is not None:
            hotels_query = hotels_query.filter(Hotel.price >= min_price)
        if max_price is not None:
            hotels_query = hotels_query.filter(Hotel.price <= max_price)
        if category:
            hotels_query = hotels_query.filter(Hotel.category == category)
        if rating is not None:
            hotels_query = hotels_query.filter(Hotel.rating >= rating)
        
        hotels = hotels_query.all()
        
        # Get users based on criteria
        users_query = User.query.filter_by(is_active=True)
        
        if vip_level:
            users_query = users_query.filter(User.vip_level == vip_level)
        if user_session_filter:
            users_query = users_query.filter(User.current_session == user_session_filter)
        
        users = users_query.all()
        
        if not users or not hotels:
            flash("No users or hotels found matching the criteria.", "warning")
            return redirect(url_for('bulk_hotel_assignment'))
        
        admin = Admin.query.get(session.get('admin_id'))
        assignments_created = 0
        assignments_updated = 0
        assignments_skipped = 0
        
        # Process each user-hotel combination
        for user in users:
            for hotel in hotels:
                # Check if assignment already exists
                existing = UserHotelAssignment.query.filter_by(
                    user_id=user.id,
                    hotel_id=hotel.id,
                    session_type=session_type
                ).first()
                
                if existing:
                    if replace_existing:
                        existing.custom_commission = custom_commission
                        existing.assigned_by = admin.id
                        existing.updated_at = datetime.utcnow()
                        assignments_updated += 1
                    else:
                        assignments_skipped += 1
                else:
                    # Create new assignment
                    assignment = UserHotelAssignment(
                        user_id=user.id,
                        hotel_id=hotel.id,
                        session_type=session_type,
                        custom_commission=custom_commission,
                        assigned_by=admin.id
                    )
                    db.session.add(assignment)
                    assignments_created += 1
        
        db.session.commit()
        
        # Log the bulk operation
        log_admin_action(
            "Bulk Hotel Assignment by Criteria",
            f"Users: {len(users)}, Hotels: {len(hotels)}, Created: {assignments_created}, Updated: {assignments_updated}, Skipped: {assignments_skipped}"
        )
        
        flash(f"Bulk assignment completed! Processed {len(users)} users and {len(hotels)} hotels. Created: {assignments_created}, Updated: {assignments_updated}, Skipped: {assignments_skipped}", "success")
        return redirect(url_for('view_hotel_assignments'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error executing bulk assignment: {str(e)}', 'error')
        return redirect(url_for('bulk_hotel_assignment'))

@app.route('/admin/bulk-remove-assignments', methods=['POST'])
@admin_required
def bulk_remove_assignments():
    """Remove hotel assignments in bulk based on criteria"""
    try:
        # Get criteria from form
        min_price = request.form.get('min_price', type=float)
        max_price = request.form.get('max_price', type=float)
        category = request.form.get('category', '')
        rating = request.form.get('rating', type=int)
        vip_level = request.form.get('vip_level', '')
        session_type = request.form.get('session_type', 'first')
        user_session_filter = request.form.get('user_session_filter', '')
        
        # Build the query to find assignments to remove
        assignments_query = UserHotelAssignment.query.join(Hotel).join(User)
        
        # Apply hotel criteria
        if min_price is not None:
            assignments_query = assignments_query.filter(Hotel.price >= min_price)
        if max_price is not None:
            assignments_query = assignments_query.filter(Hotel.price <= max_price)
        if category:
            assignments_query = assignments_query.filter(Hotel.category == category)
        if rating is not None:
            assignments_query = assignments_query.filter(Hotel.rating >= rating)
        
        # Apply user criteria
        if vip_level:
            assignments_query = assignments_query.filter(User.vip_level == vip_level)
        if user_session_filter:
            assignments_query = assignments_query.filter(User.current_session == user_session_filter)
        
        # Apply session type filter
        assignments_query = assignments_query.filter(UserHotelAssignment.session_type == session_type)
        
        assignments_to_remove = assignments_query.all()
        
        if not assignments_to_remove:
            flash("No assignments found matching the criteria.", "warning")
            return redirect(url_for('bulk_hotel_assignment'))
        
        # Remove the assignments
        for assignment in assignments_to_remove:
            db.session.delete(assignment)
        
        db.session.commit()
        
        # Log the bulk removal
        log_admin_action(
            "Bulk Hotel Assignment Removal",
            f"Removed {len(assignments_to_remove)} assignments based on criteria"
        )
        
        flash(f"Successfully removed {len(assignments_to_remove)} hotel assignments.", "success")
        return redirect(url_for('view_hotel_assignments'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing assignments: {str(e)}', 'error')
        return redirect(url_for('bulk_hotel_assignment'))

@app.route('/admin/assignment-templates')
@admin_required
def assignment_templates():
    """Manage assignment templates for common bulk operations"""
    try:
        # This could be expanded to save common assignment patterns
        # For now, we'll show some predefined templates
        
        templates = [
            {
                'name': 'VIP1 - Budget Hotels',
                'description': 'Assign budget hotels ($0-$100) to VIP1 users',
                'criteria': {
                    'min_price': 0,
                    'max_price': 100,
                    'vip_level': 'VIP1',
                    'custom_commission': 5.0
                }
            },
            {
                'name': 'VIP2 - Mid-Range Hotels',
                'description': 'Assign mid-range hotels ($100-$300) to VIP2 users',
                'criteria': {
                    'min_price': 100,
                    'max_price': 300,
                    'vip_level': 'VIP2',
                    'custom_commission': 10.0
                }
            },
            {
                'name': 'VIP3 - Luxury Hotels',
                'description': 'Assign luxury hotels ($300+) to VIP3 users',
                'criteria': {
                    'min_price': 300,
                    'max_price': None,
                    'vip_level': 'VIP3',
                    'category': 'luxury',
                    'custom_commission': 15.0
                }
            },
            {
                'name': 'First Session - All Hotels',
                'description': 'Assign all hotels to users in their first session',
                'criteria': {
                    'user_session_filter': 'first',
                    'custom_commission': 7.5
                }
            },
            {
                'name': 'High Rating Hotels',
                'description': 'Assign 4+ star hotels to all active users',
                'criteria': {
                    'rating': 4,
                    'custom_commission': 12.0
                }
            }
        ]
        
        return render_template('admin_assignment_templates.html', templates=templates)
        
    except Exception as e:
        flash(f'Error loading templates: {str(e)}', 'error')
        return redirect(url_for('bulk_hotel_assignment'))

@app.route('/admin/apply-template/<template_name>', methods=['POST'])
@admin_required
def apply_assignment_template(template_name):
    """Apply a predefined assignment template"""
    try:
        # Template definitions (in production, these could be stored in database)
        templates = {
            'VIP1 - Budget Hotels': {
                'min_price': 0,
                'max_price': 100,
                'vip_level': 'VIP1',
                'custom_commission': 5.0
            },
            'VIP2 - Mid-Range Hotels': {
                'min_price': 100,
                'max_price': 300,
                'vip_level': 'VIP2',
                'custom_commission': 10.0
            },
            'VIP3 - Luxury Hotels': {
                'min_price': 300,
                'vip_level': 'VIP3',
                'category': 'luxury',
                'custom_commission': 15.0
            },
            'First Session - All Hotels': {
                'user_session_filter': 'first',
                'custom_commission': 7.5
            },
            'High Rating Hotels': {
                'rating': 4,
                'custom_commission': 12.0
            }
        }
        
        if template_name not in templates:
            flash("Invalid template selected.", "error")
            return redirect(url_for('assignment_templates'))
        
        criteria = templates[template_name]
        session_type = request.form.get('session_type', 'first')
        replace_existing = request.form.get('replace_existing') == 'on'
        
        # Execute the template
        # ... (use the same logic as execute_bulk_assignment but with template criteria)
        
        flash(f"Template '{template_name}' applied successfully!", "success")
        return redirect(url_for('view_hotel_assignments'))
        
    except Exception as e:
        flash(f'Error applying template: {str(e)}', 'error')
        return redirect(url_for('assignment_templates'))
# ============= RESERVATION MANAGEMENT =============

@app.route('/admin/reservations')
@admin_required
def view_reservations():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    session_filter = request.args.get('session_type', '')
    
    reservations_query = Reservation.query
    
    if status_filter:
        reservations_query = reservations
    if status_filter:
        reservations_query = reservations_query.filter_by(status=status_filter)
    
    if session_filter:
        reservations_query = reservations_query.filter_by(session_type=session_filter)
    
    reservations = reservations_query.order_by(Reservation.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    status_options = ['pending', 'confirmed', 'cancelled', 'completed']
    session_types = ['first', 'second']
    
    return render_template('admin_reservations.html', 
                         reservations=reservations, 
                         status_options=status_options,
                         session_types=session_types,
                         current_status_filter=status_filter,
                         current_session_filter=session_filter)

@app.route('/admin/reservations/<int:reservation_id>/update_status', methods=['POST'])
@admin_required
def update_reservation_status(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        new_status = request.form.get('status')
        
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        if new_status not in valid_statuses:
            flash("Invalid status selected.", "error")
            return redirect(url_for('view_reservations'))
        
        old_status = reservation.status
        reservation.status = new_status
        reservation.admin_notes = request.form.get('admin_notes', '')
        
        # Handle completion
        if new_status == 'completed' and old_status != 'completed':
            reservation.completed_at = datetime.utcnow()
            # Process commission if applicable
            user = User.query.get(reservation.user_id)
            if user:
                user.process_reservation_commission(reservation)
        
        db.session.commit()
        flash(f"Reservation status updated from {old_status} to {new_status}.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating reservation status: {str(e)}", "error")
    
    return redirect(url_for('view_reservations'))

@app.route('/admin/reservations/<int:reservation_id>/delete', methods=['POST'])
@admin_required
def delete_reservation(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        
        # If reservation was paid, refund the amount
        if reservation.status in ['confirmed', 'pending']:
            user = User.query.get(reservation.user_id)
            if user:
                user.balance += reservation.total_amount
        
        db.session.delete(reservation)
        db.session.commit()
        flash('Reservation deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting reservation: {str(e)}', 'error')
    
    return redirect(url_for('view_reservations'))

# ============= INVITATION CODE MANAGEMENT =============

@app.route('/admin/invitation-codes')
@admin_required
def view_invitation_codes():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    codes_query = InvitationCode.query
    
    if status_filter == 'active':
        codes_query = codes_query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        codes_query = codes_query.filter_by(is_active=False)
    elif status_filter == 'used':
        codes_query = codes_query.filter(InvitationCode.used_count > 0)
    
    codes = codes_query.order_by(InvitationCode.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_invite.html', 
                         codes=codes, 
                         current_status_filter=status_filter)

@app.route('/admin/invitation-codes/create', methods=['GET', 'POST'])
@admin_required
def generate_invitation_code():
    if request.method == 'POST':
        try:
            code = request.form.get('code')
            #max_uses = int(request.form.get('max_uses', 1))
            
           
            
            # Generate random code if not provided
            if not code:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Check if code already exists
            existing_code = InvitationCode.query.filter_by(code=code).first()
            if existing_code:
                flash("Invitation code already exists.", "error")
                return redirect(url_for('generate_invitation_code'))
            
            admin = Admin.query.get(session.get('admin_id'))
            
            new_code = InvitationCode(
                code=code,
        
              
            
                
            )
            
            db.session.add(new_code)
            db.session.commit()
            flash(f'Invitation code "{code}" created successfully', 'success')
            return redirect(url_for('view_invitation_codes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invitation code: {str(e)}', 'error')
    
    return render_template('admin_invite.html')

@app.route('/admin/invitation-codes/<int:code_id>/toggle', methods=['POST'])
@admin_required
def toggle_invitation_code(code_id):
    code = InvitationCode.query.get_or_404(code_id)
    code.is_active = not code.is_active
    db.session.commit()
    
    action = 'activated' if code.is_active else 'deactivated'
    flash(f"Invitation code {code.code} has been {action}.", "success")
    return redirect(url_for('view_invitation_codes'))

@app.route('/admin/invitation-codes/<int:code_id>/delete', methods=['POST'])
@admin_required
def delete_invitation_code(code_id):
    try:
        code = InvitationCode.query.get_or_404(code_id)
        code_value = code.code
        
        db.session.delete(code)
        db.session.commit()
        flash(f'Invitation code "{code_value}" deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting invitation code: {str(e)}', 'error')
    
    return redirect(url_for('view_invitation_codes'))

# ============= COMMISSION MANAGEMENT =============

@app.route('/admin/commissions')
@admin_required
def view_commissions():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    user_filter = request.args.get('user_id', '')
    
    # This would require a Commission model - assuming it exists
    # If not, you might need to create it or handle commissions differently
    try:
        from hotel_app.models import Commission
        
        commissions_query = Commission.query
        
        if status_filter:
            commissions_query = commissions_query.filter_by(status=status_filter)
        
        if user_filter:
            commissions_query = commissions_query.filter_by(user_id=user_filter)
        
        commissions = commissions_query.order_by(Commission.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        users = User.query.filter_by(is_active=True).all()
        status_options = ['pending', 'paid', 'cancelled']
        
        return render_template('admin_commissions.html', 
                             commissions=commissions, 
                             users=users,
                             status_options=status_options,
                             current_status_filter=status_filter,
                             current_user_filter=user_filter)
        
    except ImportError:
        # If Commission model doesn't exist, show summary from users
        users = User.query.filter_by(is_active=True).all()
        commission_data = []
        
        for user in users:
            summary = user.get_commission_summary()
            if summary['total_earned'] > 0:
                commission_data.append({
                    'user': user,
                    'summary': summary
                })
        
        return render_template('admin_commission_summary.html', 
                             commission_data=commission_data)

@app.route('/admin/commissions/pay-all', methods=['POST'])
@admin_required
def pay_all_commissions():
    try:
        admin = Admin.query.get(session.get('admin_id'))
        total_paid = 0
        users_paid = 0
        
        users = User.query.filter_by(is_active=True).all()
        for user in users:
            summary = user.get_commission_summary()
            if summary['unpaid_amount'] > 0:
                if admin.pay_user_commission(user.id):
                    total_paid += summary['unpaid_amount']
                    users_paid += 1
        
        if users_paid > 0:
            flash(f"Paid commissions to {users_paid} users, total amount: ${total_paid:.2f}", "success")
        else:
            flash("No unpaid commissions found.", "info")
            
    except Exception as e:
        flash(f"Error paying commissions: {str(e)}", "error")
    
    return redirect(url_for('view_commissions'))

# ============= REPORTS AND ANALYTICS =============

@app.route('/admin/reports')
@admin_required
def view_reports():
    try:
        # Date range from request
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        
        # Default to last 30 days if no dates provided
        if not from_date or not to_date:
            from datetime import datetime, timedelta
            to_date = datetime.utcnow().date()
            from_date = to_date - timedelta(days=30)
        else:
            from datetime import datetime
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        # Financial summary
        approved_deposits = db.session.query(db.func.sum(DepositRequest.amount)).filter(
            DepositRequest.status == 'approved',
            DepositRequest.processed_at.between(from_date, to_date)
        ).scalar() or 0
        
        approved_withdrawals = db.session.query(db.func.sum(WithdrawalRequest.amount)).filter(
            WithdrawalRequest.status == 'approved',
            WithdrawalRequest.processed_at.between(from_date, to_date)
        ).scalar() or 0
        
        # Reservation summary
        total_reservations = Reservation.query.filter(
            Reservation.created_at.between(from_date, to_date)
        ).count()
        
        completed_reservations = Reservation.query.filter(
            Reservation.status == 'completed',
            Reservation.completed_at.between(from_date, to_date)
        ).count()
        
        reservation_revenue = db.session.query(db.func.sum(Reservation.total_amount)).filter(
            Reservation.status == 'completed',
            Reservation.completed_at.between(from_date, to_date)
        ).scalar() or 0
        
        # User statistics
        new_users = User.query.filter(
            User.created_at.between(from_date, to_date)
        ).count()
        
        active_users = User.query.filter_by(is_active=True).count()
        
        # Top performing hotels
        top_hotels = db.session.query(
            Hotel,
            db.func.count(Reservation.id).label('reservation_count'),
            db.func.sum(Reservation.total_amount).label('total_revenue')
        ).join(Reservation).filter(
            Reservation.created_at.between(from_date, to_date)
        ).group_by(Hotel.id).order_by(db.text('total_revenue DESC')).limit(10).all()
        
        # VIP level distribution
        vip_distribution = db.session.query(
            User.vip_level,
            db.func.count(User.id).label('user_count')
        ).group_by(User.vip_level).all()
        
        report_data = {
            'from_date': from_date,
            'to_date': to_date,
            'approved_deposits': approved_deposits,
            'approved_withdrawals': approved_withdrawals,
            'total_reservations': total_reservations,
            'completed_reservations': completed_reservations,
            'reservation_revenue': reservation_revenue,
            'new_users': new_users,
            'active_users': active_users,
            'top_hotels': top_hotels,
            'vip_distribution': vip_distribution,
            'net_flow': approved_deposits - approved_withdrawals,
            'completion_rate': (completed_reservations / total_reservations * 100) if total_reservations > 0 else 0
        }
        
        return render_template('admin_reports.html', report_data=report_data)
        
    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}")
        flash(f"Error generating reports: {str(e)}", "error")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/reports/export')
@admin_required
def export_reports():
    try:
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        report_type = request.args.get('type', 'summary')
        
        # This would generate CSV/Excel exports
        # Implementation depends on your specific requirements
        flash("Export functionality not yet implemented.", "info")
        return redirect(url_for('view_reports'))
        
    except Exception as e:
        flash(f"Error exporting reports: {str(e)}", "error")
        return redirect(url_for('view_reports'))

# ============= SETTINGS AND CONFIGURATION =============

@app.route('/admin/settings')
@admin_required
def admin_settings():
    try:
        # You might want to create a Settings model for this
        # For now, we'll show basic admin account settings
        admin = Admin.query.get(session.get('admin_id'))
        
        # System statistics
        total_users = User.query.count()
        total_hotels = Hotel.query.count()
        total_reservations = Reservation.query.count()
        total_deposits = DepositRequest.query.count()
        total_withdrawals = WithdrawalRequest.query.count()
        
        system_stats = {
            'total_users': total_users,
            'total_hotels': total_hotels,
            'total_reservations': total_reservations,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals
        }
        
        return render_template('admin_settings.html', 
                             admin=admin, 
                             system_stats=system_stats)
        
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        flash(f"Error loading settings: {str(e)}", "error")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings/change-password', methods=['POST'])
@admin_required
def change_admin_password():
    try:
        admin = Admin.query.get(session.get('admin_id'))
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not admin.check_password(current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for('admin_settings'))
        
        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for('admin_settings'))
        
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for('admin_settings'))
        
        admin.set_password(new_password)
        db.session.commit()
        flash("Password changed successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error changing password: {str(e)}", "error")
    
    return redirect(url_for('admin_settings'))

# ============= API ENDPOINTS FOR AJAX REQUESTS =============

@app.route('/admin/api/user-stats/<int:user_id>')
@admin_required
def get_user_stats(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        stats = {
            'balance': user.balance,
            'total_deposits': DepositRequest.query.filter_by(user_id=user_id, status='approved').count(),
            'total_withdrawals': WithdrawalRequest.query.filter_by(user_id=user_id, status='approved').count(),
            'total_reservations': Reservation.query.filter_by(user_id=user_id).count(),
            'commission_summary': user.get_commission_summary()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/hotel-stats/<int:hotel_id>')
@admin_required
def get_hotel_stats(hotel_id):
    try:
        hotel = Hotel.query.get_or_404(hotel_id)
        
        stats = {
            'total_reservations': Reservation.query.filter_by(hotel_id=hotel_id).count(),
            'completed_reservations': Reservation.query.filter_by(hotel_id=hotel_id, status='completed').count(),
            'total_revenue': db.session.query(db.func.sum(Reservation.total_amount)).filter_by(hotel_id=hotel_id, status='completed').scalar() or 0,
            'assigned_users': UserHotelAssignment.query.filter_by(hotel_id=hotel_id).count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/dashboard-data')
@admin_required
def get_dashboard_data():
    try:
        # Real-time dashboard data for AJAX updates
        data = {
            'pending_deposits': DepositRequest.query.filter_by(status='pending').count(),
            'pending_withdrawals': WithdrawalRequest.query.filter_by(status='pending').count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'today_reservations': Reservation.query.filter(
                Reservation.created_at >= datetime.utcnow().date()
            ).count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= BULK OPERATIONS =============

@app.route('/admin/bulk-actions', methods=['POST'])
@admin_required
def handle_bulk_actions():
    try:
        action = request.form.get('action')
        item_ids = request.form.getlist('item_ids')
        item_type = request.form.get('item_type')
        
        if not action or not item_ids or not item_type:
            flash("Missing required parameters for bulk action.", "error")
            return redirect(request.referrer or url_for('admin_dashboard'))
        
        item_ids = [int(id) for id in item_ids]
        
        if item_type == 'users':
            users = User.query.filter(User.id.in_(item_ids)).all()
            
            if action == 'activate':
                for user in users:
                    user.is_active = True
                flash(f"Activated {len(users)} users.", "success")
            elif action == 'deactivate':
                for user in users:
                    user.is_active = False
                flash(f"Deactivated {len(users)} users.", "success")
            elif action == 'delete':
                for user in users:
                    # Delete related records first
                    UserHotelAssignment.query.filter_by(user_id=user.id).delete()
                    Reservation.query.filter_by(user_id=user.id).delete()
                    DepositRequest.query.filter_by(user_id=user.id).delete()
                    WithdrawalRequest.query.filter_by(user_id=user.id).delete()
                    db.session.delete(user)
                flash(f"Deleted {len(users)} users and their related data.", "success")
        
        elif item_type == 'hotels':
            hotels = Hotel.query.filter(Hotel.id.in_(item_ids)).all()
            
            if action == 'activate':
                for hotel in hotels:
                    hotel.is_active = True
                flash(f"Activated {len(hotels)} hotels.", "success")
            elif action == 'deactivate':
                for hotel in hotels:
                    hotel.is_active = False
                flash(f"Deactivated {len(hotels)} hotels.", "success")
            elif action == 'delete':
                for hotel in hotels:
                    # Delete related records first
                    UserHotelAssignment.query.filter_by(hotel_id=hotel.id).delete()
                    Reservation.query.filter_by(hotel_id=hotel.id).delete()
                    db.session.delete(hotel)
                flash(f"Deleted {len(hotels)} hotels and their related data.", "success")
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error performing bulk action: {str(e)}", "error")
    
    return redirect(request.referrer or url_for('admin_dashboard'))

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/admin/'):
        return render_template('admin_404.html'), 404
    # Let the main app handle non-admin 404s
    return error

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/admin/'):
        return render_template('admin_500.html'), 500
    # Let the main app handle non-admin 500s
    return error

# ============= UTILITY FUNCTIONS =============

def generate_random_string(length=8):
    """Generate a random string for invitation codes"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def format_currency(amount):
    """Format currency for display"""
    return f"${amount:,.2f}"

# Register template filters
@app.template_filter('currency')
def currency_filter(amount):
    return format_currency(amount)

@app.template_filter('datetime')
def datetime_filter(dt):
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return 'N/A'

@app.template_filter('date')
def date_filter(dt):
    if dt:
        return dt.strftime('%Y-%m-%d')
    return 'N/A'

# ============= LOGGING CONFIGURATION =============

# Set up logging for admin operations
admin_logger = logging.getLogger('admin_operations')
admin_handler = logging.FileHandler('admin_operations.log')
admin_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
admin_logger.addHandler(admin_handler)
admin_logger.setLevel(logging.INFO)

# Log admin actions
def log_admin_action(action, details, admin_id=None):
    if not admin_id:
        admin_id = session.get('admin_id')
    
    admin_logger.info(f"Admin {admin_id} - {action}: {details}")

# Example usage in routes:
# log_admin_action("User Balance Adjustment", f"User {user_id} balance adjusted by ${amount}")
# log_admin_action("Hotel Created", f"Hotel '{hotel_name}' created")

if __name__ == '__main__':
    # This won't run when imported as a module
    app.run(debug=True)