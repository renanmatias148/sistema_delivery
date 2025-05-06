from app.models import db
from datetime import datetime

created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_telefone = db.Column(db.String(20), nullable=False)
    cliente_endereco = db.Column(db.String(200), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, enviado, finalizado
    avaliacao = db.Column(db.Integer, nullable=True)

    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
