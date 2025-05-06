from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from app.models.pedido import Pedido
from app.models import db
from app.helpers import login_required
from app.models.usuario import Usuario
from app.utils.logs import registrar_acao

bp_entregador = Blueprint('entregador', __name__, url_prefix='/entregador')

@bp_entregador.route('/painel')
def painel():
    if 'usuario_tipo' not in session or session['usuario_tipo'] != 'entregador':
        return redirect(url_for('auth.login'))

    if 'usuario_tipo' not in session or session['usuario_tipo'] != 'entregador':
        return redirect(url_for('auth.login'))

    pedidos = Pedido.query.filter_by(status='preparo').order_by(Pedido.id.asc()).all()
    return render_template('entregador/painel.html', pedidos=pedidos)
@bp_entregador.route('/marcar_entregue/<int:pedido_id>', methods=['POST'])
def marcar_entregue(pedido_id):
    if 'usuario_tipo' not in session or session['usuario_tipo'] != 'entregador':
        return redirect(url_for('auth.login'))

    pedido = Pedido.query.get(pedido_id)
    if pedido and pedido.status == 'preparo':
        pedido.status = 'entregue'
        db.session.commit()

    return redirect(url_for('entregador.painel'))
@bp_entregador.route('/aceitar/<int:pedido_id>', methods=['POST'])
def aceitar_entrega(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.status == 'preparo':
        pedido.status = 'saiu'
        db.session.commit()
    return redirect(url_for('entregador.painel'))
from werkzeug.security import check_password_hash, generate_password_hash

@bp_entregador.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if session.get('usuario_tipo') != 'entregador':
        return redirect(url_for('auth.login'))

    entregador = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        atual = request.form['senha_atual']
        nova = request.form['nova_senha']
        confirmar = request.form['confirmar_senha']

        if not check_password_hash(entregador.senha, atual):
            flash('Senha atual incorreta', 'danger')
        elif nova != confirmar:
            flash('As senhas não coincidem', 'warning')
        else:
            entregador.senha = generate_password_hash(nova)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('entregador.painel'))

    return render_template('entregador/alterar_senha.html')
@bp_entregador.route('/aceitar/<int:id>', methods=['POST'])
@login_required(tipo='entregador')
def aceitar(id):
    pedido = Pedido.query.get_or_404(id)
    if pedido.status == 'preparo':
        pedido.status = 'saiu'
        db.session.commit()

        registrar_acao('entregador aceitou pedido', f'Pedido #{pedido.id} marcado como \"saiu para entrega\".')

    return redirect(url_for('entregador.painel'))
