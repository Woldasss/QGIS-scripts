with open("C:/Users/pwold/Desktop/lista_warstw.txt", "w") as f:
    for layer in QgsProject.instance().mapLayers().values():
        f.write(f"{layer.name()} → {layer.source()}\n")
