import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'
    APP_NAME = os.environ.get('APP_NAME') or 'Sistema USP'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # USP Theme Configs
    USP_THEME_SKIN = os.environ.get('USP_THEME_SKIN') or 'ime'
    USP_THEME_CONTAINER = 'container-fluid'
    USP_THEME_SLOGAN = 'Instituto de Matemática e Estatística'
    
    # Menus (Exemplo)
    USP_THEME_MENU = [
        {'text': 'Home', 'url': '/'},
        {'text': 'Sobre', 'url': '/about'},
        {
            'text': 'Submenu Exemplo',
            'submenu': [
                {'text': 'Item 1', 'url': '/item1'},
                {'text': 'Item 2', 'url': '/item2'},
            ]
        }
    ]
    
    USP_THEME_SISTEMAS = [
        {'text': 'USP', 'url': 'https://www.usp.br'},
        {'text': 'Portão de Sistemas', 'url': 'https://uspdigital.usp.br'},
    ]
    
    # OAuth Senha Única
    USP_AUTH_KEY = os.environ.get('USP_AUTH_KEY')
    USP_AUTH_SECRET = os.environ.get('USP_AUTH_SECRET')
    USP_AUTH_CALLBACK_URL = f"{APP_URL}/auth/callback"
    
    # Mail Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    CURRENT_YEAR = datetime.now().year
