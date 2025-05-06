from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, ZonaEntrega
import json

bp_zonas = Blueprint('zonas', __name__)

@bp_zonas.route('/admin/zonas', methods=['GET', 'POST'])
def zonas_entrega():
    if request.method == 'POST':
        nome = request.form['nome']
        taxa = float(request.form['taxa'])
        coords = request.form['coordenadas']
        zona = ZonaEntrega(nome=nome, taxa=taxa, coordenadas=coords)
        db.session.add(zona)
        db.session.commit()
        flash('Zona de entrega salva.', 'success')
        return redirect(url_for('zonas.zonas_entrega'))

    zonas = ZonaEntrega.query.all()
    return render_template('admin/zonas.html', zonas=zonas)
