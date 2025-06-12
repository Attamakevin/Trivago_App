from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), default='ordinary')
    is_active = db.Column(db.Boolean, default=True)
    balance = db.Column(db.Float, default=0.0)
    daily_review_count = db.Column(db.Integer, default=0)
    wallet = db.Column(db.String(256), nullable=True)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    location = db.Column(db.String(100))
    images = db.relationship('HotelImage', backref='hotel', cascade="all, delete-orphan")

class HotelImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    image_url = db.Column(db.String(255))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LevelRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    level_requested = db.Column(db.String(20))
    tx_hash = db.Column(db.String(256))
    status = db.Column(db.String(20), default='pending')

class WithdrawRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    wallet_address = db.Column(db.String(256))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
