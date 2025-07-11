from qgis.core import QgsProject

def run(iface):
    layers = [layer for layer in QgsProject.instance().mapLayers().values() if hasattr(layer, 'labelsEnabled')]
    any_on = any(layer.labelsEnabled() for layer in layers)
    for layer in layers:
        layer.setLabelsEnabled(not any_on)
        layer.triggerRepaint()
