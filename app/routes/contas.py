from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db
from app.models.conta import Conta
from datetime import datetime

bp_conta = Blueprint('conta', __name__, url_prefix='/conta')

@bp_conta.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_conta():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')
        vencimento = request.form.get('vencimento')

        conta = Conta(
            tipo=tipo,
            descricao=descricao,
            valor=float(valor),
            vencimento=datetime.strptime(vencimento, '%Y-%m-%d').date(),
            status='aberto'
        )
        db.session.add(conta)
        db.session.commit()

        return redirect(url_for('conta.cadastrar_conta'))

    return render_template('cadastrar_conta.html')

from datetime import datetime

@bp_conta.route('/relatorio', methods=['GET'])
def relatorio_contas():
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)

    contas = Conta.query

    if mes and ano:
        contas = contas.filter(db.extract('month', Conta.vencimento) == mes)
        contas = contas.filter(db.extract('year', Conta.vencimento) == ano)

    contas = contas.order_by(Conta.vencimento).all()

    total_pagar = sum(c.valor for c in contas if c.tipo == 'pagar' and c.status == 'aberto')
    total_receber = sum(c.valor for c in contas if c.tipo == 'receber' and c.status == 'aberto')

    return render_template(
        'relatorio_contas.html',
        contas=contas,
        total_pagar=total_pagar,
        total_receber=total_receber,
        now=datetime.now(),
        mes=mes,
        ano=ano
    )


@bp_conta.route('/pagar/<int:conta_id>', methods=['POST'])
def pagar_conta(conta_id):
    conta = Conta.query.get(conta_id)
    if conta:
        conta.status = 'pago'
        db.session.commit()
    return redirect(url_for('conta.relatorio_contas'))
