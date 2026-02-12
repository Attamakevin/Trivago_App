import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, template_folder="./templates")
app.config['SECRET_KEY'] = 'your-secret-key'

# Use /data disk on Render, fallback to local sqlite file in dev
if os.environ.get('RENDER'):
    db_path = '/data/hotel_app.db'
else:
    db_path = os.path.join(os.path.dirname(__file__), 'hotel_app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

from hotel_app.models import User
from hotel_app import routes, models

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()