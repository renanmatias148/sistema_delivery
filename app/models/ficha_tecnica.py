from app.models import db

class FichaTecnica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, nullable=False)
    ingrediente_id = db.Column(db.Integer, nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
