# Tuinue Wasichana Donation Platform API

Tuinue Wasichana Donation Platform API is a Flask-based web service that provides endpoints for managing donors, charities, and donations. It allows donors to register, make donations, and view information related to their donations. Additionally, administrators can manage charities, approve or reject charity applications, and access their profiles.

## Postgres Images
![PostgreSQL1](https://github.com/RotichKipkoech/charities-donor/assets/134596553/7ca384e4-c84b-4ac5-89b8-671cce10a198)

![PostgreSQL2](https://github.com/RotichKipkoech/charities-donor/assets/134596553/9c15a546-9204-4041-968d-689a7f728c20)

## API Documentation

![Tuinue_API](https://github.com/RotichKipkoech/charities-donor/assets/134596553/6a6b661a-39e1-43dd-a4e1-0763d2002854)

## Table of Contents

Prerequisites
Installation
Getting Started
Donor Endpoints
Administrator Endpoints
Donation Endpoints
Authentication
API Documentation

### Prerequisites

Before running the API, make sure you have the following prerequisites installed:

Python 3.x
Pip (Python package manager)
Virtualenv (optional but recommended for managing dependencies)

### Installation
1. Clone the repository to your local machine.
bash:
Copy code
git clone <git@github.com:RotichKipkoech/charities-donor.git>
2. cd charities-donor
3. Create a virtual environment (optional but recommended).
bash:
Copy code
python -m venv venv
source venv/bin/activate
4. Install the required packages.
bash:
Copy code
pip install -r requirements.txt

### Getting Started
To start the API, follow these steps:

Make sure you are in the project directory.
bash:
Copy code
cd charities-donor
Run the Flask application.
bash:
Copy code
python app.py
Your API should now be running locally at http://localhost:5000. You can interact with the API.

#### Donor Endpoints

1. Register a Donor
Endpoint: /donors/register
Method: POST
Description: Register a new donor.
Parameters: first_name, last_name, email, and password.
Response: Success message and status code.

2. Get Donor Profile
Endpoint: /donors/<int:donor_id>
Method: GET
Description: Retrieve details of a specific donor by their ID.
Parameters: donor_id.
Response: Donor information.

3. List Donor's Donations
Endpoint: /donors/<int:donor_id>/donations
Method: GET
Description: List donations made by a specific donor.
Parameters: donor_id.
Response: List of donations.

4. Donor Login
Endpoint: /auth/donors/login
Method: POST
Description: Authenticate and log in a donor.
Parameters: email and password.
Response: Access token for authentication.

5. Donor Logout
Endpoint: /auth/donors/logout
Method: GET
Description: Log out a donor.
Response: Logout confirmation.

6. Get Beneficiary Stories
Endpoint: /donor_stories
Method: GET
Description: Retrieve stories about beneficiaries of the donor's donations.
Response: List of beneficiary stories.

#### Administrator Endpoints

1. Approve Charity Application
Endpoint: /administrators/approve_charity/<int:charity_id>
Method: POST
Description: Approve a pending charity application.
Parameters: charity_id.
Response: Approval confirmation.

2. Reject Charity Application
Endpoint: /administrators/reject_charity/<int:charity_id>
Method: POST
Description: Reject a pending charity application.
Parameters: charity_id.
Response: Rejection confirmation.

3. List Pending Charities
Endpoint: /administrators/pending_charities
Method: GET
Description: View pending charities.
Response: List of pending charities.

4. List All Charities
Endpoint: /administrators/charities
Method: GET
Description: View all charities with pagination.
Response: List of charities with pagination.

5. Delete Charity
Endpoint: /administrators/delete_charity/<int:charity_id>
Method: POST
Description: Delete a charity by ID.
Parameters: charity_id.
Response: Deletion confirmation.

6. Administrator Login
Endpoint: /administrators/login
Method: POST
Description: Authenticate and log in an administrator.
Parameters: username and password.
Response: Access token for authentication.

7. Administrator Profile
Endpoint: /administrators/profile
Method: GET
Description: Retrieve the profile of an administrator.
Response: Administrator's profile information.

#### Donation Endpoints

1. Initiate Donation
Endpoint: /donations/donate
Method: POST
Description: Initiate a donation from a donor to a charity.
Parameters: donor_id, amount, phone_number, is_anonymous, charity_id, and is_one_time_donation.
Response: Donation initiation confirmation.

#### Authentication
The API uses authentication for certain endpoints. Donors and administrators can log in to access their profiles and perform specific actions.

Authentication is implemented using JWT (JSON Web Tokens). When logging in, the API provides an access token that must be included in the header of authenticated requests.

#### API Documentation
Detailed API documentation can be found at the /apidocs endpoint when the API is running. It is generated using Swagger and provides information on available routes, request parameters, and expected responses.
