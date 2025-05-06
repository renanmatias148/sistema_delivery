from flask import Blueprint, request, render_template, redirect, url_for
from app.models.produto import Produto
from app.services.estoque_service import baixar_estoque

bp_venda = Blueprint('venda', __name__, url_prefix='/venda')

@bp_venda.route('/', methods=['GET', 'POST'])
def realizar_venda():
    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        quantidade = int(request.form.get('quantidade'))

        baixar_estoque(produto_id, quantidade)

        return redirect(url_for('venda.realizar_venda'))

    return render_template('realizar_venda.html', produtos=produtos)
