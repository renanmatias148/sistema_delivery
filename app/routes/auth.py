from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app.models.token import TokenRecuperacaoSenha
from app.models.usuario import Usuario
from app.models import db
from app.utils.email import enviar_email
from app.models.log_acesso import LogAcesso

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Protege rotas com login e tipo de usuário
def login_required(tipo=None):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if 'usuario_id' not in session:
                flash('Você precisa fazer login.', 'danger')
                return redirect(url_for('auth.login'))
            if tipo and session['usuario_tipo'] != tipo:
                flash('Acesso não autorizado.', 'danger')
                return redirect(url_for('auth.login'))
            return func(*args, **kwargs)
        return decorated_view
    return wrapper

# Rota de login
@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['usuario_tipo'] = usuario.tipo

            # Registrar log de acesso
            log = LogAcesso(
                usuario_id=usuario.id,
                tipo=usuario.tipo,
                ip=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()

            flash('Login realizado com sucesso!', 'success')
            if usuario.tipo == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif usuario.tipo == 'entregador':
                return redirect(url_for('entregador.painel'))
            else:
                return redirect(url_for('cliente.painel'))

        flash('Email ou senha inválidos.', 'danger')

    return render_template('auth/login.html')

# Rota de logout
@bp_auth.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))

# Cadastro de usuários
@bp_auth.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo = request.form.get('tipo')

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('auth.cadastro'))

        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash, tipo=tipo)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/cadastro.html')

# Página e atualização de perfil
@bp_auth.route('/perfil', methods=['GET', 'POST'])
@login_required()
def perfil():
    usuario = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        nova_senha = request.form.get('senha')

        if nova_senha:
            usuario.senha = generate_password_hash(nova_senha)

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.perfil'))

    return render_template('auth/perfil.html', usuario=usuario)

# Envio de senha atual (não recomendado, substituído pelo token)
@bp_auth.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            corpo = f"Olá, {usuario.nome}!\n\nSua senha atual é: (oculta por segurança)"
            enviar_email(usuario.email, 'Recuperação de Senha - Sistema Delivery', corpo)
            flash('Senha enviada para seu e-mail!', 'success')
        else:
            flash('Email não encontrado.', 'danger')
        return redirect(url_for('auth.recuperar'))

    return render_template('auth/recuperar.html')

# Envio de token para redefinir senha
@bp_auth.route('/esqueci', methods=['GET', 'POST'])
def esqueci():
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            import uuid
            token = str(uuid.uuid4())
            novo_token = TokenRecuperacaoSenha(token=token, usuario_id=usuario.id)
            db.session.add(novo_token)
            db.session.commit()

            link = url_for('auth.redefinir_senha', token=token, _external=True)
            corpo = f"Olá {usuario.nome},\n\nClique no link abaixo para redefinir sua senha:\n{link}"
            enviar_email(usuario.email, "Recuperação de Senha", corpo)

            flash('Um link de redefinição foi enviado para seu e-mail.', 'info')
        else:
            flash('Email não encontrado.', 'warning')

    return render_template('auth/esqueci.html')

# Página de redefinição de senha via token
@bp_auth.route('/redefinir/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    token_db = TokenRecuperacaoSenha.query.filter_by(token=token).first()

    if not token_db or token_db.expira_em < datetime.utcnow():
        flash('Token inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(token_db.usuario_id)

    if request.method == 'POST':
        nova = request.form['nova']
        confirmar = request.form['confirmar']

        if nova != confirmar:
            flash('Senhas não coincidem.', 'warning')
        else:
            usuario.senha = generate_password_hash(nova)
            db.session.delete(token_db)
            db.session.commit()
            flash('Senha atualizada com sucesso!', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/redefinir.html', token=token)
