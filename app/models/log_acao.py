from app import db

class LogAcao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    acao = db.Column(db.String(255))
    data_hora = db.Column(db.DateTime)
