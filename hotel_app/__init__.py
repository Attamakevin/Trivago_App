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


# ✅ Import models before anything that depends on them
from hotel_app.models import User  # explicitly import User for user_loader
from hotel_app import routes, models  # keep your routes import

# ✅ Register user_loader after importing User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Create tables if they don't exist (optional, dev only)
with app.app_context():
    db.create_all()