from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(tipo=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get('usuario_id'):
                flash('Você precisa estar logado.', 'warning')
                return redirect(url_for('auth.login'))

            if tipo and session.get('usuario_tipo') != tipo:
                flash('Acesso negado!', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator
