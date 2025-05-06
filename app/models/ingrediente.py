# app/models/ingrediente.py
from app.models import db

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    unidade = db.Column(db.String(50), nullable=False)
    estoque = db.Column(db.Float, default=0)
