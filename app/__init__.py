#app/__init__.py

from flask import Flask
import os

app = Flask(__name__)
#Define o cmaminho para o banco de dados
# __file__ se refere a este aqruivo (__init__.py)
# os.path.dirname(__file__) retorna o diretório onde este arquivo está localizado
#os.path.join() monta o caminho de forma segura
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'academia.db')

# Importa as rotas depois de criar o 'app' para evitar importação circular



from app import routes
