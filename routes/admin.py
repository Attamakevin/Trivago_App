from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models import Hotel, HotelImage, LevelRequest, WithdrawRequest, User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin/hotels.html', hotels=Hotel.query.all())

@admin_bp.route('/admin/hotels/add', methods=['GET', 'POST'])
@login_required
def add_hotel():
    if request.method == 'POST':
        hotel = Hotel(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            location=request.form['location']
        )
        db.session.add(hotel)
        db.session.flush()
        for i in range(1, 4):
            img_url = request.form.get(f'image{i}')
            if img_url:
                db.session.add(HotelImage(hotel_id=hotel.id, image_url=img_url))
        db.session.commit()
        flash("Hotel added.")
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/add_hotel.html')

@admin_bp.route('/admin/levels')
@login_required
def level_requests():
    requests = LevelRequest.query.filter_by(status='pending').all()
    return render_template('admin/level_requests.html', requests=requests)

@admin_bp.route('/admin/approve_level/<int:request_id>')
@login_required
def approve_level(request_id):
    req = LevelRequest.query.get(request_id)
    if req:
        user = User.query.get(req.user_id)
        user.role = req.level_requested
        req.status = 'approved'
        db.session.commit()
        flash("User level approved.")
    return redirect(url_for('admin.level_requests'))

@admin_bp.route('/admin/withdrawals')
@login_required
def withdrawals():
    withdrawals = WithdrawRequest.query.filter_by(status='pending').all()
    return render_template('admin/withdrawals.html', withdrawals=withdrawals)

@admin_bp.route('/admin/approve_withdrawal/<int:withdraw_id>')
@login_required
def approve_withdrawal(withdraw_id):
    req = WithdrawRequest.query.get(withdraw_id)
    if req:
        user = User.query.get(req.user_id)
        if req.amount <= user.balance:
            user.balance -= req.amount
            req.status = 'approved'
            db.session.commit()
            flash("Withdrawal approved.")
    return redirect(url_for('admin.withdrawals'))

@admin_bp.route('/admin/toggle_user/<int:user_id>')
@login_required
def toggle_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
        flash("User status toggled.")
    return redirect(url_for('admin.admin_dashboard'))
