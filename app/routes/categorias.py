# app/routes/categorias.py
from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for
from app.helpers import login_required
from app.models import db
from app.models.categoria import Categoria
from app.utils.logs import registrar_acao

bp_categoria = Blueprint('categoria', __name__, url_prefix='/categoria')

@bp_categoria.route('/', methods=['GET', 'POST'])
def cadastrar_categoria():
    if request.method == 'POST':
        nome = request.form.get('nome')

        categoria = Categoria(nome=nome)
        db.session.add(categoria)
        db.session.commit()

        return redirect(url_for('categoria.cadastrar_categoria'))

    return render_template('cadastrar_categoria.html')

@bp_categoria.route('/listar', methods=['GET'])
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('listar_categorias.html', categorias=categorias)
@bp_categoria.route('/deletar/<int:id>', methods=['POST'])
@login_required(tipo='gestor')
def deletar_categoria(id):
    Categoria = Categoria.query.get_or_404(id)
    nome = Categoria.nome

    db.session.delete(Categoria)
    db.session.commit()

    registrar_acao('exclusão de categoria', f'Categoria #{id} - {nome} foi excluído.')

    flash('categoria excluído com sucesso.', 'success')
    return redirect(url_for('categoria.listar'))
