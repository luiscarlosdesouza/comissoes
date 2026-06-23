from flask import Flask, render_template
from flask_login import LoginManager, UserMixin
from flask_mail import Mail
from config import Config

mail = Mail()
login = LoginManager()
login.login_view = 'auth.login'

class User(UserMixin):
    def __init__(self, id, name=None, email=None):
        self.id = id
        self.name = name
        self.email = email

@login.user_loader
def load_user(id):
    # Em um app real, buscaria no banco de dados. 
    # Para o start-kit, usaremos dados da sessão ou um mock.
    return User(id)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mail.init_app(app)
    login.init_app(app)

    # Registro de Blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/')
    def index():
        return render_template('base.html')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html'), 404

    return app
