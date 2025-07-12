from hotel_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
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
    session_locked = db.Column(db.Boolean, default=False)
    total_commission_earned = db.Column(db.Float, default=0.0)
    first_session_completed = db.Column(db.Boolean, default=False)
    session_reset_date = db.Column(db.String)
    bound_wallet_type = db.Column(db.String(20))
    max_first_session_reservations = db.Column(db.Integer, default=35)
    wallet_bound_at = db.Column(db.DateTime)
    second_session_reservations_count = db.Column(db.Integer, default=0)
    second_session_commission = db.Column(db.Float, default=0.0)
    bound_wallet_address = db.Column(db.String(200))
    first_session_commission = db.Column(db.Float, default=0.0)
    first_session_reservations_count = db.Column(db.Integer, default=0)
    current_session = db.Column(db.String(10), default='first')
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    deposit_requests = db.relationship('DepositRequest', backref='user', lazy=True)
    withdrawal_requests = db.relationship('WithdrawalRequest', backref='user', lazy=True)
    hotel_assignments = db.relationship('UserHotelAssignment', backref='user', lazy=True)
    hotel_ratings = db.relationship('UserHotelRating', backref='user', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.user_id:
            self.user_id = self.generate_user_id()
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def set_withdrawal_password(self, password):
        """Set withdrawal password hash"""
        self.withdrawal_password = generate_password_hash(password)
    
    def check_withdrawal_password(self, password):
        """Check if provided withdrawal password matches hash"""
        return check_password_hash(self.withdrawal_password, password)
            
    def generate_user_id(self):
        """Generate a unique 6-digit numeric ID"""
        while True:
            user_id = str(random.randint(100000, 999999))
            if not User.query.filter_by(user_id=user_id).first():
                return user_id
    
    def can_make_reservation(self):
        """Check if user can make a reservation based on session limits"""
        today = datetime.now().date().isoformat()
        
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
        rated_hotel_ids = [r.hotel_id for r in self.hotel_ratings 
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
        
        return sum(r.commission_earned for r in unpaid_reservations if r.commission_earned)
    
    def reset_daily_commission(self):
        """Reset daily commission counters (called on new day)"""
        self.first_session_commission = 0.0
        self.second_session_commission = 0.0
        db.session.commit()

class InvitationCode(db.Model):
    __tablename__ = 'invitation_code'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #used_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #used_at = db.Column(db.DateTime)
    
    @staticmethod
    def generate_code():
        """Generate a unique invitation code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not InvitationCode.query.filter_by(code=code).first():
                return code

class Hotel(db.Model):
    __tablename__ = 'hotel'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    primary_picture = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    commission_multiplier = db.Column(db.Float, default=1.0)
    days_available = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    rating = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='hotel', lazy=True)
    user_assignments = db.relationship('UserHotelAssignment', backref='hotel', lazy=True)
    user_ratings = db.relationship('UserHotelRating', backref='hotel', lazy=True)

    def get_average_rating(self):
        """Calculate average rating from all user ratings"""
        if not self.user_ratings:
            return self.rating or 5  # Default rating if no reviews
        return round(sum(r.rating for r in self.user_ratings) / len(self.user_ratings))

class UserHotelAssignment(db.Model):
    __tablename__ = 'user_hotel_assignment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    session_type = db.Column(db.String(10), nullable=False)
    custom_commission = db.Column(db.Float, nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', 'session_type'),)

class UserHotelRating(db.Model):
    __tablename__ = 'user_hotel_rating'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    session_type = db.Column(db.String(10), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text)
    commission_earned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate ratings
    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', 'session_type'),)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    commission_earned = db.Column(db.Float, default=0.0)
    commission_paid = db.Column(db.Boolean, default=False)
    commission_paid_at = db.Column(db.DateTime)
    session_type = db.Column(db.String(10))
    
    def __init__(self, **kwargs):
        super(Reservation, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    def generate_order_number(self):
        """Generate a unique order number"""
        while True:
            order_number = 'ORD' + ''.join(random.choices(string.digits, k=10))
            if not Reservation.query.filter_by(order_number=order_number).first():
                return order_number
    
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
        if not self.commission_earned:
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
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    assigned_hotels = db.relationship('UserHotelAssignment', backref='assigned_by_admin', lazy=True)
    processed_deposits = db.relationship('DepositRequest', backref='processed_by_admin', lazy=True)
    processed_withdrawals = db.relationship('WithdrawalRequest', backref='processed_by_admin', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

class DepositRequest(db.Model):
    __tablename__ = 'deposit_request'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    network = db.Column(db.String(20), nullable=False)
    wallet_address = db.Column(db.String(200))
    transaction_hash = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
    
    @staticmethod
    def validate_wallet_address(address, network):
        """
        Wallet address validation for different networks
        Returns True if valid, False otherwise
        """
        import re
        
        if not address or not network:
            return False
            
        network = network.upper()
        
        # USDT on Ethereum (ERC-20)
        if network in ['ETH', 'ERC20']:
            eth_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(eth_pattern, address) is not None
        
        # USDT on Tron (TRC-20)
        elif network in ['TRX', 'TRC20', 'TRON']:
            tron_pattern = r'^T[A-Za-z1-9]{33}$'
            return re.match(tron_pattern, address) is not None
        
        # USDT on Binance Smart Chain (BEP-20)
        elif network in ['BSC', 'BEP20']:
            bsc_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(bsc_pattern, address) is not None
        
        # USDT on Bitcoin (Omni Layer)
        elif network in ['BTC', 'OMNI']:
            btc_pattern = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'
            return re.match(btc_pattern, address) is not None
        
        # USDT on Polygon
        elif network in ['POLYGON', 'MATIC']:
            polygon_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(polygon_pattern, address) is not None
        
        # USDT on Avalanche
        elif network in ['AVAX', 'AVALANCHE']:
            avax_pattern = r'^0x[a-fA-F0-9]{40}$'
            return re.match(avax_pattern, address) is not None
        
        # USDT on Solana
        elif network in ['SOL', 'SOLANA']:
            sol_pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
            return re.match(sol_pattern, address) is not None
            
        return False

class WithdrawalRequest(db.Model):
    __tablename__ = 'withdrawal_request'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    network = db.Column(db.String(20), nullable=False)
    wallet_address = db.Column(db.String(200), nullable=False)
    transaction_hash = db.Column(db.String(200))
    transaction_fee = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Pending')
    admin_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
    
    @staticmethod
    def validate_wallet_address(address, network):
        """Use the same validation as DepositRequest"""
        return DepositRequest.validate_wallet_address(address, network)

class EventAd(db.Model):
    __tablename__ = 'event_ad'
    
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200))
    caption = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        """Get a system setting value"""
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set a system setting value"""
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
            if description:
                setting.description = description
        else:
            setting = SystemSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting