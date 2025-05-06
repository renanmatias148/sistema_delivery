from app import db
#db.create_all()

class ZonaEntrega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    taxa = db.Column(db.Float)
    coordenadas = db.Column(db.Text)  # JSON das coordenadas do polígono
