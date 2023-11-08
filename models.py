from datetime import datetime
from app import db
from sqlalchemy.orm import relationship

class Charity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Other fields you have defined
    password = db.Column(db.String(60), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

    # Define the is_active method
    def is_active(self):
        return True 
    # Define the get_id method to return the user's ID
    def get_id(self):
        return str(self.id)
    
    # Define the is_authenticated attribute to indicate if the user is authenticated
    @property
    def is_authenticated(self):
        return True  
    
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ... other fields ...
    donations_received = relationship('Donation', backref='donor', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat()
        }
    
    # Define the is_active method
    def is_active(self):
        return True 
    
    # Define the get_id method to return the user's ID
    def get_id(self):
        return str(self.id)
    
    # Define the is_authenticated attribute to indicate if the user is authenticated
    @property
    def is_authenticated(self):
        return True  # Return True for authenticated users
    
class Administrator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username
        }

class Beneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charity.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    story = db.Column(db.Text, nullable=False)
    inventory_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'charity_id': self.charity_id,
            'name': self.name,
            'age': self.age,
            'location': self.location,
            'story': self.story,
            'inventory_sent': self.inventory_sent,
            'created_at': self.created_at.isoformat()
        }

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charity.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_one_time_donation = db.Column(db.Boolean, default=True)
    def serialize(self):
        return {
            'id': self.id,
            'donor_id': self.donor_id,
            'charity_id': self.charity_id,
            'amount': self.amount,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat()
        }


class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    charity_id = db.Column(db.Integer, db.ForeignKey('charity.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiary.id'), nullable=False)  # Add beneficiary_id

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date_posted': self.date_posted.strftime("%Y-%m-%d %H:%M:%S"),
            'charity_id': self.charity_id,
            'created_at': self.created_at
        }