import threading
import time
import os
import pandas as pd
from bson.objectid import ObjectId
from Funcoes_auxiliares.Conexao import colecao

class OutputMongo(threading.Thread):
    def __init__(self, caminho_csv="Dados/mov_mongo_2025.csv", intervalo=10):
        super().__init__(daemon=True)
        self.caminho_csv = caminho_csv
        self.intervalo = intervalo
        self.ultimos_ids = set()

        # Cria pasta se não existir
        os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

        # Verifica existência e conteúdo do CSV
        if os.path.exists(self.caminho_csv):
            try:
                df = pd.read_csv(self.caminho_csv)
                if "_id" in df.columns:
                    self.ultimos_ids = set(df["_id"].tolist())
            except pd.errors.EmptyDataError:
                print("⚠️ Arquivo CSV existe mas está vazio. Cabeçalho será reescrito.")
                with open(self.caminho_csv, "w") as f:
                    f.write("hash,horario_primeira_aparicao,horario_ultima_aparicao,posicao_inicial,posicao_final,id_imagem,numero_camera,_id\n")
        else:
            with open(self.caminho_csv, "w") as f:
                f.write("hash,horario_primeira_aparicao,horario_ultima_aparicao,posicao_inicial,posicao_final,id_imagem,numero_camera,_id\n")

    def run(self):
        print("📥 OutputMongo iniciado...")

        while True:
            novos_registros = list(colecao.find({"_id": {"$nin": list(self.ultimos_ids)}}))
            if novos_registros:
                with open(self.caminho_csv, "a", encoding="utf-8") as f:
                    for doc in novos_registros:
                        linha = (
                            f"{doc['hash']},"
                            f"{doc['horario_primeira_aparicao']},"
                            f"{doc['horario_ultima_aparicao']},"
                            f"\"{doc['posicao_inicial']}\","
                            f"\"{doc['posicao_final']}\","
                            f"{doc['id_imagem']},"
                            f"{doc['numero_camera']},"
                            f"{doc['_id']}\n"
                        )
                        f.write(linha)
                        self.ultimos_ids.add(doc['_id'])
                print(f"✅ {len(novos_registros)} novos registros salvos no CSV.")
            else:
                print("Nenhum novo registro encontrado.")
            time.sleep(self.intervalo)