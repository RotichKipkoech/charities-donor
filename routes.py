from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt, login_manager
from models import Charity, Donor, Administrator, Donation, Beneficiary, Story
from flask_restx import Api, Resource, fields

api = Api(app, version='1.0', title='Charity API', description='API for managing charities, donors, and administrators')

 #Define namespaces
donors_ns = api.namespace('donors', description='Donor operations')
charities_ns = api.namespace('charities', description='Charity operations')
administrators_ns = api.namespace('administrators', description='Administrator operations')

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
administrator_model = administrators_ns.model('Administrator', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
})

@login_manager.user_loader
def load_user(user_id):
    return Donor.query.get(int(user_id))

# Donor Routes
@donors_ns.route('/')
class DonorList(Resource):
    @donors_ns.doc('get_donors')
    def get(self):
        """Get all donors"""
        donors = Donor.query.all()
        return jsonify([donor.serialize() for donor in donors])

@donors_ns.route('/<int:donor_id>')
class DonorResource(Resource):
    @donors_ns.doc('get_donor')
    def get(self, donor_id):
        """Get a donor by ID"""
        donor = Donor.query.get_or_404(donor_id)
        return jsonify(donor.serialize())

@donors_ns.route('/register')
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

@donors_ns.route('/login')
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

@donors_ns.route('/logout')
class DonorLogout(Resource):
    @donors_ns.doc('logout_donor')
    @login_required
    def get(self):
        """Logout as a donor"""
        logout_user()
        return {'message': 'Logout successful!'}


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
@administrators_ns.route('/')
class AdministratorList(Resource):
    @administrators_ns.doc('get_administrators')
    def get(self):
        """Get all administrators"""
        administrators = Administrator.query.all()
        return jsonify([administrator.serialize() for administrator in administrators])

@administrators_ns.route('/<int:administrator_id>')
class AdministratorResource(Resource):
    @administrators_ns.doc('get_administrator')
    def get(self, administrator_id):
        """Get an administrator by ID"""
        administrator = Administrator.query.get_or_404(administrator_id)
        return jsonify(administrator.serialize())

@administrators_ns.route('/register')
class AdministratorRegister(Resource):
    @administrators_ns.doc('register_administrator')
    @administrators_ns.expect(administrator_model)
    def post(self):
        """Register an administrator"""
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        administrator = Administrator(username=data['username'], password=hashed_password)
        db.session.add(administrator)
        db.session.commit()
        return {'message': 'Administrator registered successfully!'}

@administrators_ns.route('/login')
class AdministratorLogin(Resource):
    @administrators_ns.doc('login_admin')
    @administrators_ns.expect(administrator_model)
    def post(self):
        """Login as an administrator"""
        data = request.get_json()
        admin = Administrator.query.filter_by(username=data['username']).first()
        if admin and bcrypt.check_password_hash(admin.password, data['password']):
            login_user(admin)
            return {'message': 'Login successful!'}
        else:
            return {'error': 'Invalid username or password'}, 401

@administrators_ns.route('/pending_charities')
class AdministratorPendingCharities(Resource):
    @administrators_ns.doc('view_pending_charities')
    def get(self):
        """View pending charities"""
        pending_charities = Charity.query.filter_by(status='Pending').all()
        return jsonify([charity.serialize() for charity in pending_charities])

@administrators_ns.route('/approve_charity/<int:charity_id>')
class AdministratorApproveCharity(Resource):
    @administrators_ns.doc('approve_charity')
    def post(self, charity_id):
        """Approve a pending charity"""
        charity = Charity.query.get_or_404(charity_id)
        charity.status = 'Approved'
        db.session.commit()
        return {'message': 'Charity approved!'}

@administrators_ns.route('/reject_charity/<int:charity_id>')
class AdministratorRejectCharity(Resource):
    @administrators_ns.doc('reject_charity')
    def post(self, charity_id):
        """Reject a pending charity"""
        charity = Charity.query.get_or_404(charity_id)
        db.session.delete(charity)
        db.session.commit()
        return {'message': 'Charity rejected!'}

@administrators_ns.route('/all_charities')
class AdministratorAllCharities(Resource):
    @administrators_ns.doc('view_all_charities')
    def get(self):
        """View all charities"""
        all_charities = Charity.query.all()
        return jsonify([charity.serialize() for charity in all_charities])

@administrators_ns.route('/delete_charity/<int:charity_id>')
class AdministratorDeleteCharity(Resource):
    @administrators_ns.doc('delete_charity')
    def post(self, charity_id):
        """Delete a charity"""
        charity = Charity.query.get_or_404(charity_id)
        db.session.delete(charity)
        db.session.commit()
        return {'message': 'Charity deleted!'}

if __name__ == '__main__':
    app.run(debug=True)
