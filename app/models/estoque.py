from app.models import db
from datetime import datetime

class MovimentoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    tipo = db.Column(db.String(10))  # entrada ou saida
    quantidade = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.utcnow)
