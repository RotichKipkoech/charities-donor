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

# Donor DTO (Data Transfer Object)
donor_model = api.model('Donor', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

# Charity DTO
charity_model = api.model('Charity', {
    'name': fields.String(required=True, description='Charity name'),
    'description': fields.String(required=True, description='Description'),
    'password': fields.String(required=True, description='Password')
})

# Administrator DTO
admin_model = api.model('Administrator', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

@login_manager.user_loader
def load_user(user_id):
    return Donor.query.get(int(user_id))

# Donor Routes
@donors_ns.route('/donors')
class DonorList(Resource):
    @donors_ns.doc('get_donors')
    def get(self):
        """Get all donors"""
        donors = Donor.query.all()
        return jsonify([donor.serialize() for donor in donors])

@donors_ns.route('/donors/<int:donor_id>')
class DonorResource(Resource):
    @donors_ns.doc('get_donor')
    def get(self, donor_id):
        """Get a donor by ID"""
        donor = Donor.query.get_or_404(donor_id)
        return jsonify(donor.serialize())

@donors_ns.route('donors/register')
class DonorRegister(Resource):
    @donors_ns.doc('register_donor')
    @donors_ns.expect(donor_model)
    def post(self):
        """Register a donor"""
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        donor = Donor(first_name=data['first_name'], last_name=data['last_name'], email=data['email'], password=hashed_password)
        db.session.add(donor)
        db.session.commit()
        return {'message': 'Donor registered successfully!'}

@donors_ns.route('/donors/login')
class DonorLogin(Resource):
    @donors_ns.doc('login_donor')
    @donors_ns.expect(donor_model)
    def post(self):
        """Login as a donor"""
        data = request.get_json()
        donor = Donor.query.filter_by(email=data['email']).first()
        if donor and bcrypt.check_password_hash(donor.password, data['password']):
            login_user(donor)
            return {'message': 'Login successful!'}
        else:
            return {'error': 'Invalid email or password'}, 401

@donors_ns.route('/donors/logout')
class DonorLogout(Resource):
    @donors_ns.doc('logout_donor')
    @login_required
    def get(self):
        """Logout as a donor"""
        logout_user()
        return {'message': 'Logout successful!'}


# Charity Routes
# Charity Routes
@charities_ns.route('/')
class CharityList(Resource):
    @charities_ns.doc('get_charities')
    def get(self):
        """Get all charities"""
        charities = Charity.query.all()
        return jsonify([charity.serialize() for charity in charities])

@charities_ns.route('/<int:charity_id>')
class CharityResource(Resource):
    @charities_ns.doc('get_charity')
    def get(self, charity_id):
        """Get a charity by ID"""
        charity = Charity.query.get_or_404(charity_id)
        return jsonify(charity.serialize())

@charities_ns.route('/register')
class CharityRegister(Resource):
    @charities_ns.doc('register_charity')
    @charities_ns.expect(charity_model)
    def post(self):
        """Register a charity"""
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        charity = Charity(name=data['name'], description=data['description'], password=hashed_password, status='Pending')
        db.session.add(charity)
        db.session.commit()
        return {'message': 'Charity registration submitted for review!'}

@charities_ns.route('/login')
class CharityLogin(Resource):
    @charities_ns.doc('login_charity')
    @charities_ns.expect(charity_model)
    def post(self):
        """Login as a charity"""
        data = request.get_json()
        charity = Charity.query.filter_by(name=data['name']).first()
        if charity and bcrypt.check_password_hash(charity.password, data['password']):
            login_user(charity)
            return {'message': 'Login successful!'}
        else:
            return {'error': 'Invalid name or password'}, 401

@charities_ns.route('/apply')
class CharityApply(Resource):
    @charities_ns.doc('apply_charity')
    @charities_ns.expect(charity_model)
    def post(self):
        """Apply for charity status"""
        data = request.get_json()
        charity = Charity(name=data['name'], description=data['description'], status='Pending')
        db.session.add(charity)
        db.session.commit()
        return {'message': 'Charity application submitted for review!'}

@charities_ns.route('/setup/<int:charity_id>')
class CharitySetup(Resource):
    @charities_ns.doc('setup_charity')
    @charities_ns.expect(charity_model)
    @login_required
    def post(self, charity_id):
        """Set up charity details"""
        charity = Charity.query.get_or_404(charity_id)
        data = request.get_json()
        # Implement logic to set up charity details here.
        return {'message': 'Charity details set up successfully!'}

@charities_ns.route('/non_anonymous_donors')
class CharityNonAnonymousDonors(Resource):
    @charities_ns.doc('get_non_anonymous_donors')
    @login_required
    def get(self):
        """Get non-anonymous donors associated with the charity"""
        non_anonymous_donors = Donor.query.filter_by(is_anonymous=False).all()
        return jsonify([donor.serialize() for donor in non_anonymous_donors])

@charities_ns.route('/anonymous_donations')
class CharityAnonymousDonations(Resource):
    @charities_ns.doc('get_anonymous_donations')
    @login_required
    def get(self):
        """Get anonymous donations associated with the charity"""
        anonymous_donations = Donation.query.filter_by(is_anonymous=True).all()
        return jsonify([donation.serialize() for donation in anonymous_donations])

@charities_ns.route('/total_donations')
class CharityTotalDonations(Resource):
    @charities_ns.doc('get_total_donations')
    @login_required
    def get(self):
        """Get the total donations received by the charity"""
        total_donations = sum(donation.amount for donation in current_user.donations_received)
        return {'total_donations': total_donations}

@charities_ns.route('/post_story')
class CharityPostStory(Resource):
    @charities_ns.doc('post_beneficiary_story')
    @charities_ns.expect(charity_model)
    @login_required
    def post(self):
        """Post a beneficiary story"""
        data = request.get_json()
        story = Story(beneficiary_id=data['beneficiary_id'], content=data['content'])
        db.session.add(story)
        db.session.commit()
        return {'message': 'Story posted successfully!'}

@charities_ns.route('/beneficiaries')
class CharityBeneficiaries(Resource):
    @charities_ns.doc('get_beneficiaries')
    @login_required
    def get(self):
        """Get all beneficiaries associated with the charity"""
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
