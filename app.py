from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_cors import CORS
from flask_restx import Api


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

CORS(app)
api = Api(app, version='1.0', title='Your API', description='Your API Description')
from routes import *
# Create the database and tables based on models
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
