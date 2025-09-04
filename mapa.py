from pyvis.network import Network
import os

def gerar_grafo(numero_camera=None):
    try:
        if numero_camera:
            numero_camera = int(numero_camera)
    except:
        numero_camera = None

    net = Network(height="380px", width="50%", directed=False, bgcolor="#495057", font_color="white")

    cameras = [
        (1, "Câmera 1"),
        (2, "Câmera 2"),
        (3, "Câmera 3"),
    ]

    for cam_num, cam_label in cameras:
        if numero_camera == cam_num:
            net.add_node(cam_num, label=cam_label, x=cam_num*200 - 200, y=0, fixed=True, color="orange", size=10)
        else:
            net.add_node(cam_num, label=cam_label, x=cam_num*200 - 200, y=0, fixed=True, color="white", size=5)

    # Define arestas com cor neutra para não destacar
    net.add_edge(1, 2, color="#C9C9C9")
    net.add_edge(1, 3, color="#C9C9C9")

    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")

    net.write_html(caminho_html, notebook=False)
    return caminho_html
