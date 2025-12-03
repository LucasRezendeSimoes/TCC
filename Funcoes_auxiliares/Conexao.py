# conexao.py
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import sys

# Definição dos dados de acesso do banco remoto
user = "Subweye"
password = "Nando-18"
cluster_url = "cluster0.alkn6hg.mongodb.net"
database_name = "simulacao_db"
collection_name = "leituras"

uri = f'mongodb+srv://{user}:{password}@{cluster_url}/?retryWrites=true&w=majority&appName=Cluster0'

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.list_database_names()
    print("✅ Conexão com MongoDB Atlas bem-sucedida!")
except ServerSelectionTimeoutError as err:
    print("Erro ao conectar no MongoDB Atlas:")
    print(err)
    sys.exit(1)

db = client[database_name]
colecao = db[collection_name]