import uuid
from datetime import datetime, timedelta
from app.models import db

class TokenRecuperacaoSenha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    expira_em = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
