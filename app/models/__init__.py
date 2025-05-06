from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.adicional import Adicional
from app.models.ficha_tecnica import FichaTecnica  # ✅ NOVO
from app.models.financeiro import Financeiro
from app.models.conta import Conta
from app.models.pedido import Pedido, ItemPedido
from app.models.usuario import Usuario
from .estoque import MovimentoEstoque
from .zonaentrega import ZonaEntrega