from pyvis.network import Network
import os
import csv

def gerar_grafo(numero_camera=None):
    try:
        if numero_camera:
            numero_camera = int(numero_camera)
    except:
        numero_camera = None

    # Criar rede
    net = Network(height="380px", width="50%", directed=False, bgcolor="#495057", font_color="white")

    # Lê cams.csv
    caminho_csv = os.path.join("Dados", "cams.csv")
    dados_cameras = {}
    if os.path.exists(caminho_csv):
        with open(caminho_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    numero = int(row['Número da camera'])
                    dados_cameras[numero] = row
                except:
                    continue

    # Se não achar o CSV, usa fallback simples
    if not dados_cameras:
        dados_cameras = {
            1: {"Estação": "Liberdade", "Linha": "Azul", "Tipo": "entrada", "Imagem default": ""},
            2: {"Estação": "Liberdade", "Linha": "Azul", "Tipo": "trajeto", "Imagem default": ""},
        }

    # Criar nós com tooltip (hover)
    for cam_num, cam_data in dados_cameras.items():
        estacao = cam_data.get("Estação", "Desconhecida")
        linha = cam_data.get("Linha", "Desconhecida")
        tipo = cam_data.get("Tipo", "Desconhecido")
        imagem = cam_data.get("Imagem default", "")

        # Tooltip em HTML
        title = f"Câmera {cam_num}\nEstação: {estacao}\nLinha: {linha}\nTipo: {tipo}"

        net.add_node(
            cam_num,
            label=f"Câmera {cam_num}",
            title=title,
            x=cam_num * 200 - 200,
            y=0,
            fixed=True,
            color="orange" if cam_num == numero_camera else "white",
            size=10 if cam_num == numero_camera else 5
        )

    # Arestas
    net.add_edge(1, 2, color="#C9C9C9")

    # Salvar HTML
    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")
    net.write_html(caminho_html, notebook=False)
    return caminho_html
