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
    member_points = db.Column(db.Integer, default=50)
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
    currency = db.Column(db.String(10), default='$')
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
    
    # IP AND LOCATION TRACKING
    ip_address = db.Column(db.String(45))
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(2))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50))
    isp = db.Column(db.String(255))
    last_location_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ✅ FIX: Correct Relationships - removed duplicates and fixed foreign keys
    reservations = db.relationship(
        'Reservation',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    deposit_requests = db.relationship(
        'DepositRequest',
        backref='user',
        lazy='dynamic'
    )
    
    withdrawal_requests = db.relationship(
        'WithdrawalRequest',
        backref='user',
        lazy='dynamic'
    )
    
    # ✅ FIX: Single hotel_assignments relationship
    hotel_assignments = db.relationship(
        'UserHotelAssignment',
        foreign_keys='UserHotelAssignment.user_id',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    hotel_ratings = db.relationship(
        'UserHotelRating',
        backref='user',
        lazy='dynamic'
    )
    
    # ✅ FIX: Golden eggs relationship
    golden_eggs = db.relationship(
        'GoldenEgg',
        foreign_keys='GoldenEgg.user_id',
        backref='recipient',
        lazy='dynamic'
    )

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
        
        if self.session_reset_date != today:
            self.first_session_reservations_count = 0
            self.second_session_reservations_count = 0
            self.first_session_completed = False
            self.session_locked = False
            self.current_session = 'first'
            self.session_reset_date = today
            self.reset_daily_commission()
            db.session.commit()
        
        if self.current_session == 'first':
            return self.first_session_reservations_count < self.max_first_session_reservations
        
        if self.session_locked:
            return False
        
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
    
    def add_commission(self, amount, session_type):
        """Add commission to user's total and session-specific totals"""
        self.total_commission_earned += amount
        
        if session_type == 'first':
            self.first_session_commission += amount
        elif session_type == 'second':
            self.second_session_commission += amount
        
        db.session.commit()
    
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
    category = db.Column(db.String(50), default='regular')
    is_active = db.Column(db.Boolean, default=True)
    
    # ✅ FIX: Correct Relationships
    reservations = db.relationship(
        'Reservation',
        backref='hotel',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    user_assignments = db.relationship(
        'UserHotelAssignment',
        foreign_keys='UserHotelAssignment.hotel_id',
        backref='hotel',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    user_ratings = db.relationship(
        'UserHotelRating',
        backref='hotel',
        lazy='dynamic'
    )

    def get_average_rating(self):
        """Calculate average rating from all user ratings"""
        ratings = self.user_ratings.all()
        if not ratings:
            return self.rating or 5
        return round(sum(r.rating for r in ratings) / len(ratings))


class UserHotelAssignment(db.Model):
    __tablename__ = 'user_hotel_assignment'

    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ FIX: Correct foreign keys
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    hotel_id = db.Column(
        db.Integer,
        db.ForeignKey('hotel.id', ondelete='CASCADE'),
        nullable=False
    )
    assigned_by = db.Column(
        db.Integer,
        db.ForeignKey('admin.id', ondelete='SET NULL'),
        nullable=True
    )

    session_type = db.Column(db.String(10), nullable=False)
    custom_commission = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    # ✅ FIX: Relationship to admin
    admin = db.relationship('Admin', backref='assignments')


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
    
    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', 'session_type'),)


class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    # ✅ FIX: Allow NULL but with CASCADE on delete
    hotel_id = db.Column(
        db.Integer,
        db.ForeignKey('hotel.id', ondelete='CASCADE'),
        nullable=True
    )
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
    
    # ✅ FIX: Relationships
    processed_deposits = db.relationship(
        'DepositRequest',
        backref='processed_by_admin',
        lazy='dynamic'
    )
    processed_withdrawals = db.relationship(
        'WithdrawalRequest',
        backref='processed_by_admin',
        lazy='dynamic'
    )
    created_golden_eggs = db.relationship(
        'GoldenEgg',
        foreign_keys='GoldenEgg.created_by',
        backref='creator',
        lazy='dynamic'
    )
    
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


class GoldenEgg(db.Model):
    __tablename__ = 'luxury_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default='active')
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    # ADD THIS LINE:
    user = db.relationship('User', foreign_keys=[user_id])
    def is_expired(self):
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def can_claim(self):
        return self.status == 'active' and not self.is_expired()