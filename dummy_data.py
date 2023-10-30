from app import app, db
from models import Charity, Donor, Administrator, Beneficiary, Donation, Story
from datetime import datetime

# Create an application context
with app.app_context():

    # Create dummy data for Charities
    charity1 = Charity(name="Charity A", description="Description for Charity A", status="Approved")
    charity2 = Charity(name="Charity B", description="Description for Charity B", status="Pending")

    # Create dummy data for Donors
    donor1 = Donor(first_name="John", last_name="Doe", email="john@example.com", password="hashed_password_here")
    donor2 = Donor(first_name="Jane", last_name="Doe", email="jane@example.com", password="hashed_password_here")

    # Create dummy data for Administrators
    admin1 = Administrator(username="admin1", password="hashed_password_here")
    admin2 = Administrator(username="admin2", password="hashed_password_here")

    # Create dummy data for Beneficiaries
    beneficiary1 = Beneficiary(charity_id=1, name="Beneficiary 1", age=10, location="Location 1", story="Story for Beneficiary 1", inventory_sent=True)
    beneficiary2 = Beneficiary(charity_id=1, name="Beneficiary 2", age=12, location="Location 2", story="Story for Beneficiary 2", inventory_sent=False)

    # Create dummy data for Donations
    donation1 = Donation(donor_id=1, charity_id=1, amount=50.00, is_anonymous=False, created_at=datetime.utcnow())
    donation2 = Donation(donor_id=2, charity_id=2, amount=100.00, is_anonymous=True, created_at=datetime.utcnow())

    # Create dummy data for Stories
    story1 = Story(charity_id=1, title="Story Title 1", content="Story content for Charity A", created_at=datetime.utcnow())
    story2 = Story(charity_id=2, title="Story Title 2", content="Story content for Charity B", created_at=datetime.utcnow())

    # Add the dummy data to the session and commit it to the database
    db.session.add(charity1)
    db.session.add(charity2)
    db.session.add(donor1)
    db.session.add(donor2)
    db.session.add(admin1)
    db.session.add(admin2)
    db.session.add(beneficiary1)
    db.session.add(beneficiary2)
    db.session.add(donation1)
    db.session.add(donation2)
    db.session.add(story1)
    db.session.add(story2)
    db.session.commit()

    # Print a message to indicate that the data has been added
    print("Dummy data added successfully.")
