from hotel_app import db
from flask_login import UserMixin
from datetime import datetime

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

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    order_number = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Processing')
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    commission_earned = db.Column(db.Float, default=0.0)

class DepositRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    network = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    network = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')

class EventAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200))
    caption = db.Column(db.String(200))