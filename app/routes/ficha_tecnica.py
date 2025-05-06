from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.models import db
from app.models.produto import Produto
from app.models.ingrediente import Ingrediente
from app.models.ficha_tecnica import FichaTecnica
from app.routes.auth import login_required
from app.utils.logs import registrar_acao

bp_ficha_tecnica = Blueprint('ficha_tecnica', __name__, url_prefix='/ficha_tecnica')

@bp_ficha_tecnica.route('/', methods=['GET', 'POST'])
def cadastrar_ficha_tecnica():
    produtos = Produto.query.all()
    ingredientes = Ingrediente.query.all()

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        ingrediente_id = request.form.get('ingrediente_id')
        quantidade = request.form.get('quantidade')

        ficha = FichaTecnica(
            produto_id=int(produto_id),
            ingrediente_id=int(ingrediente_id),
            quantidade=float(quantidade)
        )
        db.session.add(ficha)
        db.session.commit()

        return redirect(url_for('ficha_tecnica.cadastrar_ficha_tecnica'))

    return render_template('cadastrar_ficha_tecnica.html', produtos=produtos, ingredientes=ingredientes)
@bp_ficha_tecnica.route('/ficha/cadastrar', methods=['GET', 'POST'])
@login_required(tipo='gestor')
def cadastrar_ficha():
    if request.method == 'POST':
        produto_id = request.form['produto_id']
        ingrediente_id = request.form['ingrediente_id']
        quantidade = float(request.form['quantidade'])

        nova = FichaTecnica(produto_id=produto_id, ingrediente_id=ingrediente_id, quantidade=quantidade)
        db.session.add(nova)
        db.session.commit()

        registrar_acao('cadastro de ficha técnica',
                       f'Adicionado ingrediente #{ingrediente_id} ao produto #{produto_id} (quantidade: {quantidade})')

        flash('Ficha técnica cadastrada com sucesso.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/cadastrar_ficha.html')
@bp_ficha_tecnica.route('/ficha/editar/<int:id>', methods=['GET', 'POST'])
@login_required(tipo='gestor')
def editar_ficha(id):
    ficha = FichaTecnica.query.get_or_404(id)
    anterior = ficha.quantidade

    if request.method == 'POST':
        ficha.quantidade = float(request.form['quantidade'])
        db.session.commit()

        registrar_acao('edição de ficha técnica',
                       f'Ficha #{id} alterada: de {anterior} para {ficha.quantidade}')

        flash('Ficha técnica atualizada.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/editar_ficha.html', ficha=ficha)
