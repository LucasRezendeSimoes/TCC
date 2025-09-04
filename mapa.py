from pyvis.network import Network
import os
import csv

def gerar_grafo(numero_camera=None):
    try:
        if numero_camera:
            numero_camera = int(numero_camera)
    except:
        numero_camera = None

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

    if not dados_cameras:
        dados_cameras = {
            1: {"Estação": "Liberdade", "Linha": "Azul", "Tipo": "entrada", "Imagem default": ""},
            2: {"Estação": "Liberdade", "Linha": "Azul", "Tipo": "trajeto", "Imagem default": ""},
        }

    for cam_num, cam_data in dados_cameras.items():
        estacao = cam_data.get("Estação", "Desconhecida")
        linha = cam_data.get("Linha", "Desconhecida")
        tipo = cam_data.get("Tipo", "Desconhecido")
        imagem = cam_data.get("Imagem default", "")

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

    net.add_edge(1, 2, color="#C9C9C9")

    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")
    net.write_html(caminho_html, notebook=False)

    # ✅ Adiciona legenda visual ao HTML
    _injetar_legenda_no_html(caminho_html)

    return caminho_html


def gerar_grafo_por_hash(lista_cameras):
    net = Network(height="380px", width="50%", directed=True, bgcolor="#495057", font_color="white")

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

    for cam_num, cam_data in dados_cameras.items():
        estacao = cam_data.get("Estação", "Desconhecida")
        linha = cam_data.get("Linha", "Desconhecida")
        tipo = cam_data.get("Tipo", "Desconhecido")

        title = f"Câmera {cam_num}\nEstação: {estacao}\nLinha: {linha}\nTipo: {tipo}"

        color = "red" if cam_num in lista_cameras else "white"
        size = 15 if cam_num in lista_cameras else 7

        net.add_node(
            cam_num,
            label=f"Câmera {cam_num}",
            title=title,
            color=color,
            size=size,
            x=cam_num * 200,
            y=0,
            fixed=True
        )

    for i in range(len(lista_cameras) - 1):
        origem = lista_cameras[i]
        destino = lista_cameras[i + 1]
        net.add_edge(origem, destino, color="yellow", width=3)

    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")
    net.write_html(caminho_html, notebook=False)

    # ✅ Adiciona legenda ao HTML
    _injetar_legenda_no_html(caminho_html)

    return caminho_html


# ------------------------------------------------------------------
# ✅ Função auxiliar para injetar legenda no HTML
def _injetar_legenda_no_html(caminho_html):
    if not os.path.exists(caminho_html):
        return

    with open(caminho_html, "r", encoding="utf-8") as f:
        conteudo = f.read()

    legenda_html = """
    <div style="
        position: absolute;
        top: 10px;
        left: 2px;
        background-color: #333333;
        color: white;
        padding: 10px;
        font-size: 10px;
        border-radius: 0px 0px 10px 0px;
        z-index: 9999;
        font-family: Arial, sans-serif;
        box-shadow: 0 0 5px rgba(0,0,0,0.3);
    ">
        <b>Legenda</b><br><br>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 3px; background-color: yellow; margin-right: 8px;"></div>
            <span> = Rota percorrida</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; background-color: red; border-radius: 50%; margin-right: 8px;"></div>
            <span> = Câmera percorrida</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; background-color: orange; border-radius: 50%; margin-right: 8px;"></div>
            <span> = Câmera pesquisada</span>
        </div>
    </div>
    """

    if "</body>" in conteudo:
        conteudo = conteudo.replace("</body>", legenda_html + "\n</body>")

        with open(caminho_html, "w", encoding="utf-8") as f:
            f.write(conteudo)

# ------------------------------------------------------------------
# Debug manual
if __name__ == "__main__":
    cameras_teste = [1, 2, 4, 5, 3]
    gerar_grafo_por_hash(cameras_teste)
    print("Mapa gerado com legenda em static/mapas/mapa.html")
