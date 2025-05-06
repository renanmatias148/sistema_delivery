# app/routes/ingredientes.py
from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for
from app.helpers import login_required
from app.models import db
from app.models.ingrediente import Ingrediente
from app.utils.logs import registrar_acao

bp_ingrediente = Blueprint('ingrediente', __name__, url_prefix='/ingrediente')

@bp_ingrediente.route('/', methods=['GET', 'POST'])
def cadastrar_ingrediente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        unidade = request.form.get('unidade')
        estoque = request.form.get('estoque')

        ingrediente = Ingrediente(
            nome=nome,
            unidade=unidade,
            estoque=float(estoque)
        )
        db.session.add(ingrediente)
        db.session.commit()

        return redirect(url_for('ingrediente.cadastrar_ingrediente'))

    return render_template('cadastrar_ingrediente.html')

@bp_ingrediente.route('/listar', methods=['GET'])
def listar_ingredientes():
    ingredientes = Ingrediente.query.all()
    return render_template('listar_ingredientes.html', ingredientes=ingredientes)
@bp_ingrediente.route('/deletar/<int:id>', methods=['POST'])
@login_required(tipo='gestor')
def deletar_ingrediente(id):
    Ingrediente = Ingrediente.query.get_or_404(id)
    nome = Ingrediente.nome

    db.session.delete(Ingrediente)
    db.session.commit()

    registrar_acao('exclusão de ingrediente', f'ingrediente #{id} - {nome} foi excluído.')

    flash('ingrediente excluído com sucesso.', 'success')
    return redirect(url_for('ingrediente.listar'))
