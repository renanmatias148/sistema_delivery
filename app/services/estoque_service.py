from app.models import db
from app.models.ficha_tecnica import FichaTecnica
from app.models.ingrediente import Ingrediente

def baixar_estoque(produto_id, quantidade_vendida=1):
    """
    Dá baixa no estoque dos ingredientes baseados na ficha técnica.
    quantidade_vendida = quantos produtos foram vendidos (padrão: 1)
    """
    fichas = FichaTecnica.query.filter_by(produto_id=produto_id).all()

    for ficha in fichas:
        ingrediente = Ingrediente.query.get(ficha.ingrediente_id)
        if ingrediente:
            quantidade_utilizada = ficha.quantidade * quantidade_vendida
            ingrediente.estoque -= quantidade_utilizada

    db.session.commit()
