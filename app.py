from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restx import Api
from flask_jwt_extended import JWTManager
import secrets

app = Flask(__name__)
app.config.from_object(Config)

# Generate a JWT secret key
def generate_jwt_secret_key():
    secret_key = secrets.token_urlsafe(32)
    return secret_key

# Set the JWT secret key using the generated value
app.config['JWT_SECRET_KEY'] = generate_jwt_secret_key()

# Initialize JWTManager with your app
jwt = JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#Flask-Mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ann185683@gmail.com'
app.config['MAIL_PASSWORD'] = 'simw mswg zscy orjf'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


CORS(app)

api = Api(app, version='1.0', title='Tuinue_wasichana', description='Tuinue Wasichana Donation Platform API')

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
