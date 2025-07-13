from hotel_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80))
    user_id = db.Column(db.String(6), unique=True)
    agent_id = db.Column(db.String(6), unique=True)
    contact = db.Column(db.String(20))
    invitation_code = db.Column(db.String(20))
    member_points = db.Column(db.Integer, default=0)
    balance = db.Column(db.Float, default=0.0)
    vip_level = db.Column(db.String(10), default='VIP0')
    withdrawal_password = db.Column(db.String(100))
    password_hash = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # New wallet binding fields
    bound_wallet_type = db.Column(db.String(20))  # USDT, ETH, PAYPAL, REVOLUT
    bound_wallet_address = db.Column(db.String(200))  # Wallet address/email/phone
    wallet_bound_at = db.Column(db.DateTime)  # When wallet was bound
    
   # New fields for session management
    current_session = db.Column(db.String(10), default='first')  # 'first' or 'second'
    session_reset_date = db.Column(db.Date)  # Date when session was last reset
    first_session_completed = db.Column(db.Boolean, default=False)
    first_session_reservations_count = db.Column(db.Integer, default=0)
    second_session_reservations_count = db.Column(db.Integer, default=0)
    max_first_session_reservations = db.Column(db.Integer, default=35)
    session_locked = db.Column(db.Boolean, default=False)  # Lock between sessions
    
    # Commission tracking
    total_commission_earned = db.Column(db.Float, default=0.0)  # Total commissions earned
    first_session_commission = db.Column(db.Float, default=0.0)  # Commission from first session
    second_session_commission = db.Column(db.Float, default=0.0)  # Commission from second session
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    deposit_requests = db.relationship('DepositRequest', backref='user', lazy=True)
    withdrawal_requests = db.relationship('WithdrawalRequest', backref='user', lazy=True)
    user_hotel_assignments = db.relationship('UserHotelAssignment', backref='user', lazy=True)
    rated_hotels = db.relationship('UserHotelRating', backref='user', lazy=True)
   
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.user_id:
            self.user_id = self.generate_user_id()
            
    def generate_user_id(self):
        # Generate a 6-digit numeric ID
        return str(random.randint(100000, 999999))
    
    def can_make_reservation(self):
        """Check if user can make a reservation based on session limits"""
        today = datetime.now().date()
        
        # Reset daily counters if it's a new day
        if self.session_reset_date != today:
            self.first_session_reservations_count = 0
            self.second_session_reservations_count = 0
            self.first_session_completed = False
            self.session_locked = False
            self.current_session = 'first'
            self.session_reset_date = today
            # Reset daily commission counters
            self.reset_daily_commission()
            db.session.commit()
        
        # Check first session limits
        if self.current_session == 'first':
            return self.first_session_reservations_count < self.max_first_session_reservations
        
        # Check if user is locked between sessions
        if self.session_locked:
            return False
        
        # Second session has no specific limit (controlled by admin)
        return self.current_session == 'second'
    
    def complete_first_session(self):
        """Mark first session as completed and lock user"""
        self.first_session_completed = True
        self.session_locked = True
        db.session.commit()
    
    def reset_session_by_admin(self, new_session='second'):
        """Admin function to reset user's session"""
        self.current_session = new_session
        self.session_locked = False
        if new_session == 'first':
            self.first_session_reservations_count = 0
            self.first_session_completed = False
        elif new_session == 'second':
            self.second_session_reservations_count = 0
        db.session.commit()
    
    def get_available_hotels(self):
        """Get hotels available for current session that user hasn't rated"""
        # Get rated hotel IDs for current session
        rated_hotel_ids = [r.hotel_id for r in self.rated_hotels 
                          if r.session_type == self.current_session]
        
        # Get assigned hotels for current session
        assigned_hotels = UserHotelAssignment.query.filter_by(
            user_id=self.id,
            session_type=self.current_session
        ).all()
        
        # Filter out already rated hotels
        available_assignments = [a for a in assigned_hotels 
                               if a.hotel_id not in rated_hotel_ids]
        
        return available_assignments
    
    def add_commission(self, amount, session_type):
        """Add commission to user's total and session-specific totals"""
        self.total_commission_earned += amount
        
        if session_type == 'first':
            self.first_session_commission += amount
        elif session_type == 'second':
            self.second_session_commission += amount
        
        db.session.commit()
    
    def get_commission_summary(self):
        """Get commission breakdown for the user"""
        return {
            'total_commission': self.total_commission_earned,
            'first_session_commission': self.first_session_commission,
            'second_session_commission': self.second_session_commission,
            'unpaid_commission': self.get_unpaid_commission()
        }
    
    def get_unpaid_commission(self):
        """Calculate total unpaid commission from all reservations"""
        unpaid_reservations = Reservation.query.filter_by(
            user_id=self.id,
            commission_paid=False
        ).all()
        
        return sum(r.commission_earned for r in unpaid_reservations)
    
    def reset_daily_commission(self):
        """Reset daily commission counters (called on new day)"""
        self.first_session_commission = 0.0
        self.second_session_commission = 0.0
        db.session.commit()

class InvitationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    primary_picture = db.Column(db.String(200))
    price = db.Column(db.Float)
    commission_multiplier = db.Column(db.Float, default=1.0)
    days_available = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    rating = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for categorization
    category = db.Column(db.String(50), default='regular')  # 'regular' or 'luxury'
    is_active = db.Column(db.Boolean, default=True)  # Admin can activate/deactivate
    
    # Relationships
    reservations = db.relationship('Reservation', backref='hotel', lazy=True)
    user_assignments = db.relationship('UserHotelAssignment', backref='hotel', lazy=True)
    user_ratings = db.relationship('UserHotelRating', backref='hotel', lazy=True)
    
    def get_average_rating(self):
        """Calculate average rating from all user ratings"""
        if not self.user_ratings:
            return 5  # Default rating if no reviews
        return round(sum(r.rating for r in self.user_ratings) / len(self.user_ratings))

class UserHotelAssignment(db.Model):
    """Admin assigns specific hotels to users for each session"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    session_type = db.Column(db.String(10), nullable=False)  # 'first' or 'second'
    custom_commission = db.Column(db.Float, nullable=False)  # Admin-set commission for this user-hotel combo
    assigned_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_by_admin = db.relationship('Admin', backref='hotel_assignments', lazy=True)
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', 'session_type', 
                                        name='unique_user_hotel_session'),)

class UserHotelRating(db.Model):
    """Track which hotels user has rated in each session"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    session_type = db.Column(db.String(10), nullable=False)  # 'first' or 'second'
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback = db.Column(db.Text)
    commission_earned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate ratings
    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', 'session_type', 
                                        name='unique_user_hotel_rating'),)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Processing')
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    commission_earned = db.Column(db.Float, default=0.0)
    commission_paid = db.Column(db.Boolean, default=False)
    commission_paid_at = db.Column(db.DateTime, nullable=True)
    
    # New fields for session tracking
    session_type = db.Column(db.String(10))  # 'first' or 'second'
    
    def calculate_commission(self):
        """Calculate commission based on user's hotel assignment"""
        assignment = UserHotelAssignment.query.filter_by(
            user_id=self.user_id,
            hotel_id=self.hotel_id,
            session_type=self.session_type
        ).first()
        
        if assignment:
            self.commission_earned = assignment.custom_commission
            # Add commission to user's totals
            user = User.query.get(self.user_id)
            if user:
                user.add_commission(self.commission_earned, self.session_type)
        
        db.session.commit()
    
    def complete_reservation_with_rating(self, rating, feedback=""):
        """Complete reservation with rating and create rating record"""
        self.rating = rating
        self.feedback = feedback
        self.status = 'Completed'
        
        # Calculate commission if not already calculated
        if self.commission_earned == 0.0:
            self.calculate_commission()
        
        # Create rating record
        user_rating = UserHotelRating(
            user_id=self.user_id,
            hotel_id=self.hotel_id,
            session_type=self.session_type,
            rating=rating,
            feedback=feedback,
            commission_earned=self.commission_earned
        )
        
        db.session.add(user_rating)
        
        # Update user's reservation count
        user = User.query.get(self.user_id)
        if user:
            if self.session_type == 'first':
                user.first_session_reservations_count += 1
                if user.first_session_reservations_count >= user.max_first_session_reservations:
                    user.complete_first_session()
            elif self.session_type == 'second':
                user.second_session_reservations_count += 1
        
        db.session.commit()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def assign_hotels_to_user(self, user_id, hotel_assignments):
        """
        Assign hotels to user for a specific session
        hotel_assignments: list of dicts with keys: hotel_id, session_type, custom_commission
        """
        for assignment in hotel_assignments:
            # Check if assignment already exists
            existing = UserHotelAssignment.query.filter_by(
                user_id=user_id,
                hotel_id=assignment['hotel_id'],
                session_type=assignment['session_type']
            ).first()
            
            if not existing:
                new_assignment = UserHotelAssignment(
                    user_id=user_id,
                    hotel_id=assignment['hotel_id'],
                    session_type=assignment['session_type'],
                    custom_commission=assignment['custom_commission'],
                    assigned_by=self.id
                )
                db.session.add(new_assignment)
        
        db.session.commit()
    
    def get_hotels_for_assignment(self, category=None, min_price=None, max_price=None, 
                                 sort_by='name', sort_order='asc'):
        """
        Get hotels available for assignment with filtering and sorting
        """
        query = Hotel.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if min_price is not None:
            query = query.filter(Hotel.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Hotel.price <= max_price)
        
        # Apply sorting
        if sort_by == 'price':
            if sort_order == 'desc':
                query = query.order_by(Hotel.price.desc())
            else:
                query = query.order_by(Hotel.price.asc())
        elif sort_by == 'rating':
            if sort_order == 'desc':
                query = query.order_by(Hotel.rating.desc())
            else:
                query = query.order_by(Hotel.rating.asc())
        elif sort_by == 'category':
            if sort_order == 'desc':
                query = query.order_by(Hotel.category.desc())
            else:
                query = query.order_by(Hotel.category.asc())
        else:  # Default to name
            if sort_order == 'desc':
                query = query.order_by(Hotel.name.desc())
            else:
                query = query.order_by(Hotel.name.asc())
        
        return query.all()
    
    def pay_user_commission(self, user_id, amount=None):
        """
        Pay commission to user and mark reservations as paid
        If amount is None, pays all unpaid commissions
        """
        user = User.query.get(user_id)
        if not user:
            return False
        
        unpaid_reservations = Reservation.query.filter_by(
            user_id=user_id,
            commission_paid=False
        ).all()
        
        if not unpaid_reservations:
            return False
        
        total_unpaid = sum(r.commission_earned for r in unpaid_reservations)
        
        if amount is None:
            amount = total_unpaid
        
        # Add to user's balance
        user.balance += amount
        
        # Mark reservations as paid (proportionally if partial payment)
        if amount >= total_unpaid:
            # Full payment - mark all as paid
            for reservation in unpaid_reservations:
                reservation.commission_paid = True
                reservation.commission_paid_at = datetime.utcnow()
        else:
            # Partial payment - mark proportionally
            remaining_amount = amount
            for reservation in unpaid_reservations:
                if remaining_amount >= reservation.commission_earned:
                    reservation.commission_paid = True
                    reservation.commission_paid_at = datetime.utcnow()
                    remaining_amount -= reservation.commission_earned
                else:
                    break
        
        db.session.commit()
        return True


class DepositRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    network = db.Column(db.String(20), nullable=False)  # BTC, ETH, USDT, etc.
    wallet_address = db.Column(db.String(200), nullable=True)  # User's wallet address
    transaction_hash = db.Column(db.String(200))  # Optional: for transaction verification
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    admin_notes = db.Column(db.Text)  # Admin can add notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('admin.id'))  # Which admin processed it
    
    # Relationship to admin who processed the request
    processed_by_admin = db.relationship('Admin', backref='processed_deposits', lazy=True)
    
    @staticmethod
    def validate_wallet_address(address, network):
        """
        USDT wallet address validation for different networks
        Returns True if valid, False otherwise
        """
        import re
        
        if not address or not network:
            return False
            
        network = network.upper()
        
        # USDT on Ethereum (ERC-20)
        if network == 'ETH' or network == 'ERC20':
            eth_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(eth_pattern, address) is not None
        
        # USDT on Tron (TRC-20)
        elif network == 'TRX' or network == 'TRC20' or network == 'TRON':
            tron_pattern = r'^T[A-Za-z1-9]{33}$'
            return re.match(tron_pattern, address) is not None
        
        # USDT on Binance Smart Chain (BEP-20)
        elif network == 'BSC' or network == 'BEP20':
            bsc_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(bsc_pattern, address) is not None
        
        # USDT on Bitcoin (Omni Layer) - Legacy format
        elif network == 'BTC' or network == 'OMNI':
            # Bitcoin addresses for USDT (Omni Layer)
            btc_pattern = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'
            return re.match(btc_pattern, address) is not None
        
        # USDT on Polygon (Polygon USDT)
        elif network == 'POLYGON' or network == 'MATIC':
            polygon_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(polygon_pattern, address) is not None
        
        # USDT on Avalanche (AVAX)
        elif network == 'AVAX' or network == 'AVALANCHE':
            avax_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(avax_pattern, address) is not None
        
        # USDT on Solana
        elif network == 'SOL' or network == 'SOLANA':
            sol_pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
            return re.match(sol_pattern, address) is not None
            
        # Unknown network
        else:
            return False

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    network = db.Column(db.String(20), nullable=False)  # BTC, ETH, USDT, etc.
    wallet_address = db.Column(db.String(200), nullable=False)  # Destination wallet address
    transaction_hash = db.Column(db.String(200))  # Transaction hash when processed
    transaction_fee = db.Column(db.Float, default=0.0)  # Network fee deducted
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Completed
    admin_notes = db.Column(db.Text)  # Admin can add notes
    rejection_reason = db.Column(db.Text)  # Reason if rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('admin.id'))  # Which admin processed it
    
    # Relationship to admin who processed the request
    processed_by_admin = db.relationship('Admin', backref='processed_withdrawals', lazy=True)
    
    @staticmethod
    def validate_wallet_address(address, network):
        """
        Use the same validation as DepositRequest
        """
        return DepositRequest.validate_wallet_address(address, network)

class EventAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200))
    caption = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)