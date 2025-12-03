import os

# Lista de arquivos a serem lidos
arquivos = [
    "templates/index.html",
    "static/script.js",
    "static/styles.css",
    "app.py",
    "mapa.py",
    "relatorio.py",
    "Funcoes_auxiliares/conexao.py",
    "Funcoes_auxiliares/geraDadosMongo.py",
    "Funcoes_auxiliares/InputMongo.py",
    "Funcoes_auxiliares/OutputMongo.py",
    "cam_assets/cams.csv",
    "cam_assets/grafo.csv",
    "cam_assets/positions.csv"
]

# Nome do arquivo de saída
arquivo_saida = "saida.txt"

with open(arquivo_saida, "w", encoding="utf-8") as saida:
    for caminho in arquivos:
        if os.path.exists(caminho):
            saida.write(f"Nome do arquivo: {caminho}\n")
            saida.write("-" * 40 + "\n")
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
                saida.write(conteudo + "\n")
            saida.write("\n\n")  # Separador entre arquivos
        else:
            saida.write(f"Nome do arquivo: {caminho}\n")
            saida.write("Arquivo não encontrado.\n\n")

print(f"Conteúdo dos arquivos foi salvo em '{arquivo_saida}'.")