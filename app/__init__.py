from flask import Flask
from config import Config
from flask_login import LoginManager

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)


from app import routes
