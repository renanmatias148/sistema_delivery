from app import create_app
from app.models import db, produto, categoria, ingrediente, adicional  # importe seus modelos aqui

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")
