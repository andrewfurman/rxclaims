# The users database table will store information from the users after each user has logged in using Auth0 for authentication.

# Can you create the users table so that it stores all data attributues that are able to be captured from Auth0.  All attributiues should be optional (nullable) unless absolutely required.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import TEXT, JSONB

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Auth0 Essential Fields
    auth0_id = db.Column(TEXT, unique=True, nullable=False)  # sub claim from Auth0
    email = db.Column(TEXT, unique=True, nullable=True)
    
    # Profile Information
    first_name = db.Column(TEXT, nullable=True)
    last_name = db.Column(TEXT, nullable=True)
    nickname = db.Column(TEXT, nullable=True)
    picture = db.Column(TEXT, nullable=True)  # URL to profile picture
    
    # Additional Auth0 Fields
    email_verified = db.Column(db.Boolean, nullable=True)
    locale = db.Column(TEXT, nullable=True)
    given_name = db.Column(TEXT, nullable=True)
    family_name = db.Column(TEXT, nullable=True)
    name = db.Column(TEXT, nullable=True)
    
    # Custom Claims and Extra Data
    custom_claims = db.Column(JSONB, nullable=True)
    
    # Access Information
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    login_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.id}: {self.email}>'