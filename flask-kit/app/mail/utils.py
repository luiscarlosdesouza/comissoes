from flask_mail import Message
from app import mail
from flask import current_app

def send_email(subject, recipients, body, html=None):
    """
    Função auxiliar para envio de e-mails usando Flask-Mail.
    """
    msg = Message(subject, recipients=recipients)
    msg.body = body
    if html:
        msg.html = html
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
