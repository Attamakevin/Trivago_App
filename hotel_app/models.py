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
    trial_bonus = db.Column(db.Float, default=564.00)
    balance = db.Column(db.Float, default=0.00)
    total_deposits = db.Column(db.Float, default=0.0)
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
    # REVOLUT SPECIFIC FIELDS
    revolut_name = db.Column(db.String(100))
    revolut_iban = db.Column(db.String(50))
    revolut_revtag = db.Column(db.String(20))
    # ADD THESE NEW FIELDS FOR IP AND LOCATION TRACKING
    ip_address = db.Column(db.String(45))  # IPv6 can be up to 45 characters
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(2))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50))
    isp = db.Column(db.String(255))
    last_location_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    
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
    reservations = db.relationship('Reservation', backref='user', cascade="all, delete-orphan",
        passive_deletes=True,lazy=True)
    deposit_requests = db.relationship('DepositRequest', backref='user', lazy=True)
    withdrawal_requests = db.relationship('WithdrawalRequest', backref='user', lazy=True)
<<<<<<< HEAD
    user_hotel_assignments = db.relationship('UserHotelAssignment', backref='user', lazy=True)
    rated_hotels = db.relationship('UserHotelRating', backref='user', lazy=True)
   
=======
    hotel_assignments = db.relationship('UserHotelAssignment', backref='user',cascade="all, delete-orphan",
        passive_deletes=True, lazy=True)
    hotel_ratings = db.relationship('UserHotelRating', backref='user', lazy=True)

>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.user_id:
            self.user_id = self.generate_user_id()
<<<<<<< HEAD
            
    def generate_user_id(self):
        # Generate a 6-digit numeric ID
        return str(random.randint(100000, 999999))
    
    def can_make_reservation(self):
        """Check if user can make a reservation based on session limits"""
        today = datetime.now().date()
=======
    
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
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
        
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
<<<<<<< HEAD
        rated_hotel_ids = [r.hotel_id for r in self.rated_hotels 
=======
        rated_hotel_ids = [r.hotel_id for r in self.hotel_ratings 
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
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
        
<<<<<<< HEAD
        return sum(r.commission_earned for r in unpaid_reservations)
=======
        return sum(r.commission_earned for r in unpaid_reservations if r.commission_earned)
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
    
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
    
    # New fields for categorization
    category = db.Column(db.String(50), default='regular')  # 'regular' or 'luxury'
    is_active = db.Column(db.Boolean, default=True)  # Admin can activate/deactivate
    
    # Relationships
    reservations = db.relationship('Reservation', backref='hotel', lazy=True)
    user_assignments = db.relationship('UserHotelAssignment', backref='hotel', lazy=True)
    user_ratings = db.relationship('UserHotelRating', backref='hotel', lazy=True)
<<<<<<< HEAD
    
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
=======
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6

    def get_average_rating(self):
        """Calculate average rating from all user ratings"""
        if not self.user_ratings:
            return self.rating or 5  # Default rating if no reviews
        return round(sum(r.rating for r in self.user_ratings) / len(self.user_ratings))

class UserHotelAssignment(db.Model):
    __tablename__ = 'user_hotel_assignment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    commission_earned = db.Column(db.Float, default=0.0)
    commission_paid = db.Column(db.Boolean, default=False)
<<<<<<< HEAD
    commission_paid_at = db.Column(db.DateTime, nullable=True)
    
    # New fields for session tracking
    session_type = db.Column(db.String(10))  # 'first' or 'second'
=======
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
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
    
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
<<<<<<< HEAD
        if self.commission_earned == 0.0:
=======
        if not self.commission_earned:
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
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
    __tablename__ = 'deposit_request'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    network = db.Column(db.String(20), nullable=False)
<<<<<<< HEAD
    wallet_address = db.Column(db.String(200), nullable=True)
=======
    wallet_address = db.Column(db.String(200))
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
    transaction_hash = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
<<<<<<< HEAD
    
    processed_by_admin = db.relationship('Admin', backref='processed_deposits', lazy=True)
=======
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
    
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
        
<<<<<<< HEAD
        # USDT on Bitcoin (Omni Layer) - Legacy format
        elif network == 'BTC' or network == 'OMNI':
=======
        # USDT on Bitcoin (Omni Layer)
        elif network in ['BTC', 'OMNI']:
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
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
    
<<<<<<< HEAD
    processed_by_admin = db.relationship('Admin', backref='processed_withdrawals', lazy=True)
=======
    # Add relationship to User model
    #user = db.relationship('User', backref='withdrawal_requests', lazy=True)
>>>>>>> 63f7ce8ae281c05fcd8d1abf23b2d07379e957a6
    
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
    # Database Model (add to your models.py)
class LuxuryOrder(db.Model):
    __tablename__ = 'luxury_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default='active')  # active, claimed, expired
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Admin who created it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='luxury_orders')
    admin = db.relationship('User', foreign_keys=[created_by])
    
    def is_expired(self):
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def can_claim(self):
        return self.status == 'active' and not self.is_expired()
