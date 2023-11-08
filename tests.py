import unittest
from flask import Flask
from flask_restx import Api
from app import app, db
from models import Donor, Charity, Administrator
from routes import donors_ns, donations_ns, charities_ns, administrators_ns

class DonorRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.api = Api(app)
        self.api.add_namespace(donors_ns)  # Add the donors namespace to the API for testing
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.populate_sample_data()  # Helper method to populate sample data

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def populate_sample_data(self):
        # Add sample donors to the database
        donor1 = Donor(first_name='John', last_name='Doe', email='johndoe@example.com', password='password')
        donor2 = Donor(first_name='Jane', last_name='Smith', email='janesmith@example.com', password='password')
        db.session.add(donor1)
        db.session.add(donor2)
        db.session.commit()

    def test_get_donors_list(self):
        response = self.client.get('/api/donors/')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertIsInstance(data, list)  # Assuming the response should be a list of donors

class DonationRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.api = Api(app)
        self.api.add_namespace(donations_ns)  # Add the donations namespace to the API for testing
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.populate_sample_data()  # Helper method to populate sample data

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def populate_sample_data(self):
        # Add sample donors to the database
        donor1 = Donor(first_name='John', last_name='Doe', email='johndoe@example.com', password='password')
        db.session.add(donor1)
        db.session.commit()

    def test_donation_resource(self):
        # Define test data for the donation
        test_data = {
            'donor_id': 1,  # Replace with the appropriate donor ID
            'amount': 100.0,  # Replace with the desired donation amount
            'phone_number': '1234567890',  # Replace with a valid phone number
            'is_anonymous': True,  # Set to True or False as needed
            'charity_id': 1,  # Replace with the charity ID
            'is_one_time_donation': True,  # Set to True or False as needed
        }

        # Mock your STK push function to simulate a successful response
        def mock_initiate_stk_push(phone_number, amount):
            return {'ResponseCode': "0"}

        # Replace the original function with the mock
        original_initiate_stk_push = initiate_stk_push
        initiate_stk_push = mock_initiate_stk_push

        response = self.client.post('/api/donations/donate', json=test_data)
        self.assertEqual(response.status_code, 201)  # Assuming 201 is the expected status code
        data = response.get_json()
        self.assertEqual(data['message'], 'Donation initiated successfully!')

        # Restore the original STK push function
        initiate_stk_push = original_initiate_stk_push

class CharityRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.api = Api(app)
        self.api.add_namespace(charities_ns)  # Add the charities namespace to the API for testing
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.populate_sample_data()  # Helper method to populate sample data

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def populate_sample_data(self):
        # Add sample charities to the database
        charity1 = Charity(name='Charity1', email='charity1@example.com', description='Description1', password='password')
        charity2 = Charity(name='Charity2', email='charity2@example.com', description='Description2', password='password')
        db.session.add(charity1)
        db.session.add(charity2)
        db.session.commit()

    def test_charity_registration(self):
        # Define test data for charity registration
        test_data = {
            'name': 'New Charity',
            'email': 'newcharity@example.com',
            'description': 'New Charity Description',
            'password': 'newpassword',
            'status': 'Pending',
        }

        response = self.client.post('/api/charities/register', json=test_data)
        self.assertEqual(response.status_code, 201)  # Assuming 201 is the expected status code
        data = response.get_json()
        self.assertEqual(data['message'], 'Charity registered successfully!')

        # Check if the new charity was added to the database
        new_charity = Charity.query.filter_by(name='New Charity').first()
        self.assertIsNotNone(new_charity)

    def test_charities_list(self):
        response = self.client.get('/api/charities/')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(len(data), 2) 

class AdministratorRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.api = Api(app)
        self.api.add_namespace(administrators_ns)  # Add the administrators namespace to the API for testing
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.populate_sample_data()  # Helper method to populate sample data

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def populate_sample_data(self):
        # Add sample administrators to the database
        admin1 = Administrator(username='admin1', password='password')
        admin2 = Administrator(username='admin2', password='password')
        db.session.add(admin1)
        db.session.add(admin2)

        # Add sample charities to the database
        charity1 = Charity(name='Charity1', status='Pending')
        charity2 = Charity(name='Charity2', status='Pending')
        db.session.add(charity1)
        db.session.add(charity2)
        db.session.commit()

    def test_administrators_list(self):
        response = self.client.get('/api/administrators/')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(len(data), 2)  # Assuming you have two sample administrators in the database

    def test_administrator_profile(self):
        # Assuming you have a JWT token for an administrator in the test environment
        headers = {
            'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE'
        }

        response = self.client.get('/api/administrators/profile', headers=headers)
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(data['message'], 'Admin profile retrieved')  # Check the response message

    def test_pending_charities_list(self):
        response = self.client.get('/api/administrators/pending_charities')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(len(data), 2)  # Assuming you have two sample pending charities in the database

    def test_approve_charity(self):
        # Assuming you have a charity ID to approve
        charity_id_to_approve = 1

        response = self.client.post(f'/api/administrators/approve_charity/{charity_id_to_approve}')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(data['message'], 'Charity approved')  # Check the response message

        # Check if the charity's status is now 'Approved' in the database
        approved_charity = Charity.query.get(charity_id_to_approve)
        self.assertEqual(approved_charity.status, 'Approved')

    def test_reject_charity(self):
        # Assuming you have a charity ID to reject
        charity_id_to_reject = 2

        response = self.client.post(f'/api/administrators/reject_charity/{charity_id_to_reject}')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(data['message'], 'Charity rejected')  # Check the response message

        # Check if the charity's status is now 'Rejected' in the database
        rejected_charity = Charity.query.get(charity_id_to_reject)
        self.assertEqual(rejected_charity.status, 'Rejected')

    def test_view_all_charities(self):
        response = self.client.get('/api/administrators/charities')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(len(data), 2)  # Assuming you have two sample charities in the database

    def test_delete_charity(self):
        # Assuming you have a charity ID to delete
        charity_id_to_delete = 1

        response = self.client.post(f'/api/administrators/delete_charity/{charity_id_to_delete}')
        self.assertEqual(response.status_code, 200)  # Assuming 200 is the expected status code
        data = response.get_json()
        self.assertEqual(data['message'], 'Charity deleted')  # Check the response message

        # Check if the charity is deleted from the database
        deleted_charity = Charity.query.get(charity_id_to_delete)
        self.assertIsNone(deleted_charity)

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
