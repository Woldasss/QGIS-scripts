from qgis.core import QgsProject

output_path = "C:/Users/pwold/Desktop/lista_warstw.txt"

def run(iface):
    with open(output_path, "w", encoding="utf-8") as f:
        for layer in QgsProject.instance().mapLayers().values():
            f.write(f"{layer.name()} → {layer.source()}\n")
