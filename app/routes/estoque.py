from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Produto, MovimentoEstoque
from app.utils.logs import registrar_acao
from app.utils.decorators import login_required
from datetime import datetime
from flask import send_file
import io
import xlsxwriter
from weasyprint import HTML
from flask import render_template_string

bp_estoque = Blueprint('estoque', __name__)

@bp_estoque.route('/estoque', methods=['GET'])
@login_required(tipo='gestor')
def visualizar_estoque():
    produtos = Produto.query.all()
    return render_template('admin/estoque.html', produtos=produtos)


@bp_estoque.route('/estoque/movimentar', methods=['POST'])
@login_required(tipo='gestor')
def movimentar():
    produto_id = request.form['produto_id']
    tipo = request.form['tipo']  # entrada ou saida
    quantidade = float(request.form['quantidade'])

    nova = MovimentoEstoque(produto_id=produto_id, tipo=tipo, quantidade=quantidade)
    db.session.add(nova)

    produto = Produto.query.get(produto_id)
    if tipo == 'entrada':
        produto.estoque += quantidade
    elif tipo == 'saida':
        produto.estoque -= quantidade

    db.session.commit()

    registrar_acao('movimentação de estoque',
                   f'Estoque {tipo} de {quantidade} no produto #{produto_id} ({produto.nome})')

    flash('Estoque atualizado.', 'success')
    return redirect(url_for('estoque.visualizar_estoque'))
@bp_estoque.route('/estoque/historico/<int:produto_id>')
@login_required(tipo='gestor')
def historico(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    movimentacoes = MovimentoEstoque.query.filter_by(produto_id=produto_id)\
                                           .order_by(MovimentoEstoque.data.desc()).all()
    return render_template('admin/historico_estoque.html', produto=produto, movimentacoes=movimentacoes)

@bp_estoque.route('/estoque/historico/<int:produto_id>', methods=['GET', 'POST'])
@login_required(tipo='gestor')
def historico(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    # Filtros de data
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    query = MovimentoEstoque.query.filter_by(produto_id=produto_id)

    if data_inicio:
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(MovimentoEstoque.data >= inicio)

    if data_fim:
        fim = datetime.strptime(data_fim, '%Y-%m-%d')
        query = query.filter(MovimentoEstoque.data <= fim)

    movimentacoes = query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template('admin/historico_estoque.html', produto=produto, movimentacoes=movimentacoes, data_inicio=data_inicio, data_fim=data_fim)
@bp_estoque.route('/estoque/historico/<int:produto_id>/pdf')
@login_required(tipo='gestor')
def exportar_pdf(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    movimentacoes = MovimentoEstoque.query.filter_by(produto_id=produto_id)\
                                           .order_by(MovimentoEstoque.data.desc()).all()
    
    html = render_template('admin/exportar_pdf.html', produto=produto, movimentacoes=movimentacoes)
    pdf_file = HTML(string=html).write_pdf()
    
    return send_file(io.BytesIO(pdf_file), download_name=f"historico_{produto.nome}.pdf", as_attachment=True)
@bp_estoque.route('/estoque/historico/<int:produto_id>/excel')
@login_required(tipo='gestor')
def exportar_excel(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    movimentacoes = MovimentoEstoque.query.filter_by(produto_id=produto_id)\
                                           .order_by(MovimentoEstoque.data.desc()).all()
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet('Histórico')

    sheet.write(0, 0, 'Data')
    sheet.write(0, 1, 'Tipo')
    sheet.write(0, 2, 'Quantidade')

    for idx, m in enumerate(movimentacoes, start=1):
        sheet.write(idx, 0, m.data.strftime('%d/%m/%Y %H:%M'))
        sheet.write(idx, 1, m.tipo)
        sheet.write(idx, 2, m.quantidade)

    workbook.close()
    output.seek(0)
    
    return send_file(output, download_name=f"historico_{produto.nome}.xlsx", as_attachment=True)
