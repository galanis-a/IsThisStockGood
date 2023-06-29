import logging

from flask import (
    Flask
)
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

logger = logging.getLogger("IsThisStockGood")

handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)

h_format = logging.Formatter('%(name)s - %(levelname)s : %(message)s')
handler.setFormatter(h_format)

logger.addHandler(handler)


def create_app():
    app = Flask(__name__)

    app.secret_key = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app
