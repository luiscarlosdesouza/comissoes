from flask import Blueprint, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user
from app import User
import requests
from requests_oauthlib import OAuth1

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Lógica simplificada de redirecionamento (precisa de consumer key/secret da USP)
    if not current_app.config['USP_AUTH_KEY']:
        flash('Configuração de Senha Única faltando (.env)', 'danger')
        return redirect(url_for('index'))
    
    # Aqui entraria o fluxo OAuth 1.0a para obter request_token e redirecionar
    # Para o start-kit, deixaremos os placeholders
    flash('Funcionalidade de Login Senha Única pré-configurada. Insira suas credenciais.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/callback')
def callback():
    # Lógica para tratar o retorno da USP e criar o usuário
    flash('Autenticação concluída com sucesso (Simulação).', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('index'))
