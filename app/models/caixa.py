from app.models import db
from datetime import datetime

class MovimentacaoCaixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10))  # entrada ou saida
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
