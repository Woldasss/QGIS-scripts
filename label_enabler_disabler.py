# Customize this starter script by adding code
# to the run_script function. See the Help for
# complete information on how to create a script
# and use Script Runner.

""" Your Description of the script goes here """

# Some commonly used imports

def run_script(iface):
    layers = [layer for layer in QgsProject.instance().mapLayers().values() if hasattr(layer, 'labelsEnabled')]
    any_on = any(layer.labelsEnabled() for layer in layers)
    for layer in layers:
        layer.setLabelsEnabled(not any_on)
        layer.triggerRepaint()

