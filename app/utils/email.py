from flask_mail import Message
from app import mail

def enviar_email(destinatario, assunto, corpo):
    msg = Message(assunto, recipients=[destinatario])
    msg.body = corpo
    mail.send(msg)
