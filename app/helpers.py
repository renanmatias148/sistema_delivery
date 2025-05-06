from functools import wraps
from flask import session, redirect, url_for, flash

# Decorador universal para rotas protegidas
# Se "tipo" for informado, valida também o tipo do usuário

def login_required(tipo=None):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if 'usuario_tipo' not in session:
                flash('Você precisa fazer login.', 'danger')
                return redirect(url_for('auth.login'))

            if tipo and session['usuario_tipo'] != tipo:
                flash('Acesso não autorizado para seu perfil.', 'danger')
                return redirect(url_for('auth.login'))

            return func(*args, **kwargs)
        return decorated_view
    return wrapper
