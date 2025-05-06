from app.models import db

class Conta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # 'pagar' ou 'receber'
    descricao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='aberto')  # 'aberto' ou 'pago'
