# InputMongo.py
import threading
import time
from Funcoes_auxiliares.Conexao import colecao
from Funcoes_auxiliares.geraDadosMongo import gerar_movimentacao_realista

class InputMongo(threading.Thread):
    def __init__(self, num_hashes=10, intervalo=5, lote_tamanho=20):
        super().__init__(daemon=True)
        self.num_hashes = num_hashes
        self.intervalo = intervalo
        self.lote_tamanho = lote_tamanho

    def run(self):
        print("InputMongo iniciado...")
        while True:
            df = gerar_movimentacao_realista(num_hashes=self.num_hashes, salvar_csv=False)
            total_registros = len(df)
            posicao = 0

            while posicao < total_registros:
                fim = min(posicao + self.lote_tamanho, total_registros)
                lote_df = df.iloc[posicao:fim]
                documentos = lote_df.to_dict(orient="records")

                try:
                    colecao.insert_many(documentos)
                    print(f"📤 Inserido {len(documentos)} registros (de {posicao} a {fim - 1})")
                except Exception as e:
                    print("❌ Erro ao inserir no MongoDB:", e)

                posicao = fim
                time.sleep(self.intervalo)