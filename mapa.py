from pyvis.network import Network
import os

def gerar_grafo():
    net = Network(height="380px", width="50%", directed=False, bgcolor="#495057", font_color="white")

    # Vértices
    net.add_node(1, label="Câmera 1", x=0, y=0, fixed=True, color="white", size=5)
    net.add_node(2, label="Câmera 2", x=200, y=100, fixed=True, color="white", size=5)
    net.add_node(3, label="Câmera 3", x=400, y=0, fixed=True, color="white", size=5)

    # Arestas
    net.add_edge(1, 2)
    net.add_edge(1, 3)

    # Salvar em static/mapas/mapa.html
    pasta_saida = os.path.join("static", "mapas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_html = os.path.join(pasta_saida, "mapa.html")

    net.write_html(caminho_html, notebook=False)
    return caminho_html