from datetime import datetime
from app.models import db

class LogAcesso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer)
    tipo = db.Column(db.String(20))  # superadmin, gestor, etc.
    ip = db.Column(db.String(50))
    data = db.Column(db.DateTime, default=datetime.utcnow)
