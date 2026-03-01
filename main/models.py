"""
This module defines database models for the application.
It provides structure for storing and managing user-related data, transactions, listings, and energy generation.
"""

import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from main import db

# Database model representing a user in the system
class User(db.Model, UserMixin):
    """
    Represents a user in the database.
    
    Attributes:
        id (str): UUID primary key for the user.
        clerk_user_id (str): Unique identifier from Clerk authentication.
        email (str): Email of the user.
        role (str): buyer | seller | admin
        seller_status (str): pending | approved | rejected
        battery_capacity (int): Maximum energy capacity (default 35).
        available_units (int): Available units the user owns (default 0).
        created_at (datetime): Timestamp when created.
    """
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=True) # None until role selected
    seller_status = db.Column(db.String(50), default='pending') 
    battery_capacity = db.Column(db.Integer, default=35)
    available_units = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Double, nullable=True)
    longitude = db.Column(db.Double, nullable=True)
    energy_type = db.Column(db.String(50), default='Solar') # Solar, Wind, etc.
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"

# Database model representing a sell order listing
class Listing(db.Model):
    """
    Represents an energy sell listing in the database.
    """
    __tablename__ = 'listings'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    units_listed = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Double, nullable=False)
    status = db.Column(db.String(50), default='active') # active | sold | cancelled
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    seller = db.relationship('User', foreign_keys=[seller_id], backref='listings')

    def __repr__(self) -> str:
        return f"<Listing {self.id} / Units: {self.units_listed}>"

# Database model representing transaction history
class Transaction(db.Model):
    """
    Represents a transaction record in the database.
    """
    __tablename__ = 'transactions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Double, nullable=False)
    status = db.Column(db.String(50), default='completed') 
    transaction_hash = db.Column(db.String(64), unique=True)
    previous_hash = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')


# Database model representing energy production history
class EnergyProduction(db.Model):
    """
    Represents an energy generation history record.
    """
    __tablename__ = 'energy_production'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    units_generated = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='productions')


class EnergyPriceHistory(db.Model):
    __tablename__ = 'energy_price_history'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, default=datetime.date.today)
    avg_demand = db.Column(db.Double, default=0.0)
    avg_supply = db.Column(db.Double, default=0.0)
    weather_score = db.Column(db.Double, default=0.0) # 0 to 1
    price_per_kwh = db.Column(db.Double, nullable=False)

class CarbonLog(db.Model):
    __tablename__ = 'carbon_logs'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    transaction_id = db.Column(db.String(36), db.ForeignKey("transactions.id"), nullable=False)
    kwh = db.Column(db.Double, nullable=False)
    co2_saved = db.Column(db.Double, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class UserRewards(db.Model):
    __tablename__ = 'user_rewards'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)
    badges = db.Column(db.JSON, default=list) # List of badge names
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', backref=db.backref('rewards', uselist=False))

