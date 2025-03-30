from app import db
from datetime import datetime

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    total_distance = db.Column(db.Float)  # in meters
    total_duration = db.Column(db.Float)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RouteLocation(db.Model):
    __tablename__ = 'route_locations'
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), primary_key=True)
    sequence = db.Column(db.Integer, nullable=False)

    # Define relationships
    route = db.relationship('Route', backref=db.backref('route_locations', cascade='all, delete-orphan'))
    location = db.relationship('Location')