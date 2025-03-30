import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("SESSION_SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///routes.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ORS_API_KEY"] = os.environ.get("ORS_API_KEY", "")

# Initialize extensions
db.init_app(app)

# Import routes after app initialization to avoid circular imports
from routes import *  # noqa: E402

with app.app_context():
    # Import models here to ensure they're registered with SQLAlchemy
    from models import Location, Route, RouteLocation  # noqa: F401
    db.create_all()