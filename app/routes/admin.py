from flask import Blueprint, render_template, redirect, send_file, url_for, request, flash, session
from weasyprint import HTML
from app.models.log_acesso import LogAcesso
from app.models.pedido import Pedido, ItemPedido
from app.models import db
from app.models.usuario import Usuario
from app.routes.auth import login_required  # Importa o decorador
from app.helpers import login_required
from datetime import datetime
from app.models.conta import ContaFinanceira
from weasyprint import HTML
import io

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

# DASHBOARD - Acesso: superadmin e gestor
@bp_admin.route('/dashboard')
@login_required()
def dashboard():
    if session['usuario_tipo'] not in ['superadmin', 'gestor']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('auth.login'))

    total_pedidos = Pedido.query.count()
    total_vendas = db.session.query(db.func.sum(Pedido.total)).scalar() or 0
    pendentes = Pedido.query.filter_by(status='pendente').count()
    preparo = Pedido.query.filter_by(status='preparo').count()
    entregue = Pedido.query.filter_by(status='entregue').count()

    return render_template('admin/dashboard.html',
                           total_pedidos=total_pedidos,
                           total_vendas=total_vendas,
                           pendentes=pendentes,
                           preparo=preparo,
                           entregue=entregue)

# LISTAR PEDIDOS - Acesso: superadmin e gestor
@bp_admin.route('/pedidos')
@login_required()
def listar_pedidos():
    if session['usuario_tipo'] not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    status = request.args.get('status')
    if status in ['pendente', 'preparo', 'entregue']:
        pedidos = Pedido.query.filter_by(status=status).order_by(Pedido.id.desc()).all()
    else:
        pedidos = Pedido.query.order_by(Pedido.id.desc()).all()

    total_todos = Pedido.query.count()
    total_pendentes = Pedido.query.filter_by(status='pendente').count()
    total_preparo = Pedido.query.filter_by(status='preparo').count()
    total_entregue = Pedido.query.filter_by(status='entregue').count()

    return render_template('admin/pedidos.html', pedidos=pedidos, status_filtro=status,
                           total_todos=total_todos, total_pendentes=total_pendentes,
                           total_preparo=total_preparo, total_entregue=total_entregue)

# ATUALIZAR STATUS DO PEDIDO - Acesso: superadmin e gestor
@bp_admin.route('/atualizar_status/<int:pedido_id>', methods=['POST'])
@login_required()
def atualizar_status(pedido_id):
    if session['usuario_tipo'] not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    pedido = Pedido.query.get(pedido_id)
    if pedido:
        novo_status = request.form.get('status')
        pedido.status = novo_status
        db.session.commit()

    return redirect(url_for('admin.listar_pedidos'))

# IMPRIMIR PEDIDO - Acesso: superadmin e gestor
@bp_admin.route('/imprimir_pedido/<int:pedido_id>')
@login_required()
def imprimir_pedido(pedido_id):
    if session['usuario_tipo'] not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return redirect(url_for('admin.listar_pedidos'))
    return render_template('admin/imprimir_pedido.html', pedido=pedido)

# RELATÓRIO DE VENDAS - Acesso: superadmin e gestor
@bp_admin.route('/relatorio')
@login_required()
def relatorio_vendas():
    if session['usuario_tipo'] not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    dia = request.args.get('dia')
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    vendas = Pedido.query

    if dia and mes and ano:
        vendas = vendas.filter(
            db.extract('day', Pedido.id) == int(dia),
            db.extract('month', Pedido.id) == int(mes),
            db.extract('year', Pedido.id) == int(ano)
        )
    elif mes and ano:
        vendas = vendas.filter(
            db.extract('month', Pedido.id) == int(mes),
            db.extract('year', Pedido.id) == int(ano)
        )
    elif ano:
        vendas = vendas.filter(
            db.extract('year', Pedido.id) == int(ano)
        )

    vendas = vendas.order_by(Pedido.id.desc()).all()
    total_vendas = sum(v.total for v in vendas)

    return render_template('admin/relatorio_vendas.html', vendas=vendas, total_vendas=total_vendas)

# RANKING DE PRODUTOS - Acesso: superadmin e gestor
@bp_admin.route('/ranking')
@login_required()
def ranking_produtos():
    if session['usuario_tipo'] not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    from app.models.pedido import ItemPedido
    ranking = db.session.query(
        ItemPedido.produto_nome,
        db.func.sum(ItemPedido.quantidade).label('total_vendido')
    ).group_by(ItemPedido.produto_nome).order_by(db.desc('total_vendido')).limit(10).all()

    return render_template('admin/ranking_produtos.html', ranking=ranking)
from werkzeug.security import check_password_hash, generate_password_hash

@bp_admin.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if session.get('usuario_tipo') not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    admin = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        atual = request.form['senha_atual']
        nova = request.form['nova_senha']
        confirmar = request.form['confirmar_senha']

        if not check_password_hash(admin.senha, atual):
            flash('Senha atual incorreta', 'danger')
        elif nova != confirmar:
            flash('As senhas não coincidem', 'warning')
        else:
            admin.senha = generate_password_hash(nova)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))

    return render_template('admin/alterar_senha.html')
@bp_admin.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if session.get('usuario_tipo') not in ['superadmin', 'gestor']:
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('admin.perfil'))

    return render_template('admin/perfil.html', usuario=usuario)
@bp_admin.route('/usuarios')
@login_required(tipo='superadmin')
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)
@bp_admin.route('/logs')
@login_required(tipo='superadmin')
def ver_logs():
    logs = LogAcesso.query.order_by(LogAcesso.data.desc()).limit(50).all()
    return render_template('admin/logs.html', logs=logs)
@bp_admin.route('/super_dashboard')
@login_required(tipo='superadmin')
def super_dashboard():
    total_usuarios = Usuario.query.count()
    total_clientes = Usuario.query.filter_by(tipo='cliente').count()
    total_pedidos = Pedido.query.count()
    pedidos_entregues = Pedido.query.filter_by(status='entregue').all()
    total_vendas = sum(p.total for p in pedidos_entregues)

    logs = LogAcesso.query.order_by(LogAcesso.data.desc()).limit(5).all()

    return render_template('admin/super_dashboard.html', **locals())
@bp_admin.route('/acoes')
@login_required(tipo='superadmin')
def acoes():
    from app.models.log_acao import LogAcao
    logs = LogAcao.query.order_by(LogAcao.data.desc()).limit(50).all()
    return render_template('admin/log_acoes.html', logs=logs)
from app.utils.logs import registrar_acao

@bp_admin.route('/pedido/status/<int:id>', methods=['POST'])
@login_required(tipo='gestor')
def mudar_status(id):
    pedido = Pedido.query.get_or_404(id)
    novo_status = request.form['status']
    status_anterior = pedido.status

    pedido.status = novo_status
    db.session.commit()

    registrar_acao('mudança de status do pedido',
                   f'Pedido #{pedido.id} alterado de "{status_anterior}" para "{novo_status}"')

    flash('Status do pedido atualizado.', 'success')
    return redirect(url_for('admin.pedidos'))
@bp_admin.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required(tipo='superadmin')
def criar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        tipo = request.form['tipo']
        senha = generate_password_hash(request.form['senha'])

        novo = Usuario(nome=nome, email=email, tipo=tipo, senha=senha)
        db.session.add(novo)
        db.session.commit()

        registrar_acao('cadastro de usuário',
                       f'Novo usuário criado: {nome} ({email}), tipo: {tipo}')

        flash('Usuário cadastrado com sucesso.', 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/novo_usuario.html')
@bp_admin.route('/relatorio/financeiro')
@login_required(tipo='gestor')
def relatorio_financeiro():
    mes = request.args.get('mes') or datetime.now().month
    ano = request.args.get('ano') or datetime.now().year

    contas = ContaFinanceira.query.filter_by(mes=mes, ano=ano).all()
    total = sum(c.valor for c in contas)

    registrar_acao('acesso a relatório financeiro',
                   f'Relatório de {mes}/{ano} acessado com total de R$ {total:.2f}')

    return render_template('admin/relatorio_financeiro.html', contas=contas, total=total, mes=mes, ano=ano)

@bp_admin.route('/relatorio/financeiro/pdf')
@login_required(tipo='gestor')
def exportar_relatorio_pdf():
    mes = request.args.get('mes') or datetime.now().month
    ano = request.args.get('ano') or datetime.now().year
    contas = ContaFinanceira.query.filter_by(mes=mes, ano=ano).all()
    total = sum(c.valor for c in contas)

    html = render_template('admin/exportar_relatorio_pdf.html', contas=contas, total=total, mes=mes, ano=ano)
    pdf = HTML(string=html).write_pdf()
    return send_file(io.BytesIO(pdf), download_name=f"relatorio_{mes}_{ano}.pdf", as_attachment=True)

import xlsxwriter

@bp_admin.route('/relatorio/financeiro/excel')
@login_required(tipo='gestor')
def exportar_relatorio_excel():
    mes = request.args.get('mes') or datetime.now().month
    ano = request.args.get('ano') or datetime.now().year
    contas = ContaFinanceira.query.filter_by(mes=mes, ano=ano).all()

    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Relatório Financeiro')

    ws.write(0, 0, 'Descrição')
    ws.write(0, 1, 'Tipo')
    ws.write(0, 2, 'Valor')
    ws.write(0, 3, 'Vencimento')

    for i, conta in enumerate(contas, start=1):
        ws.write(i, 0, conta.descricao)
        ws.write(i, 1, conta.tipo)
        ws.write(i, 2, conta.valor)
        ws.write(i, 3, conta.vencimento.strftime('%d/%m/%Y'))

    wb.close()
    output.seek(0)
    return send_file(output, download_name=f'relatorio_{mes}_{ano}.xlsx', as_attachment=True)
from sqlalchemy import func
from app.models import PedidoItem, Produto

@bp_admin.route('/ranking')
@login_required(tipo='gestor')
def ranking():
    ranking = db.session.query(
        Produto.nome,
        func.sum(PedidoItem.quantidade).label('total_vendido')
    ).join(Produto, Produto.id == PedidoItem.produto_id) \
     .group_by(Produto.nome) \
     .order_by(func.sum(PedidoItem.quantidade).desc()) \
     .limit(10).all()

    return render_template('admin/ranking.html', ranking=ranking)
from datetime import datetime
from flask import request

@bp_admin.route('/ranking', methods=['GET'])
@login_required(tipo='gestor')
def ranking():
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    query = db.session.query(
        Produto.nome,
        func.sum(PedidoItem.quantidade).label('total_vendido')
    ).join(Produto, Produto.id == PedidoItem.produto_id) \
     .join(PedidoItem.pedido)  # relaciona com o pedido para acessar a data

    if data_inicio:
        dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(Pedido.data >= dt_inicio)
    if data_fim:
        dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        query = query.filter(Pedido.data <= dt_fim)

    ranking = query.group_by(Produto.nome) \
                   .order_by(func.sum(PedidoItem.quantidade).desc()) \
                   .limit(10).all()

    return render_template('admin/ranking.html', ranking=ranking, data_inicio=data_inicio, data_fim=data_fim)
from weasyprint import HTML
import io

@bp_admin.route('/ranking/pdf')
@login_required(tipo='gestor')
def ranking_pdf():
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    query = db.session.query(
        Produto.nome,
        func.sum(PedidoItem.quantidade).label('total_vendido')
    ).join(Produto, Produto.id == PedidoItem.produto_id) \
     .join(PedidoItem.pedido)

    if data_inicio:
        dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(Pedido.data >= dt_inicio)
    if data_fim:
        dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        query = query.filter(Pedido.data <= dt_fim)

    ranking = query.group_by(Produto.nome) \
                   .order_by(func.sum(PedidoItem.quantidade).desc()) \
                   .limit(10).all()

    html = render_template('admin/exportar_ranking_pdf.html', ranking=ranking, data_inicio=data_inicio, data_fim=data_fim)
    pdf = HTML(string=html).write_pdf()
    return send_file(io.BytesIO(pdf), download_name="ranking_produtos.pdf", as_attachment=True)
import xlsxwriter

@bp_admin.route('/ranking/excel')
@login_required(tipo='gestor')
def ranking_excel():
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    query = db.session.query(
        Produto.nome,
        func.sum(PedidoItem.quantidade).label('total_vendido')
    ).join(Produto, Produto.id == PedidoItem.produto_id) \
     .join(PedidoItem.pedido)

    if data_inicio:
        dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(Pedido.data >= dt_inicio)
    if data_fim:
        dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        query = query.filter(Pedido.data <= dt_fim)

    ranking = query.group_by(Produto.nome) \
                   .order_by(func.sum(PedidoItem.quantidade).desc()) \
                   .limit(10).all()

    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Ranking')

    ws.write(0, 0, 'Produto')
    ws.write(0, 1, 'Total Vendido')

    for i, (nome, total) in enumerate(ranking, start=1):
        ws.write(i, 0, nome)
        ws.write(i, 1, total)

    wb.close()
    output.seek(0)
    return send_file(output, download_name="ranking_produtos.xlsx", as_attachment=True)
