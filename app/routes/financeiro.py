from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.models import db
from app.models.financeiro import Financeiro
from datetime import date
from app.models.conta import ContaFinanceira
from app.models.conta import ContaFinanceira
from app.routes.auth import login_required
from app.utils.logs import registrar_acao

bp_financeiro = Blueprint('financeiro', __name__, url_prefix='/financeiro')

@bp_financeiro.route('/', methods=['GET', 'POST'])
def registrar_movimentacao():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')

        movimento = Financeiro(
            tipo=tipo,
            descricao=descricao,
            valor=float(valor),
            data=date.today()
        )
        db.session.add(movimento)
        db.session.commit()

        return redirect(url_for('financeiro.registrar_movimentacao'))

    return render_template('registrar_movimentacao.html')

@bp_financeiro.route('/relatorio', methods=['GET'])
def relatorio_financeiro():
    movimentacoes = Financeiro.query.order_by(Financeiro.data.desc()).all()
    saldo = sum(m.valor if m.tipo == 'entrada' else -m.valor for m in movimentacoes)

    entradas = sum(m.valor for m in movimentacoes if m.tipo == 'entrada')
    saidas = sum(m.valor for m in movimentacoes if m.tipo == 'saida')

    return render_template(
        'relatorio_financeiro.html',
        movimentacoes=movimentacoes,
        saldo=saldo,
        entradas=entradas,
        saidas=saidas
    )
@bp_financeiro.route('/conta/editar/<int:id>', methods=['GET', 'POST'])
@login_required(tipo='gestor')
def editar_conta(id):
    conta = ContaFinanceira.query.get_or_404(id)
    valor_antigo = conta.valor

    if request.method == 'POST':
        conta.descricao = request.form['descricao']
        conta.tipo = request.form['tipo']  # 'receber' ou 'pagar'
        conta.valor = float(request.form['valor'])
        conta.vencimento = request.form['vencimento']
        db.session.commit()

        registrar_acao(
            'edição de conta financeira',
            f'Conta #{conta.id} editada: valor de R$ {valor_antigo:.2f} para R$ {conta.valor:.2f}'
        )

        flash('Conta atualizada com sucesso.', 'success')
        return redirect(url_for('admin.relatorio_financeiro'))

    return render_template('admin/editar_conta.html', conta=conta)
