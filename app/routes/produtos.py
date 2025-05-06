# app/routes/produtos.py
from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for
from app.helpers import login_required
from app.models import db
from app.models.produto import Produto

bp_produto = Blueprint('produto', __name__, url_prefix='/produto')

@bp_produto.route('/', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        categoria = request.form.get('categoria')

        produto = Produto(nome=nome, preco=float(preco), categoria=categoria)
        db.session.add(produto)
        db.session.commit()

        return redirect(url_for('produto.cadastrar_produto'))

    return render_template('cadastrar_produto.html')

@bp_produto.route('/listar', methods=['GET'])
def listar_produtos():
    produtos = Produto.query.all()
    return render_template('listar_produtos.html', produtos=produtos)
from app.utils.logs import registrar_acao

@bp_produto.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required(tipo='gestor')
def editar_produto(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        nome_anterior = produto.nome
        produto.nome = request.form['nome']
        produto.preco = request.form['preco']
        db.session.commit()

        registrar_acao('edição de produto', f'Produto #{produto.id} alterado de "{nome_anterior}" para "{produto.nome}"')

        flash('Produto atualizado com sucesso.', 'success')
        return redirect(url_for('produto.listar'))

    return render_template('produtos/editar.html', produto=produto)
@bp_produto.route('/deletar/<int:id>', methods=['POST'])
@login_required(tipo='gestor')
def deletar_produto(id):
    produto = Produto.query.get_or_404(id)
    nome = produto.nome

    db.session.delete(produto)
    db.session.commit()

    registrar_acao('exclusão de produto', f'Produto #{id} - {nome} foi excluído.')

    flash('Produto excluído com sucesso.', 'success')
    return redirect(url_for('produto.listar'))
