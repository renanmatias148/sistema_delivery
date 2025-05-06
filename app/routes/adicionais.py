# app/routes/adicionais.py
from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for
from app.helpers import login_required
from app.models import db
from app.models.adicional import Adicional
from app.utils.logs import registrar_acao

bp_adicional = Blueprint('adicional', __name__, url_prefix='/adicional')

@bp_adicional.route('/', methods=['GET', 'POST'])
def cadastrar_adicional():
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')

        adicional = Adicional(nome=nome, preco=float(preco))
        db.session.add(adicional)
        db.session.commit()

        return redirect(url_for('adicional.cadastrar_adicional'))

    return render_template('cadastrar_adicional.html')

@bp_adicional.route('/listar', methods=['GET'])
def listar_adicionais():
    adicionais = Adicional.query.all()
    return render_template('listar_adicionais.html', adicionais=adicionais)
@bp_adicional.route('/deletar/<int:id>', methods=['POST'])
@login_required(tipo='gestor')
def deletar_adicional(id):
    Adicional = Adicional.query.get_or_404(id)
    nome = Adicional.nome

    db.session.delete(Adicional)
    db.session.commit()

    registrar_acao('exclusão de adicional', f'Adicional #{id} - {nome} foi excluído.')

    flash('adicionl excluído com sucesso.', 'success')
    return redirect(url_for('adicional.listar'))
