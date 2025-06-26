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
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    deposit_requests = db.relationship('DepositRequest', backref='user', lazy=True)
    withdrawal_requests = db.relationship('WithdrawalRequest', backref='user', lazy=True)
   
    def __init__(self, **kwargs):
                super(User, self).__init__(**kwargs)
                if not self.user_id:
                    self.user_id = self.generate_user_id()
            
    def generate_user_id(self):
    # Generate a 6-digit numeric ID
        return str(random.randint(100000, 999999))
    
        
            

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
    description = db.Column(db.Text)  # Added for admin hotel management
    location = db.Column(db.String(200))  # Added for admin hotel management
    rating = db.Column(db.Integer, default=5)  # Hotel rating (1-5 stars)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='hotel', lazy=True)
    
    def get_average_rating(self):
        """Calculate average rating from all reservations with ratings"""
        rated_reservations = [r for r in self.reservations if r.rating is not None]
        if not rated_reservations:
            return 5  # Default rating if no reviews
        return round(sum(r.rating for r in rated_reservations) / len(rated_reservations))

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

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))  # Added for admin settings
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DepositRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    network = db.Column(db.String(20), nullable=False)  # BTC, ETH, USDT, etc.
    wallet_address = db.Column(db.String(200), nullable=False)  # User's wallet address
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