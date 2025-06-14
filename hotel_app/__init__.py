from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, template_folder="./templates")
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel_app.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# Register user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # adjust this for your ORM if needed

from hotel_app import routes, models
