from datetime import datetime
from faker import Faker
from app import db  # Import your SQLAlchemy database instance
from models import Charity, Donor, Administrator, Beneficiary, Donation, Story

fake = Faker()

# Create a function to generate fake data for Charity model
def create_fake_charity():
    charity = Charity(
        name=fake.company(),
        email=fake.email(),
        description=fake.text(),
        password=fake.password(),
    )
    return charity

# Create a function to generate fake data for Donor model
def create_fake_donor():
    donor = Donor(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        password=fake.password(),
        is_anonymous=fake.boolean(chance_of_getting_true=50),
    )
    return donor

# Create a function to generate fake data for Administrator model
def create_fake_administrator():
    administrator = Administrator(
        username=fake.user_name(),
        password=fake.password(),
    )
    return administrator

# Create a function to generate fake data for Beneficiary model
def create_fake_beneficiary(charity_id):
    beneficiary = Beneficiary(
        charity_id=charity_id,
        name=fake.name(),
        age=fake.random_int(min=1, max=100),
        location=fake.address(),
        story=fake.paragraph(),
        inventory_sent=fake.boolean(chance_of_getting_true=50),
    )
    return beneficiary

# Create a function to generate fake data for Donation model
def create_fake_donation(donor_id, charity_id):
    donation = Donation(
        donor_id=donor_id,
        charity_id=charity_id,
        amount=fake.random_float(min=10, max=500, precision=2),
        is_anonymous=fake.boolean(chance_of_getting_true=30),
    )
    return donation

# Create a function to generate fake data for Story model
def create_fake_story(charity_id, beneficiary_id):
    story = Story(
        title=fake.sentence(),
        content=fake.paragraph(),
        date_posted=fake.date_time_this_decade(before_now=True, after_now=False),
        charity_id=charity_id,
        beneficiary_id=beneficiary_id,
    )
    return story

# Generate and add fake data to the database
def generate_fake_data():
    # Replace these values with the appropriate charity_id and donor_id
    charity_id = 1
    donor_id = 1

    for _ in range(10):
        charity = create_fake_charity()
        db.session.add(charity)

    for _ in range(20):
        donor = create_fake_donor()
        db.session.add(donor)

    for _ in range(5):
        administrator = create_fake_administrator()
        db.session.add(administrator)

    db.session.commit()

    for _ in range(30):
        beneficiary = create_fake_beneficiary(charity_id)
        db.session.add(beneficiary)

    for _ in range(50):
        donation = create_fake_donation(donor_id, charity_id)
        db.session.add(donation)

    db.session.commit()

    for _ in range(15):
        beneficiary_id = fake.random_int(min=1, max=30)  # Adjust the max value based on the number of beneficiaries
        story = create_fake_story(charity_id, beneficiary_id)
        db.session.add(story)

    db.session.commit()

if __name__ == '__main__':
    generate_fake_data()
