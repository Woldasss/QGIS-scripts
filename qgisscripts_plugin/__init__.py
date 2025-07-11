def classFactory(iface):
    from .plugin import ScriptsPlugin
    return ScriptsPlugin(iface)
