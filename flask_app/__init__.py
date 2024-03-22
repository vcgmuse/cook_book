from flask import Flask
import secrets
app_secret = secrets.token_hex(32)
app = Flask(__name__)
app.secret_key = app_secret
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)