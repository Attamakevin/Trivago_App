# hotel_app/routes.py
from flask import render_template, redirect, url_for, flash, request,jsonify, session
from hotel_app import app, db
from hotel_app.models import User, Hotel,LuxuryOrder, UserHotelAssignment,Reservation, DepositRequest, WithdrawalRequest, EventAd, Admin, InvitationCode
from datetime import datetime, date,timedelta
from flask_login import login_required, login_user, logout_user, current_user
@app.route('/')
def home():
    return render_template('home.html')
from flask import render_template, request,  url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from hotel_app import db
from flask import g
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

def get_user_ip():
    """Get the real IP address of the user"""
    # Check for forwarded IP first (in case of proxy/load balancer)
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip

import ipaddress

def is_private_ip(ip):
    """Check if an IP address is private"""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

def get_location_from_ip(ip_address):
    """Get location information from IP address"""
    # Check if it's a private IP
    if is_private_ip(ip_address):
        print(f"Cannot geolocate private IP: {ip_address}")
        return {
            'country': 'Private Network',
            'country_code': 'N/A',
            'region': 'Local Network',
            'city': 'Local Network',
            'latitude': None,
            'longitude': None,
            'timezone': 'Unknown',
            'isp': 'Private Network'
        }
    try:
        import requests
    except ImportError:
        print("requests library not installed. Install with: pip install requests")
        return {
            'country': 'Unknown',
            'country_code': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'latitude': None,
            'longitude': None,
            'timezone': 'Unknown',
            'isp': 'Unknown'
        }
    
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {  # Don't forget this return!
                'country': data.get('country_name', 'Unknown'),
                'country_code': data.get('country_code', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone', 'Unknown'),
                'isp': data.get('org', 'Unknown')
            }
    except Exception as e:
        print(f"Error getting location: {e}")
    
    return {
        'country': 'Unknown',
        'country_code': 'Unknown',
        'region': 'Unknown',
        'city': 'Unknown',
        'latitude': None,
        'longitude': None,
        'timezone': 'Unknown',
        'isp': 'Unknown'
    }
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
        # Silently collect user's IP address and location data
        user_ip = get_user_ip()
        location_data = get_location_from_ip(user_ip)
        
        # Mark invitation code as used
        code_entry.is_used = True
        
        # Create new user with inactive status, IP, and location data (collected silently)
        new_user = User(
            contact=phone,
            password_hash=generate_password_hash(password),
            is_active=False,
            invitation_code=invitation_code,
            # Silently collected IP and location fields
            ip_address=user_ip,
            country=location_data['country'],
            country_code=location_data['country_code'],
            region=location_data['region'],
            city=location_data['city'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            timezone=location_data['timezone'],
            isp=location_data['isp'],
            last_location_update=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()

        # Clear captcha from session after successful registration
        session.pop('captcha_code', None)
        new_user.trial_bonus = 564.00
        flash('Registration successful! ', 'success')
        return redirect(url_for('auth'))  # Redirect to login form
    
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('register'))

# Additional route to update user location (optional - for existing users)
@app.route('/update_location', methods=['POST'])
def update_user_location():
    """Update current user's location information"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    try:
        user = User.query.get(session['user_id'])
        if user:
            user_ip = get_user_ip()
            location_data = get_location_from_ip(user_ip)
            
            # Update user's location info
            user.ip_address = user_ip
            user.country = location_data['country']
            user.country_code = location_data['country_code']
            user.region = location_data['region']
            user.city = location_data['city']
            user.latitude = location_data['latitude']
            user.longitude = location_data['longitude']
            user.timezone = location_data['timezone']
            user.isp = location_data['isp']
            user.last_location_update = datetime.utcnow()
            
            db.session.commit()
            flash('Location updated successfully', 'success')
        else:
            flash('User not found', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update location', 'error')
    
    return redirect(url_for('dashboard'))
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

# Updated reservation route with automatic completion and rating
@app.route('/reserve/<int:hotel_id>', methods=['GET', 'POST'])
def reserve(hotel_id):
    if 'user_id' not in session:
        if request.method == 'GET':
            return redirect(url_for('login'))
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        hotel = Hotel.query.get_or_404(hotel_id)

        # Check if user has access to this hotel
        hotel_assignment = UserHotelAssignment.query.filter_by(
            user_id=user.id, 
            hotel_id=hotel_id
        ).first()
        
        if not hotel_assignment:
            if request.method == 'GET':
                flash('You do not have access to this hotel', 'error')
                return redirect(url_for('reservations'))
            return jsonify({'error': 'You do not have access to this hotel'}), 403

        # Check if user has already reserved and rated this hotel
        existing_reservation = Reservation.query.filter_by(
            user_id=user.id,
            hotel_id=hotel_id,
            status='Completed'
        ).filter(Reservation.rating.isnot(None)).first()
        
        if existing_reservation:
            if request.method == 'GET':
                flash('You have already completed this hotel reservation', 'error')
                return redirect(url_for('reservations'))
            return jsonify({'error': 'You have already completed this hotel reservation'}), 400

        # Check daily reservation limit
        today_reservations = Reservation.query.filter_by(user_id=user.id).filter(
            Reservation.timestamp >= datetime.combine(date.today(), datetime.min.time())).count()
        
        limits = {'VIP0': 70, 'VIP1': 80, 'VIP2': 80}
        daily_limit = limits.get(user.vip_level, 70)

        if today_reservations >= daily_limit:
            if request.method == 'GET':
                flash(f'Daily reservation limit reached ({daily_limit} reservations per day for {user.vip_level})', 'error')
                return redirect(url_for('reservations'))
            return jsonify({
                'error': f'Daily reservation limit reached ({daily_limit} reservations per day for {user.vip_level})'
            }), 403

        # Calculate commission
        commission = hotel_assignment.custom_commission * hotel.commission_multiplier
        
        # Generate unique order number
        order_number = f"ORD{user.id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create reservation with immediate completion, commission payment, and automatic rating
        reservation = Reservation(
            user_id=user.id,
            hotel_id=hotel.id,
            order_number=order_number,
            commission_earned=commission,
            status='Completed',  # Set to completed immediately
            timestamp=datetime.utcnow(),
            commission_paid=True,  # Mark commission as paid immediately
            commission_paid_at=datetime.utcnow(),  # Set payment timestamp
            rating=5  # Auto-rate as 5 stars to mark as completed
        )
        
        # Add commission to user balance immediately
        print(f"DEBUG: Adding commission {commission} to user {user.id}")
        print(f"DEBUG: User balance before: {user.balance}")
        
        user.balance += commission
        
        print(f"DEBUG: User balance after: {user.balance}")
        user.balance -= user.trial_bonus  # Deduct trial bonus if applicable
        user.trial_bonus = 0.0 # reset trial bonus after processing commissions
        
        # Add both user and reservation to session
        db.session.add(reservation)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Refresh to get updated data
        
        print(f"DEBUG: User balance after commit: {user.balance}")
        print(f"DEBUG: Reservation created for hotel {hotel_id} with rating {reservation.rating}")
        
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
    
    # Get all hotels assigned to this user WITH commission information
    assigned_hotels_query = db.session.query(
        Hotel, 
        UserHotelAssignment.custom_commission,
        UserHotelAssignment.created_at
    ).join(
        UserHotelAssignment, 
        Hotel.id == UserHotelAssignment.hotel_id
    ).filter(
        UserHotelAssignment.user_id == user.id
    ).order_by(Hotel.id)  # Order by ID for consistent ordering
    
    all_assigned_hotels_data = assigned_hotels_query.all()
    all_assigned_hotels = [hotel for hotel, commission, assigned_at in all_assigned_hotels_data]
    
    # Create a mapping of hotel_id to commission for easy lookup
    hotel_commission_map = {
        hotel.id: commission for hotel, commission, assigned_at in all_assigned_hotels_data
    }
    
    # Create a mapping of hotel_id to assignment date for easy lookup
    hotel_assignment_date_map = {
        hotel.id: assigned_at for hotel, commission, assigned_at in all_assigned_hotels_data
    }
    
    # Get hotels that have been reserved AND rated by this user
    completed_reservations = db.session.query(Reservation).filter(
        Reservation.user_id == user.id,
        Reservation.status == 'Completed',
        Reservation.rating.isnot(None)  # Has been rated
    ).all()
    
    # Extract unique hotel IDs from completed reservations
    completed_hotel_ids = list(set([reservation.hotel_id for reservation in completed_reservations]))
    
    # Filter out hotels that have been completed (reserved and rated)
    available_hotels = [hotel for hotel in all_assigned_hotels if hotel.id not in completed_hotel_ids]
    
    # Get the next hotel to display (first available hotel)
    current_hotel = available_hotels[0] if available_hotels else None
    
    # Get current hotel's commission if available
    current_hotel_commission = hotel_commission_map.get(current_hotel.id) if current_hotel else None
    current_hotel_assignment_date = hotel_assignment_date_map.get(current_hotel.id) if current_hotel else None
    
    # Debug information
    print(f"DEBUG: User {user.id} has {len(all_assigned_hotels)} total assigned hotels")
    print(f"DEBUG: Completed reservations: {len(completed_reservations)}")
    print(f"DEBUG: Completed hotel IDs: {completed_hotel_ids}")
    print(f"DEBUG: Available hotels: {len(available_hotels)}")
    
    # Debug: Show commission information
    print(f"DEBUG: Hotel commission mapping:")
    for hotel_id, commission in hotel_commission_map.items():
        hotel_name = next((h.name for h in all_assigned_hotels if h.id == hotel_id), "Unknown")
        print(f"  - Hotel ID {hotel_id} ({hotel_name}): ${commission}")
    
    if current_hotel:
        print(f"DEBUG: Current hotel to display: {current_hotel.name} (ID: {current_hotel.id})")
        print(f"DEBUG: Current hotel commission: ${current_hotel_commission}")
        print(f"DEBUG: Current hotel assigned at: {current_hotel_assignment_date}")
    else:
        print("DEBUG: No more hotels available for this user - all completed!")
    
    # Debug: Show all reservations for this user
    all_user_reservations = Reservation.query.filter_by(user_id=user.id).all()
    print(f"DEBUG: All user reservations ({len(all_user_reservations)}):")
    for res in all_user_reservations:
        print(f"  - Hotel ID: {res.hotel_id}, Status: {res.status}, Rating: {res.rating}")
    
    # Debug: Show available hotels with their commissions
    print(f"DEBUG: Available hotels:")
    for hotel in available_hotels:
        commission = hotel_commission_map.get(hotel.id, 'Unknown')
        print(f"  - {hotel.name} (ID: {hotel.id}) - Commission: ${commission}")
    
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
        user.balance -= user.trial_bonus  # Deduct trial bonus if applicable
        user.trial_bonus = 0.0 # reset trial bonus after processing commissions
        
        print(f"DEBUG: User balance after: {user.balance}")
        print(f"{user.trial_bonus} trial bonus deducted from user {user.id}")

    # Commit any legacy commission updates
    if unpaid_reservations:
        user.balance -= user.trial_bonus  # Deduct trial bonus if applicable
        user.trial_bonus = 0.0 # reset trial bonus after processing commissions
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        print(f"DEBUG: User balance after commit: {user.balance}")
    
    # Get user's reservations with hotel details
    user_reservations = db.session.query(Reservation, Hotel).join(
        Hotel, Reservation.hotel_id == Hotel.id
    ).filter(Reservation.user_id == user.id).order_by(Reservation.timestamp.desc()).all()
    
    # Format reservations for template with assignment commission information
    formatted_reservations = []
    for reservation, hotel in user_reservations:
        assignment_commission = hotel_commission_map.get(hotel.id, 0)  # Get commission from assignment
        formatted_reservations.append({
            'id': reservation.id,
            'hotel_name': hotel.name,
            'location': f"{hotel.name} Location",
            'price': hotel.price,
            'commission': reservation.commission_earned,  # Commission from reservation
            'assignment_commission': assignment_commission,  # Commission from assignment
            'status': reservation.status.lower(),
            'created_at': reservation.timestamp,
            'rated': reservation.rating is not None,
            'commission_paid': reservation.commission_paid,
            'rating': reservation.rating,
            'assigned_at': hotel_assignment_date_map.get(hotel.id)
        })
    
    # Calculate user stats for display
    total_commission = sum([r.commission_earned for r in Reservation.query.filter_by(user_id=user.id, commission_paid=True).all()])
    trial_bonus = user.trial_bonus if hasattr(user, 'trial_bonus') else 0.0
    deposit_balance = user.deposit_balance if hasattr(user, 'deposit_balance') else 0.0
    active_bookings = len([r for r in formatted_reservations if r['status'] in ['processing', 'confirmed']])
    
    # Calculate total potential commission from all assignments
    total_potential_commission = sum(hotel_commission_map.values())
    
    user_stats = {
        'total_commission': total_commission,
        'trial_bonus': trial_bonus,
        'deposit_balance': deposit_balance,
        'active_bookings': active_bookings,
        'completed_hotels': len(completed_hotel_ids),
        'total_assigned_hotels': len(all_assigned_hotels),
        'remaining_hotels': len(available_hotels),
        'total_potential_commission': total_potential_commission,  # New stat
        'current_hotel_commission': current_hotel_commission  # New stat
    }
    
    print(f"Final user balance being sent to template: {user.balance}")
    print(f"Total potential commission from assignments: ${total_potential_commission}")
    
    # Pass the current hotel with its commission information
    current_hotel_data = None
    if current_hotel:
        current_hotel_data = {
            'hotel': current_hotel,
            'commission': current_hotel_commission,
            'assigned_at': current_hotel_assignment_date
        }
    
    # Pass only the current hotel (or None if all are completed) and additional stats
    return render_template('reservations.html', 
                         hotels=[current_hotel] if current_hotel else [], 
                         current_hotel=current_hotel,
                         current_hotel_data=current_hotel_data,  # New data with commission
                         hotel_commission_map=hotel_commission_map,  # All hotel commissions
                         user=user, 
                         reservations=formatted_reservations, 
                         user_stats=user_stats)
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
            
            print(f"DEBUG: Form data - amount: {amount_str}, network: {network}, wallet: {wallet_address}")
            
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
            
            print(f"DEBUG: All validations passed. User balance: {user.balance}, Withdrawal amount: {amount}")
            
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest(
                user_id=user.id, 
                amount=amount, 
                network=network,
                wallet_address=wallet_address,
                status='Pending'
            )
            
            print(f"DEBUG: Withdrawal request created: {withdrawal_request}")
            print(f"DEBUG: User ID: {user.id}, Amount: {amount}, Network: {network}")
            
            # Temporarily reduce balance (will be restored if withdrawal is rejected)
            original_balance = user.balance
            user.balance -= amount
            
            print(f"DEBUG: Balance reduced from {original_balance} to {user.balance}")
            
            db.session.add(withdrawal_request)
            print("DEBUG: Withdrawal request added to session")
            
            # Commit the transaction
            db.session.commit()
            print("DEBUG: Transaction committed successfully")
            
            # Verify the withdrawal was saved
            saved_withdrawal = WithdrawalRequest.query.filter_by(user_id=user.id).order_by(WithdrawalRequest.id.desc()).first()
            if saved_withdrawal:
                print(f"DEBUG: Withdrawal saved with ID: {saved_withdrawal.id}")
            else:
                print("DEBUG: WARNING - Withdrawal not found after commit!")
            
            flash('Withdrawal request submitted successfully. Please wait for approval.', 'success')
            return redirect(url_for('profile'))
            
        except KeyError as e:
            print(f"DEBUG: KeyError - {str(e)}")
            flash(f'Missing required field: {str(e)}', 'error')
            return render_template('withdraw.html', user=user)
        except ValueError as e:
            print(f"DEBUG: ValueError - {str(e)}")
            flash(f'Invalid data format: {str(e)}', 'error')
            return render_template('withdraw.html', user=user)
        except Exception as e:
            print(f"DEBUG: General Exception - {str(e)}")
            print(f"DEBUG: Exception type - {type(e)}")
            import traceback
            traceback.print_exc()
            
            db.session.rollback()
            print("DEBUG: Transaction rolled back")
            
            # Restore balance if it was already deducted
            try:
                if 'amount' in locals() and amount > 0:
                    user.balance += amount
                    db.session.commit()
                    print(f"DEBUG: Balance restored to {user.balance}")
            except Exception as restore_error:
                print(f"DEBUG: Balance restoration failed: {str(restore_error)}")
            
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
        'deposit_balance': user.deposit_balance, # Static value as per your template
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
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

@app.route('/bind_wallet', methods=['GET', 'POST'])
def bind_wallet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # Check if user already has a bound wallet
    if hasattr(user, 'bound_wallet_address') and user.bound_wallet_address:
        if request.method == 'POST':
            return jsonify({
                'success': False, 
                'message': 'Wallet already bound. You cannot change your wallet address once it has been set.'
            }), 400
        
        # GET request - show current wallet info
        return render_template('bind_wallet.html', user=user, wallet_already_bound=True)
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        wallet_type = data.get('wallet_type', '').strip().upper()
        wallet_address = data.get('wallet_address', '').strip()
        
        # Get Revolut-specific fields
        revolut_name = data.get('revolut_name', '').strip() if wallet_type == 'REVOLUT' else None
        revolut_iban = data.get('revolut_iban', '').strip() if wallet_type == 'REVOLUT' else None
        revolut_revtag = data.get('revolut_revtag', '').strip() if wallet_type == 'REVOLUT' else None
        
        # Validation
        if not wallet_type:
            return jsonify({'success': False, 'message': 'Wallet type is required'}), 400
        
        if not wallet_address:
            return jsonify({'success': False, 'message': 'Wallet address is required'}), 400
        
        # Validate wallet type
        valid_wallet_types = ['USDT', 'ETH', 'PAYPAL', 'REVOLUT']
        if wallet_type not in valid_wallet_types:
            return jsonify({'success': False, 'message': 'Invalid wallet type'}), 400
        
        # Validate wallet address format based on type
        validation_result = validate_wallet_format(wallet_address, wallet_type)
        if not validation_result['valid']:
            return jsonify({'success': False, 'message': validation_result['message']}), 400
        
        # Additional validation for Revolut-specific fields
        if wallet_type == 'REVOLUT':
            if not revolut_name or len(revolut_name.strip()) < 2:
                return jsonify({'success': False, 'message': 'Revolut account holder name is required (minimum 2 characters)'}), 400
            
            if not revolut_iban:
                return jsonify({'success': False, 'message': 'Revolut IBAN number is required'}), 400
            
            # Basic IBAN validation
            import re
            iban_pattern = r'^[A-Z]{2}\d{2}[A-Z0-9]{4,30}$'
            if not re.match(iban_pattern, revolut_iban.upper().replace(' ', '')):
                return jsonify({'success': False, 'message': 'Invalid IBAN format. IBAN should start with 2 letters, followed by 2 digits, then alphanumeric characters'}), 400
            
            if not revolut_revtag:
                return jsonify({'success': False, 'message': 'Revolut RevTag is required'}), 400
            
            # RevTag validation
            if not revolut_revtag.startswith('@') or len(revolut_revtag) < 4 or len(revolut_revtag) > 20:
                return jsonify({'success': False, 'message': 'Invalid RevTag format. RevTag should start with @ and be 4-20 characters long'}), 400
            
            revtag_content = revolut_revtag[1:]  # Remove @ symbol
            if not re.match(r'^[a-zA-Z0-9_]+$', revtag_content):
                return jsonify({'success': False, 'message': 'RevTag can only contain letters, numbers, and underscores after @'}), 400
        
        try:
            # Bind wallet to user
            user.bound_wallet_type = wallet_type
            user.bound_wallet_address = wallet_address
            user.wallet_bound_at = datetime.utcnow()
            
            # Handle Revolut-specific fields
            if wallet_type == 'REVOLUT':
                user.revolut_name = revolut_name
                user.revolut_iban = revolut_iban
                user.revolut_revtag = revolut_revtag
            
            db.session.commit()
            
            flash('Wallet bound successfully!', 'success')
            return jsonify({
                'success': True, 
                'message': 'Wallet bound successfully! You can now use this wallet for transactions.',
                'wallet_type': wallet_type,
                'wallet_address': wallet_address
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'An error occurred while binding wallet'}), 500
    
    # GET request - render bind wallet form
    return render_template('bind_wallet.html', user=user, wallet_already_bound=False)

def validate_wallet_format(address, wallet_type):
    """
    Validate wallet address format based on wallet type
    """
    import re
    
    if not address or not wallet_type:
        return {'valid': False, 'message': 'Address and wallet type are required'}
    
    wallet_type = wallet_type.upper()
    
    # USDT wallet validation (using existing validation from DepositRequest)
    if wallet_type == 'USDT':
        # For USDT, we need to know the network, so we'll accept common formats
        # ETH/ERC-20 format
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return {'valid': True, 'message': 'Valid USDT (ERC-20) address'}
        # TRON/TRC-20 format
        elif re.match(r'^T[A-Za-z1-9]{33}$', address):
            return {'valid': True, 'message': 'Valid USDT (TRC-20) address'}
        # Bitcoin/Omni format
        elif re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return {'valid': True, 'message': 'Valid USDT (Omni) address'}
        else:
            return {'valid': False, 'message': 'Invalid USDT wallet address format'}
    
    # ETH wallet validation
    elif wallet_type == 'ETH':
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return {'valid': True, 'message': 'Valid Ethereum address'}
        else:
            return {'valid': False, 'message': 'Invalid Ethereum address format'}
    
    # PayPal validation (email format)
    elif wallet_type == 'PAYPAL':
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, address):
            return {'valid': True, 'message': 'Valid PayPal email address'}
        else:
            return {'valid': False, 'message': 'Invalid PayPal email format'}
    
    # Revolut validation (phone number or email)
    elif wallet_type == 'REVOLUT':
        # Check if it's an email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # Check if it's a phone number (basic validation)
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        
        if re.match(email_pattern, address):
            return {'valid': True, 'message': 'Valid Revolut email address'}
        elif re.match(phone_pattern, address):
            return {'valid': True, 'message': 'Valid Revolut phone number'}
        else:
            return {'valid': False, 'message': 'Invalid Revolut account (use email or phone number)'}
    
    else:
        return {'valid': False, 'message': 'Unsupported wallet type'}

@app.route('/get_wallet_info')
def get_wallet_info():
    """Get current user's bound wallet information"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # DEBUG: Print user attributes to see what fields exist
    print("=== DEBUG: User attributes ===")
    for attr in dir(user):
        if not attr.startswith('_') and not callable(getattr(user, attr)):
            value = getattr(user, attr, 'N/A')
            print(f"{attr}: {value}")
    print("=== END DEBUG ===")
    
    # Initialize wallets dictionary
    wallets = {}
    
    # Check if user has bound wallet
    if hasattr(user, 'bound_wallet_address') and user.bound_wallet_address:
        wallet_type_lower = user.bound_wallet_type.lower() if user.bound_wallet_type else 'unknown'
        
        # Basic wallet data
        wallet_data = {
            'address': user.bound_wallet_address,
            'type': user.bound_wallet_type,
            'bound_at': user.wallet_bound_at.isoformat() if user.wallet_bound_at else None
        }
        
        # Add Revolut-specific fields if it's a Revolut wallet
        if wallet_type_lower == 'revolut':
            print("=== DEBUG: Processing Revolut wallet ===")
            
            # Check if Revolut fields exist in database
            revolut_name = getattr(user, 'revolut_name', None)
            revolut_iban = getattr(user, 'revolut_iban', None) 
            revolut_revtag = getattr(user, 'revolut_revtag', None)
            
            print(f"revolut_name from DB: '{revolut_name}'")
            print(f"revolut_iban from DB: '{revolut_iban}'")
            print(f"revolut_revtag from DB: '{revolut_revtag}'")
            
            wallet_data.update({
                'name': revolut_name or '',
                'iban': revolut_iban or '', 
                'revtag': revolut_revtag or ''
            })
            
            print(f"Final wallet_data: {wallet_data}")
            print("=== END Revolut DEBUG ===")
        
        # Add to wallets dictionary with lowercase key
        wallets[wallet_type_lower] = wallet_data
        
        response_data = {
            'success': True,
            'wallet_bound': True,
            'wallets': wallets,
            # Keep backward compatibility
            'wallet_type': user.bound_wallet_type,
            'wallet_address': user.bound_wallet_address,
            'wallet_bound_at': user.wallet_bound_at.strftime('%Y-%m-%d %H:%M:%S') if user.wallet_bound_at else None
        }
        
        print(f"=== FINAL RESPONSE: {response_data} ===")
        return jsonify(response_data)
    else:
        return jsonify({
            'success': True,
            'wallet_bound': False,
            'wallets': {},
            'message': 'No wallet bound yet'
        })


@app.route('/transaction_details')
def transaction_details():
    if 'user_id' not in session:
        return jsonify({'redirect': url_for('login')}), 401
    
    user = User.query.get(session['user_id'])
    
    # Get all deposits for the user
    deposits = DepositRequest.query.filter_by(user_id=session['user_id']).all()
    
    # Get all withdrawals for the user
    withdrawals = WithdrawalRequest.query.filter_by(user_id=session['user_id']).all()
    
    # Combine deposits and withdrawals into a single list
    transaction_list = []
    
    # Add deposits to transaction list
    for deposit in deposits:
        transaction_list.append({
            'id': deposit.id,
            'type': 'deposit',
            'amount': float(deposit.amount),
            'network': deposit.network,
            'wallet_address': deposit.wallet_address,
            'transaction_hash': deposit.transaction_hash,
            'status': deposit.status,
            'date': deposit.created_at.strftime('%Y-%m-%d'),
            'time': deposit.created_at.strftime('%H:%M:%S'),
            'datetime': deposit.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'admin_notes': deposit.admin_notes,
            'processed_at': deposit.processed_at.strftime('%Y-%m-%d %H:%M:%S') if deposit.processed_at else None
        })
    
    # Add withdrawals to transaction list
    for withdrawal in withdrawals:
        transaction_list.append({
            'id': withdrawal.id,
            'type': 'withdrawal',
            'amount': float(withdrawal.amount),
            'network': withdrawal.network,
            'wallet_address': withdrawal.wallet_address,
            'transaction_hash': withdrawal.transaction_hash,
            'transaction_fee': float(withdrawal.transaction_fee),
            'status': withdrawal.status,
            'date': withdrawal.created_at.strftime('%Y-%m-%d'),
            'time': withdrawal.created_at.strftime('%H:%M:%S'),
            'datetime': withdrawal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'admin_notes': withdrawal.admin_notes,
            'rejection_reason': withdrawal.rejection_reason,
            'processed_at': withdrawal.processed_at.strftime('%Y-%m-%d %H:%M:%S') if withdrawal.processed_at else None
        })
    
    # Sort all transactions by date (newest first)
    transaction_list.sort(key=lambda x: x['datetime'], reverse=True)
    
    # Check if this is an AJAX request for JSON data
    if request.args.get('format') == 'json':
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'nickname': user.nickname,
                'user_id': user.user_id,
                'balance': float(user.balance),
                'member_points': user.member_points,
                'vip_level': user.vip_level
            },
            'transactions': transaction_list,
            'total_transactions': len(transaction_list)
        })
    
    # Otherwise, render the HTML template
    return render_template('transaction_details.html', user=user)

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    """Customer password reset route"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Get user identifier (could be user_id, contact, or nickname)
        user_identifier = data.get('user_identifier', '').strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validation
        if not user_identifier:
            return jsonify({'success': False, 'message': 'User identifier is required'}), 400
        
        if not new_password:
            return jsonify({'success': False, 'message': 'New password is required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        # Find user by user_id, contact, or nickname
        user = User.query.filter(
            (User.user_id == user_identifier) | 
            (User.contact == user_identifier) | 
            (User.nickname == user_identifier)
        ).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        try:
            # Update user's password
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
            # Clear any existing sessions for this user (optional security measure)
            # Note: This would require session management implementation
            
            return jsonify({
                'success': True, 
                'message': 'Password reset successfully. You can now login with your new password.',
                'redirect': url_for('login')
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'An error occurred while resetting password'}), 500
    
    # GET request - render password reset form
    return render_template('password_reset.html')

@app.route('/change_withdrawal_password', methods=['POST'])
def change_withdrawal_password():
    """Change user's withdrawal password"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first', 'redirect': url_for('login')}), 401
    
    data = request.get_json() if request.is_json else request.form
    
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validation
    if not new_password:
        return jsonify({'success': False, 'message': 'New withdrawal password is required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Withdrawal password must be at least 6 characters long'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

# Admin Setup Functions
from functools import wraps
from flask import session, flash, redirect, url_for, request, render_template
import string
import random
from hotel_app.models import Admin
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
        
        # Make admin available to the route
        g.current_admin = admin
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
@app.route('/admin/api/users/<int:user_id>/member_point', methods=['PUT'])
@admin_required
def api_update_user_member_point(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    new_member_point = data.get('member_point')
    
    
    old_member_point = user.member_points
    user.member_points = new_member_point
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'member point updated from {old_member_point} to {new_member_point}',
        'old_member_point': old_member_point,
        'new_member_point': new_member_point
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
                    user.deposit_balance += deposit.amount
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

@app.route('/admin/withdrawals')
@admin_required
def view_withdrawals():
    """View all withdrawal requests - Admin only"""
    try:
        logger.debug("Accessing view_withdrawals route")
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        
        # Debug: Check total withdrawals
        total_withdrawals = WithdrawalRequest.query.count()
        logger.debug(f"Total withdrawals in database: {total_withdrawals}")
        
        # Build query with join to User table for better performance
        withdrawals_query = WithdrawalRequest.query.options(db.joinedload(WithdrawalRequest.user))
        
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
        logger.debug(f"Total pages: {withdrawals.pages}, Total items: {withdrawals.total}")
        
        # Debug: Log first few withdrawals
        for i, withdrawal in enumerate(withdrawals.items[:3]):
            logger.debug(f"Withdrawal {i}: ID={withdrawal.id}, Status={withdrawal.status}, Amount=${withdrawal.amount}, User={withdrawal.user.nickname if withdrawal.user else 'No user'}")
        
        return render_template('admin_withdrawals.html', 
                             withdrawals=withdrawals, 
                             current_status=status_filter)
        
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


@app.route('/admin/hotels', methods=['GET', 'POST'])
def manage_hotels():
    if request.method == 'POST':
        # Handle hotel creation
        hotel = Hotel(
            name=request.form['name'],
            location=request.form['location'],
            primary_picture=request.form['primary_picture'],
            price=float(request.form['price']),
            commission_multiplier=float(request.form['commission_multiplier']),
            days_available=int(request.form['days_available']),
            rating=int(request.form['rating']),
            category=request.form['category'],
            description=request.form['description'],
            is_active=bool(request.form.get('is_active'))
        )
        db.session.add(hotel)
        db.session.commit()
        flash('Hotel added successfully!', 'success')
        return redirect(url_for('manage_hotels'))
    
    hotels = Hotel.query.order_by(Hotel.name).all()
    for hotel in hotels:
        if hotel.category is None:
            hotel.category = 'Uncategorized'
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
    # Updated routes with price filtering functionality

@app.route('/admin/assign-hotels', methods=['GET', 'POST'])
@admin_required
def assign_hotels_to_user():
    """Assign hotels to a specific user with price and category filtering"""
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        session_type = request.form['session_type']
        hotel_ids = request.form.getlist('hotel_ids')
        
        user = User.query.get_or_404(user_id)
        assignments_created = 0
        
        for hotel_id in hotel_ids:
            commission = float(request.form.get(f'commission_{hotel_id}', 0.0))
            
            # Check if assignment already exists
            existing = UserHotelAssignment.query.filter_by(
                user_id=user_id,
                hotel_id=hotel_id,
                session_type=session_type
            ).first()
            
            if existing:
                # Update existing assignment
                existing.custom_commission = commission
                flash(f'Updated commission for hotel {hotel_id}', 'info')
            else:
                # Create new assignment
                new_assignment = UserHotelAssignment(
                    user_id=user_id,
                    hotel_id=hotel_id,
                    session_type=session_type,
                    custom_commission=commission,
                    assigned_by=g.current_admin.id
                )
                db.session.add(new_assignment)
                assignments_created += 1
        
        db.session.commit()
        flash(f'Created {assignments_created} new hotel assignments for user {user.nickname}', 'success')
        return redirect(url_for('manage_hotels'))
    
    # GET request - show form with filtering
    user_id = request.args.get('user_id')
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    users = User.query.filter_by(is_active=True).all()
    
    # Build hotel query with filters
    query = Hotel.query.filter_by(is_active=True)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if min_price is not None:
        query = query.filter(Hotel.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Hotel.price <= max_price)
    
    hotels = query.order_by(Hotel.category, Hotel.price, Hotel.name).all()
    
    selected_user = None
    if user_id:
        selected_user = User.query.get(user_id)
    
    # Get price range for the form
    price_stats = db.session.query(
        db.func.min(Hotel.price).label('min_price'),
        db.func.max(Hotel.price).label('max_price')
    ).filter_by(is_active=True).first()
    
    return render_template('admin_assign_hotels.html', 
                         users=users, 
                         hotels=hotels, 
                         selected_user=selected_user,
                         category_filter=category_filter,
                         min_price=min_price,
                         max_price=max_price,
                         price_stats=price_stats)

@app.route('/admin/bulk-assign-hotels', methods=['GET', 'POST'])
@admin_required
def bulk_assign_hotels():
    """Bulk assign hotels to multiple users with enhanced filtering"""
    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids')
        session_type = request.form['session_type']
        assignment_type = request.form['assignment_type']  # 'category', 'price_range', or 'specific'
        
        assignments_created = 0
        
        if assignment_type == 'category':
            # Assign by category
            category = request.form['category']
            base_commission = float(request.form['base_commission'])
            
            hotels = Hotel.query.filter_by(category=category, is_active=True).all()
            
            for user_id in user_ids:
                for hotel in hotels:
                    # Check if assignment already exists
                    existing = UserHotelAssignment.query.filter_by(
                        user_id=user_id,
                        hotel_id=hotel.id,
                        session_type=session_type
                    ).first()
                    
                    if not existing:
                        new_assignment = UserHotelAssignment(
                            user_id=user_id,
                            hotel_id=hotel.id,
                            session_type=session_type,
                            custom_commission=base_commission,
                            assigned_by=current_user.id
                        )
                        db.session.add(new_assignment)
                        assignments_created += 1
        
        elif assignment_type == 'price_range':
            # NEW: Assign by price range
            min_price = float(request.form['min_price'])
            max_price = float(request.form['max_price'])
            category = request.form.get('category_filter', '')
            base_commission = float(request.form['base_commission'])
            
            query = Hotel.query.filter(
                Hotel.price >= min_price,
                Hotel.price <= max_price,
                Hotel.is_active == True
            )
            
            if category:
                query = query.filter_by(category=category)
            
            hotels = query.all()
            
            for user_id in user_ids:
                for hotel in hotels:
                    # Check if assignment already exists
                    existing = UserHotelAssignment.query.filter_by(
                        user_id=user_id,
                        hotel_id=hotel.id,
                        session_type=session_type
                    ).first()
                    
                    if not existing:
                        new_assignment = UserHotelAssignment(
                            user_id=user_id,
                            hotel_id=hotel.id,
                            session_type=session_type,
                            custom_commission=base_commission,
                            assigned_by=current_user.id
                        )
                        db.session.add(new_assignment)
                        assignments_created += 1
        
        else:  # specific hotels
            hotel_ids = request.form.getlist('hotel_ids')
            
            for user_id in user_ids:
                for hotel_id in hotel_ids:
                    commission = float(request.form.get(f'commission_{hotel_id}', 0.0))
                    
                    # Check if assignment already exists
                    existing = UserHotelAssignment.query.filter_by(
                        user_id=user_id,
                        hotel_id=hotel_id,
                        session_type=session_type
                    ).first()
                    
                    if not existing:
                        new_assignment = UserHotelAssignment(
                            user_id=user_id,
                            hotel_id=hotel_id,
                            session_type=session_type,
                            custom_commission=commission,
                            assigned_by=current_user.id
                        )
                        db.session.add(new_assignment)
                        assignments_created += 1
        
        db.session.commit()
        flash(f'Created {assignments_created} new hotel assignments', 'success')
        return redirect(url_for('manage_hotels'))
    
    # GET request - show form with filtering
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    users = User.query.filter_by(is_active=True).all()
    
    # Build hotel query with filters
    query = Hotel.query.filter_by(is_active=True)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if min_price is not None:
        query = query.filter(Hotel.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Hotel.price <= max_price)
    
    hotels = query.order_by(Hotel.category, Hotel.price, Hotel.name).all()
    
    # Get price range for the form
    price_stats = db.session.query(
        db.func.min(Hotel.price).label('min_price'),
        db.func.max(Hotel.price).label('max_price')
    ).filter_by(is_active=True).first()
    
    return render_template('admin_bulk_assign_hotels.html', 
                         users=users, 
                         hotels=hotels,
                         category_filter=category_filter,
                         min_price=min_price,
                         max_price=max_price,
                         price_stats=price_stats)

# NEW: API endpoint for dynamic hotel filtering
@app.route('/admin/api/hotels/filter')
@admin_required
def filter_hotels_api():
    """API endpoint to filter hotels dynamically"""
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Build query
    query = Hotel.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if min_price is not None:
        query = query.filter(Hotel.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Hotel.price <= max_price)
    
    hotels = query.order_by(Hotel.category, Hotel.price, Hotel.name).all()
    
    result = []
    for hotel in hotels:
        result.append({
            'id': hotel.id,
            'name': hotel.name,
            'category': hotel.category,
            'price': float(hotel.price),
            'location': hotel.location,
            'commission_multiplier': float(hotel.commission_multiplier)
        })
    
    return jsonify({
        'hotels': result,
        'count': len(result),
        'total_hotels': Hotel.query.filter_by(is_active=True).count()
    })

# NEW: Quick assignment presets
@app.route('/admin/assignment-presets')
@admin_required
def assignment_presets():
    """Predefined assignment presets for common scenarios"""
    presets = {
        'budget_hotels': {
            'name': 'Budget Hotels',
            'description': 'Hotels under £500',
            'max_price': 500,
            'suggested_commission': 10.0
        },
        'mid_range_hotels': {
            'name': 'Mid-Range Hotels', 
            'description': 'Hotels between £500-£1500',
            'min_price': 500,
            'max_price': 1500,
            'suggested_commission': 15.0
        },
        'luxury_hotels': {
            'name': 'Luxury Hotels',
            'description': 'Hotels above £1500',
            'min_price': 1500,
            'suggested_commission': 20.0
        },
        'regular_category': {
            'name': 'Regular Category',
            'description': 'All regular category hotels',
            'category': 'regular',
            'suggested_commission': 12.0
        },
        'luxury_category': {
            'name': 'Luxury Category',
            'description': 'All luxury category hotels',
            'category': 'luxury',
            'suggested_commission': 18.0
        }
    }
    
    return render_template('admin_assignment_presets.html', presets=presets)

@app.route('/admin/apply-preset', methods=['POST'])
@admin_required
def apply_assignment_preset():
    """Apply a predefined assignment preset"""
    preset_name = request.form['preset']
    user_ids = request.form.getlist('user_ids')
    session_type = request.form['session_type']
    
    # Define preset configurations
    presets = {
        'budget_hotels': {'max_price': 500, 'commission': 10.0},
        'mid_range_hotels': {'min_price': 500, 'max_price': 1500, 'commission': 15.0},
        'luxury_hotels': {'min_price': 1500, 'commission': 20.0},
        'regular_category': {'category': 'regular', 'commission': 12.0},
        'luxury_category': {'category': 'luxury', 'commission': 18.0}
    }
    
    if preset_name not in presets:
        flash('Invalid preset selected', 'error')
        return redirect(url_for('assignment_presets'))
    
    preset_config = presets[preset_name]
    
    # Build hotel query based on preset
    query = Hotel.query.filter_by(is_active=True)
    
    if 'category' in preset_config:
        query = query.filter_by(category=preset_config['category'])
    
    if 'min_price' in preset_config:
        query = query.filter(Hotel.price >= preset_config['min_price'])
    
    if 'max_price' in preset_config:
        query = query.filter(Hotel.price <= preset_config['max_price'])
    
    hotels = query.all()
    assignments_created = 0
    
    for user_id in user_ids:
        for hotel in hotels:
            # Check if assignment already exists
            existing = UserHotelAssignment.query.filter_by(
                user_id=user_id,
                hotel_id=hotel.id,
                session_type=session_type
            ).first()
            
            if not existing:
                new_assignment = UserHotelAssignment(
                    user_id=user_id,
                    hotel_id=hotel.id,
                    session_type=session_type,
                    custom_commission=preset_config['commission'],
                    assigned_by=current_user.id
                )
                db.session.add(new_assignment)
                assignments_created += 1
    
    db.session.commit()
    flash(f'Applied {preset_name} preset: Created {assignments_created} new assignments', 'success')
    return redirect(url_for('manage_hotel_assignments'))

# Enhanced hotel management with price-based insights
@app.route('/admin/hotels/price-analysis')
@admin_required
def hotel_price_analysis():
    """Analyze hotel pricing and assignment patterns"""
    from sqlalchemy import func
    
    # Price distribution analysis
    price_ranges = [
        {'name': 'Budget', 'min': 0, 'max': 500},
        {'name': 'Mid-Range', 'min': 500, 'max': 1500},
        {'name': 'Luxury', 'min': 1500, 'max': float('inf')}
    ]
    
    analysis = []
    for range_info in price_ranges:
        query = Hotel.query.filter_by(is_active=True)
        
        if range_info['max'] == float('inf'):
            query = query.filter(Hotel.price >= range_info['min'])
        else:
            query = query.filter(
                Hotel.price >= range_info['min'],
                Hotel.price < range_info['max']
            )
        
        hotels_in_range = query.all()
        total_assignments = sum(
            UserHotelAssignment.query.filter_by(hotel_id=hotel.id).count()
            for hotel in hotels_in_range
        )
        
        analysis.append({
            'range_name': range_info['name'],
            'hotel_count': len(hotels_in_range),
            'total_assignments': total_assignments,
            'avg_price': sum(hotel.price for hotel in hotels_in_range) / len(hotels_in_range) if hotels_in_range else 0,
            'price_range': f"${range_info['min']:.0f} - ${range_info['max']:.0f}" if range_info['max'] != float('inf') else f"${range_info['min']:.0f}+"
        })
    
    # Category-based analysis
    category_analysis = []
    for category in ['regular', 'luxury']:
        hotels = Hotel.query.filter_by(category=category, is_active=True).all()
        if hotels:
            avg_price = sum(hotel.price for hotel in hotels) / len(hotels)
            total_assignments = sum(
                UserHotelAssignment.query.filter_by(hotel_id=hotel.id).count()
                for hotel in hotels
            )
            
            category_analysis.append({
                'category': category,
                'hotel_count': len(hotels),
                'avg_price': avg_price,
                'total_assignments': total_assignments,
                'min_price': min(hotel.price for hotel in hotels),
                'max_price': max(hotel.price for hotel in hotels)
            })
    
    return render_template('admin_hotel_price_analysis.html',
                         price_analysis=analysis,
                         category_analysis=category_analysis)
@app.route('/admin/luxury_orders/create', methods=['GET', 'POST'])
@admin_required
def admin_create_luxury_order():
    if request.method == 'GET':
        # Remove is_admin filter since the field doesn't exist in your User model
        # You can add other filtering criteria if needed
        users = User.query.order_by(User.username).all()
        return render_template('admin/create_luxury_order.html', users=users)
    
    # Handle POST request (keep existing functionality)
    try:
        data = request.get_json() if request.is_json else request.form
        
        # Debug: Print received data
        print(f"Received data: {dict(data)}")
        print(f"Request content type: {request.content_type}")
        print(f"Is JSON: {request.is_json}")
        
        # Validate required fields
        required_fields = ['user_id', 'title', 'amount']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing field: {field}")
                if request.is_json:
                    return jsonify({'error': f'{field} is required'}), 400
                else:
                    flash(f'{field} is required', 'error')
                    return redirect(url_for('admin_create_luxury_order'))
        
        # Get user
        user = User.query.get_or_404(data['user_id'])
        print(f"Found user: {user.id} - {getattr(user, 'contact', 'N/A')}")
        
        # Check if session user_id exists (try different possible session keys)
        admin_user_id = None
        possible_keys = ['user_id', 'admin_id', 'admin_user_id']
        
        for key in possible_keys:
            if key in session:
                admin_user_id = session[key]
                print(f"Found admin user ID in session['{key}']: {admin_user_id}")
                break
        
        if admin_user_id is None:
            print(f"Error: No admin user ID found in session. Available keys: {list(session.keys())}")
            if request.is_json:
                return jsonify({'error': 'Session expired. Please login again.'}), 401
            else:
                flash('Session expired. Please login again.', 'error')
                return redirect(url_for('admin_login'))
        
        # Create luxury order
        luxury_order = LuxuryOrder(
            user_id=user.id,
            title=data['title'],
            description=data.get('description', ''),
            amount=float(data['amount']),
            image_url=data.get('image_url', ''),
            created_by=admin_user_id
        )
        print(f"Created luxury order object")
        
        # Set expiration if provided (handle None values properly)
        expires_in_hours = data.get('expires_in_hours')
        if expires_in_hours is not None and expires_in_hours != '' and expires_in_hours != 'None':
            try:
                expires_in_hours = int(expires_in_hours)
                luxury_order.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
                print(f"Set expiration to {expires_in_hours} hours")
            except (ValueError, TypeError) as e:
                print(f"Invalid expires_in_hours value: {expires_in_hours}, error: {e}")
        
        print(f"About to add to database")
        db.session.add(luxury_order)
        print(f"Added to session, about to commit")
        db.session.commit()
        print(f"Successfully committed to database")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': f'Luxury order created successfully for {getattr(user, "contact", user.id)}',
                'order_id': luxury_order.id
            })
        else:
            flash(f'Luxury order created successfully for {getattr(user, "contact", user.id)}!', 'success')
            return redirect(url_for('admin_luxury_orders'))
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creating luxury order: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Error creating luxury order: {str(e)}', 'error')
            return redirect(url_for('admin_create_luxury_order'))

# Admin Route to View All Luxury Orders
@app.route('/admin/luxury_orders')
@admin_required
def admin_luxury_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    orders = LuxuryOrder.query.join(User, LuxuryOrder.user_id == User.id)\
                             .order_by(LuxuryOrder.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin_luxury_orders.html', orders=orders)


# User Route to Get Active Luxury Orders (for popup)
@app.route('/api/luxury_orders/active')
def get_active_luxury_orders():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    active_orders = LuxuryOrder.query.filter_by(
        user_id=user_id,
        status='active'
    ).filter(
        db.or_(
            LuxuryOrder.expires_at.is_(None),
            LuxuryOrder.expires_at > datetime.utcnow()
        )
    ).order_by(LuxuryOrder.created_at.desc()).all()
    
    orders_data = []
    for order in active_orders:
        orders_data.append({
            'id': order.id,
            'title': order.title,
            'description': order.description,
            'amount': order.amount,
            'image_url': order.image_url,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'expires_at': order.expires_at.strftime('%Y-%m-%d %H:%M') if order.expires_at else None
        })
    
    return jsonify({'orders': orders_data})


# User Route to Claim Luxury Order
@app.route('/api/luxury_orders/<int:order_id>/claim', methods=['POST'])
def claim_luxury_order(order_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        luxury_order = LuxuryOrder.query.get_or_404(order_id)
        
        # Validate ownership
        if luxury_order.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if can claim
        if not luxury_order.can_claim():
            return jsonify({'error': 'This order cannot be claimed'}), 400
        
        # Credit user account
        old_balance = user.balance
        user.balance += luxury_order.amount
        
        # Update order status
        luxury_order.status = 'claimed'
        luxury_order.claimed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order amount has been credited to your account!',
            'amount_credited': luxury_order.amount,
            'old_balance': old_balance,
            'new_balance': user.balance,
            'order_title': luxury_order.title
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error claiming luxury order: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Admin API Route to Delete/Cancel Luxury Order
@app.route('/admin/api/luxury_orders/<int:order_id>/cancel', methods=['DELETE'])
@admin_required
def admin_cancel_luxury_order(order_id):
    try:
        luxury_order = LuxuryOrder.query.get_or_404(order_id)
        
        if luxury_order.status == 'claimed':
            return jsonify({'error': 'Cannot cancel already claimed order'}), 400
        
        luxury_order.status = 'expired'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Luxury order cancelled successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500