import logging
from flask import request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt, login_manager, api
from models import Charity, Donor, Administrator, Donation, Beneficiary, Story
from flask_restx import Resource, fields, Namespace, reqparse, inputs
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from email_utils import send_approval_email, send_rejection_email, send_thank_you_email
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from mpesa_integration import initiate_stk_push
from sqlalchemy import func


# Configure logging
logging.basicConfig(level=logging.DEBUG)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Donor, int(user_id))


# Define pagination parser
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, help='Page number', default=1)
pagination_parser.add_argument('per_page', type=int, help='Items per page', default=10)

# Create a namespace for donors
donors_ns = Namespace('donors', description='Donors operations')

# Define a model for donor serialization
donor_model = donors_ns.model('Donor', {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
})

# Donor Routes

@donors_ns.route('/')
class DonorsList(Resource):
    @donors_ns.doc(params={
        'page': 'Page number for pagination',
        'per_page': 'Number of donors per page'
    })
    @donors_ns.marshal_list_with(donor_model)
    @donors_ns.expect(pagination_parser)
    def get(self):
        """
        Get a list of donors with pagination
        """
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        # Calculate offset and limit for pagination
        offset = (page - 1) * per_page
        limit = per_page

        donors = Donor.query.offset(offset).limit(limit).all()
        return donors, 200
    
# Create a request parser for donor registration
donor_registration_parser  = reqparse.RequestParser()
donor_registration_parser .add_argument('first_name', type=str, required=True, help='First name of the donor')
donor_registration_parser .add_argument('last_name', type=str, required=True, help='Last name of the donor')
donor_registration_parser.add_argument('email', type=str, required=True, help='Email of the donor')
donor_registration_parser.add_argument('password', type=str, required=True, help='Password of the donor')

@donors_ns.route('/register')
class DonorRegistration(Resource):
    @donors_ns.expect(donor_registration_parser)
    @donors_ns.doc(responses={201: 'Donor registered successfully!'})
    def post(self):
        logging.debug("Donor registration route called")
        data = donor_registration_parser.parse_args()
        logging.debug(f"Data parsed: {data}")
        
        # Attempt to create a new donor
        try:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            donor = Donor(first_name=data['first_name'], last_name=data['last_name'], email=data['email'], password=hashed_password)
            db.session.add(donor)
            db.session.commit()
            logging.debug("Donor added to the database")
            response = {'message': 'Donor registered successfully!'}
            return response, 201  # Return a JSON-serializable dictionary
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"IntegrityError: {str(e)}")
            response = {'message': 'Email address already exists'}
            return response, 400  # Return a JSON-serializable dictionary

@donors_ns.route('/<int:donor_id>')
class DonorResource(Resource):
    @donors_ns.doc(responses={200: 'Donor found', 404: 'Donor not found'})
    @donors_ns.marshal_with(donor_model)
    def get(self, donor_id):
        """
        Get a specific donor by ID
        """
        donor = Donor.query.get_or_404(donor_id)
        return donor, 200

donation_model = donors_ns.model('Donation', {
    'id': fields.Integer,
    'donor_id': fields.Integer,
    'charity_id': fields.Integer,
    'amount': fields.Float,
    'is_anonymous': fields.Boolean,
    'created_at': fields.String,
})

@donors_ns.route('/<int:donor_id>/donations')
class DonorDonations(Resource):
    @donors_ns.marshal_with(donation_model)
    @donors_ns.doc(params={'donor_id': 'The ID of the donor'})
    def get(self, donor_id):
        donor = Donor.query.get(donor_id)
        if donor is None:
            donors_ns.abort(404, "Donor not found")

        donations = Donation.query.filter_by(donor_id=donor_id).all()
        return donations, 200
    
# Create a namespace for donor login and logout
auth_ns = Namespace('auth', description='Authentication operations')

# Create a request parser for donor login
donor_login_parser = reqparse.RequestParser()
donor_login_parser.add_argument('email', type=str, required=True, help='Email of the donor')
donor_login_parser.add_argument('password', type=str, required=True, help='Password of the donor')

@auth_ns.route('/donors/login')
class DonorLogin(Resource):
    @auth_ns.expect(donor_login_parser)
    @auth_ns.doc(responses={200: 'Login successful!', 401: 'Invalid email or password'})
    def post(self):
        data = donor_login_parser.parse_args()
        donor = Donor.query.filter_by(email=data['email']).first()

        if donor and bcrypt.check_password_hash(donor.password, data['password']):
            # Generate an access token
            access_token = create_access_token(identity=donor.id)

            # Include the access token in the response
            return {'access_token': access_token, 'message': 'Login successful!'}, 200
        else:
            return {'error': 'Invalid email or password'}, 401

@auth_ns.route('/donors/logout')
class DonorLogout(Resource):
    @auth_ns.doc(responses={200: 'Logout successful'})
    @login_required
    def get(self):
        logout_user()
        return {'message': 'Logout successful!'}, 200

story_model = donors_ns.model('Story', {
    'id': fields.Integer(required=True, description='Story ID'),
    'title': fields.String(required=True, description='Story Title'),
    'content': fields.String(required=True, description='Story Content'),
    'date_posted': fields.String(description='Date Posted'),
    'charity_id': fields.Integer(description='Charity ID'),
    'created_at': fields.String(description='Created At Date'),
})

@donors_ns.route('/beneficiary_stories')
class DonorStoriesResource(Resource):
    @donors_ns.doc(security='apikey')  # Define your authentication here
    @donors_ns.marshal_list_with(story_model)
    def get(self):
        """
        Get stories about beneficiaries of your donations
        """
        # Add authentication and authorization logic here if needed
        donor_id = current_user.id  # Replace with your actual authentication logic

        # Query the database to get stories related to the donor's donations
        # You should adapt this query based on your database structure
        stories = Story.query.filter_by(charity_id=donor_id).all()

        return stories, 200
    
api.add_namespace(auth_ns)
api.add_namespace(donors_ns)

# Define a namespace for donations
donations_ns = api.namespace('donations', description='Donation operations')

# Define a model for the response in Swagger
donation_response_model = api.model('DonationResponse', {
    'message': fields.String(description='Response message'),
})

donation_parser = reqparse.RequestParser()
donation_parser.add_argument('donor_id', type=int, required=True, help='Donor ID')
donation_parser.add_argument('amount', type=float, required=True, help='Donation amount')
donation_parser.add_argument('phone_number', type=str, required=True, help='Phone number')
donation_parser.add_argument('is_anonymous', type=bool, required=True, help='Is donation anonymous')
donation_parser.add_argument('charity_id', type=int, required=True, help='Charity ID')
donation_parser.add_argument('is_one_time_donation', type=bool, required=True, help='Is it a one-time donation')

@donations_ns.route('/donate')
class DonationResource(Resource):
    @donations_ns.expect(donation_parser)
    @donations_ns.marshal_with(donation_response_model, code=201)
    @donations_ns.doc(responses={201: 'Donation initiated successfully!', 400: 'Bad request'})
    def post(self):
        data = donation_parser.parse_args()

        donor_id = data['donor_id']
        amount = data['amount']
        phone_number = data['phone_number']
        is_anonymous = data['is_anonymous']
        charity_id = data['charity_id']
        is_one_time_donation = data['is_one_time_donation']  # New parameter

        # Logic with your charity ID determination
        charity_id = request.args.get('charity_id')

        if charity_id is None:
            return {'error': 'Invalid charity ID'}, 400

        donor = Donor.query.get(donor_id)

        if donor:
            response = initiate_stk_push(phone_number, amount)

            if response.get('ResponseCode') == "0":
                new_donation = Donation(
                    donor_id=donor_id,
                    charity_id=charity_id,
                    amount=amount,
                    is_anonymous=is_anonymous,
                    is_one_time_donation=is_one_time_donation  # Set the donation type
                )
                db.session.add(new_donation)
                db.session.commit()
                return {'message': 'Donation initiated successfully!'}, 201
            else:
                # Handle the case where the STK push failed
                return {'error': 'STK push payment failed. Donation not recorded.'}, 400

        return {'error': 'Donor not found'}, 400


# Add the donations namespace to the API
api.add_namespace(donations_ns)

# Create a namespace for charities
charities_ns = Namespace('charities', description='Charities operations')

# Define a model for charity serialization
charity_model = charities_ns.model('Charity', {
    'id': fields.Integer,
    'name': fields.String(description='Name of the charity', required=True),
    'description': fields.String(description='Description of the charity', required=True),
    'status': fields.String(description='Status of the charity', required=False),
    'created_at': fields.String(description='Date and time of creation', required=False),
})

# Create a request parser for charity registration
charity_registration_parser = reqparse.RequestParser()
charity_registration_parser.add_argument('name', type=str, required=True, help='Name of the charity')
charity_registration_parser.add_argument('email', type=str, required=True, help='Email of the charity')
charity_registration_parser.add_argument('description', type=str, required=True, help='Description of the charity')
charity_registration_parser.add_argument('password', type=str, required=True, help='Password for the charity')
charity_registration_parser.add_argument('status', type=str, default='Pending', help='Status of the charity')

@charities_ns.route('/register')
class CharityRegistration(Resource):
    @charities_ns.doc(responses={201: 'Charity registration submitted for review.'})
    @charities_ns.expect(charity_registration_parser)
    @charities_ns.marshal_with(charity_model, code=201)
    def post(self):
        logging.debug("Charity registration route called")
        data = charity_registration_parser.parse_args()
        logging.debug(f"Data parsed: {data}")

        try:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            charity = Charity(name=data['name'], email=data['email'], description=data['description'], password=hashed_password, status=data['status'])
            db.session.add(charity)
            db.session.commit()
            logging.debug("Charity added to the database")
            response = {'message': 'Charity registered successfully!'}
            return response, 201
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"IntegrityError: {str(e)}")

            # Sending a thank you email
            send_thank_you_email(charity)

            response = {'message': 'Email address already exists'}
            return response, 400  # Return a JSON-serializable dictionary
        
# Define a pagination parser for charities
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, help='Page number for pagination', default=1)
pagination_parser.add_argument('per_page', type=int, help='Items per page', default=10)

@charities_ns.route('/')
class CharitiesList(Resource):
    @charities_ns.doc(params={
        'page': 'Page number for pagination',
        'per_page': 'Number of charities per page'
    })
    @charities_ns.marshal_list_with(charity_model)
    @charities_ns.expect(pagination_parser)
    def get(self):
        """
        Get a list of charities with pagination
        """
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        # Calculate offset and limit for pagination
        offset = (page - 1) * per_page
        limit = per_page

        charities = Charity.query.offset(offset).limit(limit).all()
        return charities, 200
    
@charities_ns.route('/<int:charity_id>')
class CharityResource(Resource):
    @charities_ns.doc(params={'charity_id': 'ID of the charity'})
    @charities_ns.marshal_with(charity_model)
    def get(self, charity_id):
        """
        Get a specific charity by ID
        """
        charity = Charity.query.get_or_404(charity_id)
        return charity, 200
    
# Define a model for the login response
login_response_model = charities_ns.model('LoginResponse', {
    'message': fields.String(description='Login response message'),
})

# Create a request parser for login
charity_login_parser = reqparse.RequestParser()
charity_login_parser.add_argument('email', type=str, required=True, help='Email of the charity')
charity_login_parser.add_argument('password', type=str, required=True, help='Password of the charity')

@charities_ns.route('/login')
class CharityLogin(Resource):
    @charities_ns.expect(charity_login_parser)
    @charities_ns.marshal_with(login_response_model)
    @charities_ns.doc(responses={200: 'Login successful!', 401: 'Invalid email or password', 403: 'Pending status'})
    def post(self):
        data = charity_login_parser.parse_args()
        charity = Charity.query.filter_by(email=data['email']).first()

        if charity:
            if charity.status == 'Pending':
                return {'error': 'Charity status is pending. Cannot log in yet.'}, 403
            elif bcrypt.check_password_hash(charity.password, data['password']):
                # Use create_access_token to generate a JWT token
                access_token = create_access_token(identity=charity.id)
                return {'access_token': access_token, 'message': 'Login successful!'}, 200

        return {'error': 'Invalid email or password'}, 401

# Define a route to verify the JWT token
@charities_ns.route('/verify')
class CharityVerify(Resource):
    @jwt_required()
    @charities_ns.doc(responses={200: 'Token is valid', 401: 'Token is invalid'})
    def get(self):
        current_charity_id = get_jwt_identity()
        return {'message': 'Token is valid', 'charity_id': current_charity_id}

setup_ns = Namespace('setup', description='Charity setup operations')

charity_setup_response_model = setup_ns.model('CharitySetupResponse', {
    'message': fields.String(description='Message indicating the success of charity setup'),
})

# Define a request parser for charity setup
setup_parser = reqparse.RequestParser()
setup_parser.add_argument('details', type=str, required=True, help='Details for charity setup')

@setup_ns.route('/<int:charity_id>')
class CharitySetup(Resource):
    @setup_ns.expect(setup_parser)
    @setup_ns.marshal_with(charity_setup_response_model)
    @setup_ns.doc(responses={200: 'Charity details set up successfully!', 401: 'Unauthorized'})
    @login_required
    def post(self, charity_id):
        charity = Charity.query.get_or_404(charity_id)
        data = setup_parser.parse_args()

        # Implement logic to set up charity details
        charity.details = data['details']
        db.session.commit()

        return {'message': 'Charity details set up successfully!'}, 200
    
# Create a request parser for pagination
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, help='Page number', default=1)
pagination_parser.add_argument('per_page', type=int, help='Items per page', default=10)

@charities_ns.route('/non_anonymous_donors')
class NonAnonymousDonors(Resource):
    @charities_ns.doc(params={
        'page': 'Page number for pagination',
        'per_page': 'Number of non-anonymous donors per page'
    })
    @charities_ns.marshal_list_with(donor_model)
    @charities_ns.expect(pagination_parser)
    @login_required
    def get(self):
        """
        Get a list of non-anonymous donors with pagination
        """
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        # Calculate offset and limit for pagination
        offset = (page - 1) * per_page
        limit = per_page

        non_anonymous_donors = Donor.query.filter_by(is_anonymous=False).offset(offset).limit(limit).all()
        return non_anonymous_donors, 200
    
# Define a model for donation serialization
donation_model = charities_ns.model('Donation', {
    'id': fields.Integer,
    'amount': fields.Float,
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'is_anonymous': fields.Boolean,
    'donor_id': fields.Integer,
    'beneficiary_id': fields.Integer,
})

#Create a request parser for pagination
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, help='Page number', default=1)
pagination_parser.add_argument('per_page', type=int, help='Items per page', default=10)

donation_model = charities_ns.model('Donation', {
    'id': fields.Integer,
    'donor_id': fields.Integer,
    'charity_id': fields.Integer,
    'amount': fields.Float,
    'is_anonymous': fields.Boolean,
    'created_at': fields.String,
})

@charities_ns.route('/<int:charity_id>/donations')
class CharityDonations(Resource):
    @charities_ns.marshal_with(donation_model, as_list=True)
    @charities_ns.doc(params={'charity_id': 'The ID of the charity'})
    def get(self, charity_id):
        charity = Charity.query.get(charity_id)
        if charity is None:
            charities_ns.abort(404, "Charity not found")

        donations = Donation.query.filter_by(charity_id=charity_id).all()
        return donations, 200

@charities_ns.route('/anonymous_donations')
class AnonymousDonations(Resource):
    @charities_ns.doc(params={
        'page': 'Page number for pagination',
        'per_page': 'Number of anonymous donations per page'
    })
    @charities_ns.marshal_list_with(donation_model)
    @charities_ns.expect(pagination_parser)
    @login_required
    def get(self):
        """
        Get a list of anonymous donations with pagination
        """
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        # Calculate offset and limit for pagination
        offset = (page - 1) * per_page
        limit = per_page

        anonymous_donations = Donation.query.filter_by(is_anonymous=True).offset(offset).limit(limit).all()
        return anonymous_donations, 200
    
@charities_ns.route('/<int:charity_id>/total_donations')
class CharityTotalDonations(Resource):
    @charities_ns.doc(params={'charity_id': 'The ID of the charity'})
    def get(self, charity_id):
        charity = Charity.query.get(charity_id)
        if charity is None:
            charities_ns.abort(404, "Charity not found")

        total_donations = db.session.query(func.sum(Donation.amount)).filter_by(charity_id=charity_id).scalar()
        if total_donations is None:
            total_donations = 0.0

        return {'total_donations': total_donations}, 200

# Define a model for the input data (if required)
beneficiary_story_model = api.model('BeneficiaryStory', {
    'beneficiary_id': fields.Integer(required=True, description='Beneficiary ID'),
    'content': fields.String(required=True, description='Story content'),
})

# Define a model for beneficiary serialization
beneficiary_model = charities_ns.model('Beneficiary', {
    'id': fields.Integer(description='Beneficiary ID', required=True),
    'name': fields.String(description='Beneficiary name', required=True),
    'age': fields.Integer(description='Age of the beneficiary', required=True),
    'location': fields.String(description='Location of the beneficiary', required=True),
    'story': fields.String(description='Story of the beneficiary', required=True),
    'inventory_sent': fields.Boolean(description='Inventory sent status', required=True),
    'created_at': fields.DateTime(description='Date created', required=True),
    'charity_id': fields.Integer(description='Charity ID', required=True),
})

# Pagination parser for list endpoints
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=inputs.positive, default=1, help='Page number')
pagination_parser.add_argument('per_page', type=inputs.positive, default=10, help='Items per page')

@charities_ns.route('/beneficiaries')
class Beneficiaries(Resource):
    def get(self):
        """
        Get a list of beneficiary names
        """
        beneficiaries = Beneficiary.query.all()
        beneficiary_names = [beneficiary.name for beneficiary in beneficiaries]
        return beneficiary_names

@charities_ns.route('/beneficiaries/add')
class AddBeneficiary(Resource):
    @charities_ns.expect(beneficiary_model)
    def post(self):
        """
        Add a new beneficiary to the charity.
        """
        data = request.json
        charity_id = 1  # Replace with the actual charity ID, e.g., current_user.id

        # Create a new beneficiary
        beneficiary = Beneficiary(
            charity_id=charity_id,
            name=data['name'],
            age=data['age'],
            location=data['location'],
            story=data['story'],
            inventory_sent=data['inventory_sent']
        )

        db.session.add(beneficiary)
        db.session.commit()
        return {'message': 'Beneficiary added successfully'}, 201

# Create the update_story_model
update_story_model = api.model('UpdateStory', {
    'story': fields.String(required=True, description='New story content for the beneficiary'),
})

@charities_ns.route('/update_story/<int:beneficiary_id>', methods=['PUT'])
class UpdateBeneficiaryStoryResource(Resource):
    @charities_ns.doc(params={'beneficiary_id': 'ID of the beneficiary'})
    @charities_ns.doc(responses={200: 'Success', 404: 'Beneficiary not found'})
    @charities_ns.expect(update_story_model)  # Define the model for the request payload
    def put(self, beneficiary_id):
        """
        Update the story of a beneficiary by ID
        """
        # Retrieve the beneficiary from the database
        beneficiary = Beneficiary.query.get_or_404(beneficiary_id)

        # Parse the request data
        data = api.payload  # Assuming 'update_story_model' defines the expected request structure

        # Update the beneficiary's story with the new content
        beneficiary.story = data['story']

        # Commit the changes to the database
        db.session.commit()

        return {'message': 'Beneficiary story updated successfully'}


api.add_namespace(charities_ns)

# Create a namespace for administrators
administrators_ns = Namespace('administrators', description='Administrators operations')

# Define a model for administrator serialization
administrator_model = administrators_ns.model('Administrator', {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    # Add more fields as needed
})

# Define a pagination parser (if required)
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, help='Page number', default=1)
pagination_parser.add_argument('per_page', type=int, help='Items per page', default=10)

@administrators_ns.route('/')
class AdministratorsList(Resource):
    @administrators_ns.doc(params={
        'page': 'Page number for pagination',
        'per_page': 'Number of administrators per page'
    })
    @administrators_ns.marshal_list_with(administrator_model)
    @administrators_ns.expect(pagination_parser)
    def get(self):
        """
        Get a list of administrators with pagination
        """
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        # Calculate offset and limit for pagination
        offset = (page - 1) * per_page
        limit = per_page

        administrators = Administrator.query.offset(offset).limit(limit).all()
        return administrators
    
# Define a model for administrator serialization
administrator_model = administrators_ns.model('Administrator', {
    'id': fields.Integer,
    'username': fields.String,
})


@administrators_ns.route('/<int:administrator_id>')
class AdministratorResource(Resource):
    @administrators_ns.doc(params={'administrator_id': 'ID of the administrator'})
    @administrators_ns.marshal_with(administrator_model)
    def get(self, administrator_id):
        try:
            """
            Get a specific administrator by ID
            """
            administrator = Administrator.query.get_or_404(administrator_id)
            return administrator
        except Exception as e:
            logging.exception("An error occurred while processing the request:")
            return {"error": "An error occurred while processing the request."}, 500
        
# Define a parser for the registration input
admin_registration_parser = reqparse.RequestParser()
admin_registration_parser.add_argument('username', type=str, required=True, help='Username')
admin_registration_parser.add_argument('password', type=str, required=True, help='Password')

# Registration resource
@administrators_ns.route('/register')
class AdminRegistrationResource(Resource):
    @administrators_ns.doc(description='Register a new administrator', responses={200: 'Success', 400: 'Validation Error'})
    @administrators_ns.expect(admin_registration_parser)
    @administrators_ns.marshal_with(administrator_model, code = 201)
    def post(self):
        args = admin_registration_parser.parse_args()
        username = args['username']
        password = args['password']

        # Check if the username is already in use
        if Administrator.query.filter_by(username=username).first():
            return {'message': 'Username already in use'}, 400

        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Create a new administrator
        admin = Administrator(username=username, password=hashed_password)

        # Add and commit to the database
        db.session.add(admin)
        db.session.commit()

        return {'message': 'Administrator registered successfully'}, 200


# Define a parser for the login input
login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True, help='Username')
login_parser.add_argument('password', type=str, required=True, help='Password')

# Model for Swagger documentation
login_model = administrators_ns.model('AdminLogin', {
    'username': fields.String(description='Username', required=True),
    'password': fields.String(description='Password', required=True)
})

# Login resource
@administrators_ns.route('/login')
class AdminLoginResource(Resource):
    @administrators_ns.doc(description='Administrator login', responses={200: 'Success', 400: 'Validation Error', 401: 'Unauthorized'})
    @administrators_ns.expect(login_model, validate=True)
    def post(self):
        args = login_parser.parse_args()
        username = args['username']
        password = args['password']

        # Find the administrator by username
        admin = Administrator.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            # Create a JWT token when login is successful
            access_token = create_access_token(identity=admin.id)

            # Return the JWT token along with the success message
            return {'message': 'Login successful', 'access_token': access_token}, 200
        else:
            return {'message': 'Invalid username or password'}, 401

@administrators_ns.route('/profile')
class AdminProfileResource(Resource):
    @jwt_required()  # Requires a valid JWT token
    def get(self):
        current_admin_id = get_jwt_identity()
        admin = Administrator.query.get(current_admin_id)

        if admin:
            return {'message': 'Admin profile retrieved', 'admin_id': admin.id, 'username': admin.username}, 200
        else:
            return {'message': 'Admin not found'}, 404

# Model for Charity serialization
charity_model = administrators_ns.model('Charity', {
    'id': fields.Integer(description='Charity ID'),
    'name': fields.String(description='Charity Name'),
    'status': fields.String(description='Charity Status')
})

# Admin route for viewing pending charities
@administrators_ns.route('/pending_charities')
class AdminPendingCharitiesResource(Resource):
    @administrators_ns.doc(description='View pending charities', responses={200: 'Success'})
    @administrators_ns.marshal_list_with(charity_model)
    def get(self):
        pending_charities = Charity.query.filter_by(status='Pending').all()
        return pending_charities
    
# Admin route for approving a approving charity
@administrators_ns.route('/approve_charity/<int:charity_id>')
class AdminApproveCharityResource(Resource):
    @administrators_ns.doc(description='Approve a pending charity', responses={200: 'Success'})
    def post(self, charity_id):
        charity = Charity.query.get_or_404(charity_id)
        charity.status = 'Approved'
        db.session.commit()

        # Send an approval email to the charity
        send_approval_email(charity)

        return {'message': 'Charity approved!'}
    
@administrators_ns.route('/reject_charity/<int:charity_id>')
class CharityResource(Resource):
    @administrators_ns.doc(description='Reject a pending charity', responses={200: 'Success'})
    @administrators_ns.marshal_with(charity_model)
    def post(self, charity_id):
        """
        Reject a charity by ID
        """
        
        charity = Charity.query.get_or_404(charity_id)
        charity.status = 'Rejected'
        db.session.commit()

        # Send rejection email to the charity
        send_rejection_email(charity)

        return charity, 200
    
parser = reqparse.RequestParser()
parser.add_argument('page', type=int, help='Page number')
parser.add_argument('per_page', type=int, help='Items per page')

@administrators_ns.route('/charities')
class AllCharitiesResource(Resource):
    @administrators_ns.doc(params={'page': 'Page number', 'per_page': 'Number of Charities per page'})
    @administrators_ns.expect(pagination_parser)
    @administrators_ns.marshal_list_with(charity_model)
    def get(self):
        """
        View all charities with pagination
        """
        
        args = pagination_parser.parse_args()
        page = args['page'] 
        per_page = args['per_page']
        offset = (page - 1) * per_page
        limit = per_page

        charities = Charity.query.offset(offset).limit(limit).all()
        return charities
    
@administrators_ns.route('/delete_charity/<int:charity_id>')
class DeleteCharityResource(Resource):
    @administrators_ns.doc(params={'charity_id': 'ID of the charity'})
    def post(self, charity_id):
        """
        Delete a charity by ID
        """
        charity = Charity.query.get_or_404(charity_id)
        db.session.delete(charity)
        db.session.commit()
        return {'message': 'Charity deleted'}

    
api.add_namespace(administrators_ns)


if __name__ == '__main__':
    app.run(debug=True)