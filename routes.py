from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt, login_manager
from models import Charity, Donor, Administrator, Donation, Beneficiary, Story
from flask_restx import Api, Resource, fields


api = Api(app, version='1.0', title='Charity API', description='API for managing charities, donors, and administrators')


 #Define namespaces
donors_ns = api.namespace('donors', description='Donor operations')
charities_ns = api.namespace('charities', description='Charity operations')
admins_ns = api.namespace('administrators', description='Administrator operations')

@login_manager.user_loader
def load_user(user_id):
    return Donor.query.get(int(user_id))

# Donor Routes

@app.route('/api/donors', methods=['GET'])
def get_donors():
    donors = Donor.query.all()
    return jsonify([donor.serialize() for donor in donors])

@app.route('/api/donors/<int:donor_id>', methods=['GET'])
def get_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    return jsonify(donor.serialize())

@app.route('/api/donors/register', methods=['POST'])
def register_donor():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    donor = Donor(first_name=data['first_name'], last_name=data['last_name'], email=data['email'], password=hashed_password)
    db.session.add(donor)
    db.session.commit()
    return jsonify({'message': 'Donor registered successfully!'})

@app.route('/api/donors/login', methods=['POST'])
def login_donor():
    data = request.get_json()
    donor = Donor.query.filter_by(email=data['email']).first()
    if donor and bcrypt.check_password_hash(donor.password, data['password']):
        login_user(donor)
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/donors/logout', methods=['GET'])
@login_required
def logout_donor():
    logout_user()
    return jsonify({'message': 'Logout successful!'})

# Charity Routes

@app.route('/api/charities', methods=['GET'])
def get_charities():
    charities = Charity.query.all()
    return jsonify([charity.serialize() for charity in charities])

@app.route('/api/charities/<int:charity_id>', methods=['GET'])
def get_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    return jsonify(charity.serialize())

@app.route('/api/charities/register', methods=['POST'])
def register_charity():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    charity = Charity(name=data['name'], description=data['description'], password=hashed_password, status='Pending')
    db.session.add(charity)
    db.session.commit()
    return jsonify({'message': 'Charity registration submitted for review.'})

@app.route('/api/charities/login', methods=['POST'])
def login_charities():
    data = request.get_json()
    charities = Charity.query.filter_by(email=data['email']).first()
    if charities and bcrypt.check_password_hash(charities.password, data['password']):
        login_user(charities)
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401
@app.route('/api/charities/apply', methods=['POST'])
def apply_charity():
    data = request.get_json()
    charity = Charity(name=data['name'], description=data['description'], status='Pending')
    db.session.add(charity)
    db.session.commit()
    return jsonify({'message': 'Charity application submitted for review.'})

@app.route('/api/charities/setup/<int:charity_id>', methods=['POST'])
@login_required
def setup_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    data = request.get_json()
    # Implement logic to set up charity details here.
    return jsonify({'message': 'Charity details set up successfully!'})

@app.route('/api/charities/non_anonymous_donors', methods=['GET'])
@login_required
def get_non_anonymous_donors():
    non_anonymous_donors = Donor.query.filter_by(is_anonymous=False).all()
    return jsonify([donor.serialize() for donor in non_anonymous_donors])

@app.route('/api/charities/anonymous_donations', methods=['GET'])
@login_required
def get_anonymous_donations():
    anonymous_donations = Donation.query.filter_by(is_anonymous=True).all()
    return jsonify([donation.serialize() for donation in anonymous_donations])

@app.route('/api/charities/total_donations', methods=['GET'])
@login_required
def get_total_donations():
    total_donations = sum(donation.amount for donation in current_user.donations_received)
    return jsonify({'total_donations': total_donations})

@app.route('/api/charities/post_story', methods=['POST'])
@login_required
def post_beneficiary_story():
    data = request.get_json()
    story = Story(beneficiary_id=data['beneficiary_id'], content=data['content'])
    db.session.add(story)
    db.session.commit()
    return jsonify({'message': 'Story posted successfully!'})

@app.route('/api/charities/beneficiaries', methods=['GET'])
@login_required
def get_beneficiaries():
    beneficiaries = Beneficiary.query.all()
    return jsonify([beneficiary.serialize() for beneficiary in beneficiaries])

# Administrator Routes

@app.route('/api/administrators', methods=['GET'])
def get_administrators():
    administrators = Administrator.query.all()
    return jsonify([administrator.serialize() for administrator in administrators])

@app.route('/api/administrators/<int:administrator_id>', methods=['GET'])
def get_administrator(administrator_id):
    administrator = Administrator.query.get_or_404(administrator_id)
    return jsonify(administrator.serialize())

@app.route('/api/administrators/register', methods=['POST'])
def register_administrator():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    administrator = Administrator(username=data['username'], password=hashed_password)
    db.session.add(administrator)
    db.session.commit()
    return jsonify({'message': 'Administrator registered successfully!'})

@app.route('/api/administrators/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    admin = Administrator.query.filter_by(email=data['email']).first()
    if admin and bcrypt.check_password_hash(admin.password, data['password']):
        login_user(admin)
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

# Add route for admin to view pending charities
@app.route('/api/admin/pending_charities', methods=['GET'])
def view_pending_charities():
    pending_charities = Charity.query.filter_by(status='Pending').all()
    return jsonify([charity.serialize() for charity in pending_charities])

# Add route for admin to approve a pending charity
@app.route('/api/admin/approve_charity/<int:charity_id>', methods=['POST'])
def approve_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    charity.status = 'Approved'
    db.session.commit()
    return jsonify({'message': 'Charity approved!'})

# Add route for admin to reject a pending charity
@app.route('/api/admin/reject_charity/<int:charity_id>', methods=['POST'])
def reject_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    db.session.delete(charity)
    db.session.commit()
    return jsonify({'message': 'Charity rejected!'})

# Add route for admin to view all charities
@app.route('/api/admin/all_charities', methods=['GET'])
def view_all_charities():
    all_charities = Charity.query.all()
    return jsonify([charity.serialize() for charity in all_charities])

# Add route for admin to delete a charity
@app.route('/api/admin/delete_charity/<int:charity_id>', methods=['POST'])
def delete_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    db.session.delete(charity)
    db.session.commit()
    return jsonify({'message': 'Charity deleted!'})

if __name__ == '__main__':
    app.run(debug=True)
