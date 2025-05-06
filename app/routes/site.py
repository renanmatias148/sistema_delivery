from flask import Blueprint, render_template, redirect, url_for, session, request
from app.models.pedido import ItemPedido,Pedido
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models import db

bp_site = Blueprint('site', __name__, url_prefix='/cardapio')

@bp_site.route('/')
def home_site():
    categorias = Categoria.query.all()
    produtos = Produto.query.all()
    return render_template('site/cardapio.html', categorias=categorias, produtos=produtos)

@bp_site.route('/adicionar_carrinho/<int:produto_id>')
def adicionar_carrinho(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return redirect(url_for('site.home_site'))

    if 'carrinho' not in session:
        session['carrinho'] = {}

    carrinho = session['carrinho']

    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] += 1
    else:
        carrinho[str(produto_id)] = {
            'nome': produto.nome,
            'preco': produto.preco,
            'quantidade': 1
        }

    session['carrinho'] = carrinho

    return redirect(url_for('site.ver_carrinho'))

@bp_site.route('/carrinho')
def ver_carrinho():
    carrinho = session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return render_template('site/carrinho.html', carrinho=carrinho, total=total)
@bp_site.route('/finalizar', methods=['GET', 'POST'])
def finalizar_pedido():
    carrinho = session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')

        # Criar o Pedido
        pedido = Pedido(
            cliente_nome=nome,
            cliente_telefone=telefone,
            cliente_endereco=endereco,
            total=total
        )
        db.session.add(pedido)
        db.session.commit()

        # Criar Itens do Pedido
        for item in carrinho.values():
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_nome=item['nome'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco']
            )
            db.session.add(item_pedido)

        db.session.commit()

        # Limpar o carrinho
        session.pop('carrinho', None)

        return render_template('site/pedido_realizado.html', pedido_id=pedido.id)

    return render_template('site/finalizar_pedido.html', carrinho=carrinho, total=total)
