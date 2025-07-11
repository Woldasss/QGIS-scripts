from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsApplication

from .scripts import (
    EGIB_wlasnosci,
    delete_duplicates_by_fields,
    export_categories_to_separate_dxf_files,
    kateg_wlasnosci,
    label_enabler_disabler,
    lista_warstw_z_qgisa_na_pulpit,
)


class ScriptsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.menu = None

    def initGui(self):
        self.menu = QMenu("QGIS Scripts", self.iface.mainWindow())
        self.iface.pluginMenu().addMenu(self.menu)
        self.add_action("Toggle Labels", label_enabler_disabler.run)
        self.add_action("Delete Duplicates", delete_duplicates_by_fields.run)
        self.add_action("Export Categories to DXF", export_categories_to_separate_dxf_files.run)
        self.add_action("Assign Ownership", EGIB_wlasnosci.run)
        self.add_action("Classify Ownership", kateg_wlasnosci.run)
        self.add_action("List Layers", lista_warstw_z_qgisa_na_pulpit.run)

    def add_action(self, text, func):
        action = QAction(text, self.iface.mainWindow())
        action.triggered.connect(lambda: func(self.iface))
        self.menu.addAction(action)
        self.actions.append(action)

    def unload(self):
        for action in self.actions:
            self.menu.removeAction(action)
        self.iface.pluginMenu().removeAction(self.menu.menuAction())
        self.menu = None
        self.actions = []
