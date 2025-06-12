from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import Hotel, HotelImage, Review, LevelRequest, WithdrawRequest, User
from datetime import date

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@user_bp.route('/hotels')
@login_required
def list_hotels():
    hotels = Hotel.query.all()
    return render_template('hotels.html', hotels=hotels)

@user_bp.route('/review/<int:hotel_id>', methods=['POST'])
@login_required
def submit_review(hotel_id):
    user = User.query.get(current_user.id)
    level_limits = {'ordinary': 5, 'silver': 10, 'gold': 20, 'diamond': 50}
    if user.daily_review_count >= level_limits.get(user.role, 5):
        flash("Review limit reached.")
        return redirect(url_for('user.list_hotels'))
    rating = int(request.form['rating'])
    comment = request.form['comment']
    review = Review(user_id=user.id, hotel_id=hotel_id, rating=rating, comment=comment)
    db.session.add(review)
    hotel = Hotel.query.get(hotel_id)
    reward = hotel.price * 0.02
    user.balance += reward
    user.daily_review_count += 1
    db.session.commit()
    flash("Review submitted! You earned ${:.2f}".format(reward))
    return redirect(url_for('user.list_hotels'))

@user_bp.route('/upgrade', methods=['POST'])
@login_required
def request_upgrade():
    level = request.form['level']
    tx_hash = request.form['tx_hash']
    req = LevelRequest(user_id=current_user.id, level_requested=level, tx_hash=tx_hash)
    db.session.add(req)
    db.session.commit()
    flash("Upgrade request submitted.")
    return redirect(url_for('user.dashboard'))

@user_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    wallet_address = request.form['wallet']
    amount = float(request.form['amount'])
    if amount > current_user.balance:
        flash("Insufficient balance.")
        return redirect(url_for('user.dashboard'))
    req = WithdrawRequest(user_id=current_user.id, wallet_address=wallet_address, amount=amount)
    db.session.add(req)
    db.session.commit()
    flash("Withdrawal request submitted.")
    return redirect(url_for('user.dashboard'))
