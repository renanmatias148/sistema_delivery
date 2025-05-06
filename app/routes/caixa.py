from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db
from app.models.caixa import MovimentacaoCaixa
from app.utils.logs import registrar_acao
from app.utils.decorators import login_required

bp_caixa = Blueprint('caixa', __name__, url_prefix='/caixa')

@bp_caixa.route('/movimento', methods=['GET', 'POST'])
@login_required(tipo='gestor')
def registrar_movimentacao():
    if request.method == 'POST':
        tipo = request.form['tipo']  # entrada ou saida
        valor = float(request.form['valor'])
        descricao = request.form['descricao']

        novo = MovimentacaoCaixa(tipo=tipo, valor=valor, descricao=descricao)
        db.session.add(novo)
        db.session.commit()

        registrar_acao(
            'movimentação de caixa',
            f'{tipo.upper()} de R$ {valor:.2f} registrada: {descricao}'
        )

        flash('Movimentação registrada com sucesso.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/movimentacao.html')
