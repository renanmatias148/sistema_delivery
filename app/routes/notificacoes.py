# Em app/routes/notificacoes.py
from flask import Blueprint, jsonify
from app.models.pedido import Pedido
from app.models.ingrediente import Ingrediente

bp_notificacoes = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')

@bp_notificacoes.route('/atualizar')
def atualizar():
    novos_pedidos = Pedido.query.filter_by(status='pendente').count()
    estoque_baixo = Ingrediente.query.filter(Ingrediente.quantidade < Ingrediente.quantidade_minima).count()

    return jsonify({
        'novos_pedidos': novos_pedidos,
        'estoque_baixo': estoque_baixo,
        'total': novos_pedidos + estoque_baixo
    })
