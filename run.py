import os
from app import create_app

# Obter o ambiente do sistema operacional, com 'production' como padrão.
flask_env = os.getenv('FLASK_ENV', 'production')

# Criar a instância da aplicação Flask.
# O Gunicorn procurará por esta variável 'app'.
app = create_app(flask_env)