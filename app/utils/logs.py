from app.models.log_acao import LogAcao
from app.models import db
from flask import session

def registrar_acao(acao, descricao):
    log = LogAcao(
        usuario_id=session.get('usuario_id'),
        tipo=session.get('usuario_tipo'),
        acao=acao,
        descricao=descricao
    )
    db.session.add(log)
    db.session.commit()
