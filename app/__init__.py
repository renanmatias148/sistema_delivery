# app/__init__.py

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Extensões fora da função para evitar import circular
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Carregar variáveis de ambiente
    load_dotenv()

    # Configurações gerais
    app.secret_key = 'meu_segredo_super_secreto'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///delivery.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações do Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    # Inicializa as extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Rota de teste
    @app.route('/')
    def home():
        return render_template('dashboard.html')

    # Importa e registra Blueprints
    from app.routes.produtos import bp_produto
    from app.routes.categorias import bp_categoria
    from app.routes.ingredientes import bp_ingrediente
    from app.routes.adicionais import bp_adicional
    from app.routes.ficha_tecnica import bp_ficha_tecnica
    from app.routes.vendas import bp_venda
    from app.routes.relatorio import bp_relatorio
    from app.routes.financeiro import bp_financeiro
    from app.routes.contas import bp_conta
    from app.routes.site import bp_site
    from app.routes.admin import bp_admin
    from app.routes.notificacoes import bp_notificacoes
    from app.routes.cliente import bp_cliente
    from app.routes.caixa import bp_caixa
    from app.routes.estoque import bp_estoque
    from app.routes.funcionario import bp_func
    from app.routes.zonas import bp_zonas

    app.register_blueprint(bp_produto)
    app.register_blueprint(bp_categoria)
    app.register_blueprint(bp_ingrediente)
    app.register_blueprint(bp_adicional)
    app.register_blueprint(bp_ficha_tecnica)
    app.register_blueprint(bp_venda)
    app.register_blueprint(bp_relatorio)
    app.register_blueprint(bp_financeiro)
    app.register_blueprint(bp_conta)
    app.register_blueprint(bp_site)
    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_notificacoes)
    app.register_blueprint(bp_cliente)
    app.register_blueprint(bp_caixa)
    app.register_blueprint(bp_estoque)
    app.register_blueprint(bp_func)
    app.register_blueprint(bp_zonas)

    return app
