from flask import Blueprint, render_template
from app.models.ingrediente import Ingrediente

bp_relatorio = Blueprint('relatorio', __name__, url_prefix='/relatorio')

@bp_relatorio.route('/estoque', methods=['GET'])
def relatorio_estoque():
    ingredientes = Ingrediente.query.all()
    return render_template('relatorio_estoque.html', ingredientes=ingredientes)
