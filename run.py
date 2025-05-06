# run.py
from app import create_app  # Importa a função que cria o app Flask

app = create_app()  # Chama a função para configurar tudo

if __name__ == '__main__':
    app.run(debug=True)  # Roda o servidor Flask
