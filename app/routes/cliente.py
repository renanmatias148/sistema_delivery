from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.models import db
from app.models.usuario import Usuario
from app.models.pedido import Pedido

bp_cliente = Blueprint('cliente', __name__, url_prefix='/cliente')

@bp_cliente.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = Usuario.query.filter_by(email=email, senha=senha, tipo='cliente').first()
        if user:
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome
            session['usuario_tipo'] = 'cliente'
            return redirect(url_for('cliente.painel'))
        else:
            flash('Credenciais inválidas.', 'danger')
            return redirect(url_for('cliente.login'))

    return render_template('cliente/login.html')

@bp_cliente.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('cliente.cadastro'))

        novo = Usuario(nome=nome, email=email, senha=senha, tipo='cliente')
        db.session.add(novo)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('cliente.login'))

    return render_template('cliente/cadastro.html')

@bp_cliente.route('/painel')
def painel():
    if session.get('usuario_tipo') != 'cliente':
        return redirect(url_for('cliente.login'))

    pedidos = Pedido.query.filter_by(cliente_id=session['usuario_id']).order_by(Pedido.id.desc()).all()
    return render_template('cliente/painel.html', pedidos=pedidos)

@bp_cliente.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('cliente.login'))
@bp_cliente.route('/avaliar/<int:pedido_id>', methods=['POST'])
def avaliar(pedido_id):
    if session.get('usuario_tipo') != 'cliente':
        return redirect(url_for('cliente.login'))

    nota = int(request.form.get('avaliacao'))
    pedido = Pedido.query.get(pedido_id)

    if pedido and pedido.cliente_id == session['usuario_id']:
        pedido.avaliacao = nota
        db.session.commit()
        flash('Obrigado pela sua avaliação! ⭐', 'success')

    return redirect(url_for('cliente.painel'))
@bp_cliente.route('/recibo/<int:pedido_id>')
def recibo(pedido_id):
    if session.get('usuario_tipo') != 'cliente':
        return redirect(url_for('cliente.login'))

    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.cliente_id != session.get('usuario_id'):
        return redirect(url_for('cliente.painel'))

    return render_template('cliente/recibo.html', pedido=pedido)

@bp_cliente.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if session.get('usuario_tipo') != 'cliente':
        return redirect(url_for('cliente.login'))

    cliente = cliente.query.get(session['usuario_id'])

    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        db.session.commit()
        flash('Perfil atualizado!', 'success')
        return redirect(url_for('cliente.perfil'))

    return render_template('cliente/perfil.html', cliente=cliente)
from werkzeug.security import check_password_hash, generate_password_hash

@bp_cliente.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if session.get('usuario_tipo') != 'cliente':
        return redirect(url_for('cliente.login'))

    cliente = cliente.query.get(session['usuario_id'])

    if request.method == 'POST':
        atual = request.form['senha_atual']
        nova = request.form['nova_senha']
        confirmar = request.form['confirmar_senha']

        if not check_password_hash(cliente.senha, atual):
            flash('Senha atual incorreta', 'danger')
        elif nova != confirmar:
            flash('As senhas não coincidem', 'warning')
        else:
            cliente.senha = generate_password_hash(nova)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('cliente.perfil'))

    return render_template('cliente/alterar_senha.html')
