from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Usuario
from werkzeug.security import generate_password_hash
from app.utils.decorators import login_required
from app.utils.logs import registrar_acao

bp_func = Blueprint('funcionarios', __name__)

@bp_func.route('/admin/funcionarios')
@login_required(tipo='superadmin')
def listar_funcionarios():
    funcionarios = Usuario.query.filter(Usuario.tipo != 'cliente').all()
    return render_template('admin/funcionarios.html', funcionarios=funcionarios)


@bp_func.route('/admin/funcionarios/novo', methods=['GET', 'POST'])
@login_required(tipo='superadmin')
def novo_funcionario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        tipo = request.form['tipo']

        novo = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
        db.session.add(novo)
        db.session.commit()
        registrar_acao('cadastro de funcionário', f'{nome} ({email}) - tipo: {tipo}')
        flash('Funcionário cadastrado.', 'success')
        return redirect(url_for('funcionarios.listar_funcionarios'))

    return render_template('admin/novo_funcionario.html')


@bp_func.route('/admin/funcionarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required(tipo='superadmin')
def editar_funcionario(id):
    funcionario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        funcionario.nome = request.form['nome']
        funcionario.email = request.form['email']
        funcionario.tipo = request.form['tipo']
        db.session.commit()
        registrar_acao('edição de funcionário', f'#{id} atualizado')
        flash('Funcionário atualizado.', 'success')
        return redirect(url_for('funcionarios.listar_funcionarios'))

    return render_template('admin/editar_funcionario.html', funcionario=funcionario)


@bp_func.route('/admin/funcionarios/excluir/<int:id>', methods=['POST'])
@login_required(tipo='superadmin')
def excluir_funcionario(id):
    funcionario = Usuario.query.get_or_404(id)
    nome = funcionario.nome
    db.session.delete(funcionario)
    db.session.commit()
    registrar_acao('exclusão de funcionário', f'{nome} removido do sistema')
    flash('Funcionário removido.', 'warning')
    return redirect(url_for('funcionarios.listar_funcionarios'))
