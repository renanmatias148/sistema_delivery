from app import db
from datetime import datetime

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100))
    cliente_telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    lat = db.Column(db.Float)  # Latitude do cliente
    lng = db.Column(db.Float)  # Longitude do cliente
    zona_nome = db.Column(db.String(100))
    taxa_entrega = db.Column(db.Float)
    total = db.Column(db.Float)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
