from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtWidgets import QInputDialog


def run(iface):
    layer = iface.activeLayer()
    if not layer:
        raise Exception("Select a layer first")

    fields = [f.name() for f in layer.fields()]
    group_field, ok = QInputDialog.getItem(
        None,
        "Duplicate grouping field",
        "Group features by (duplicates share the same value):",
        fields,
        0,
        False,
    )
    if not ok:
        raise Exception("Canceled")

    pick_field, ok = QInputDialog.getItem(
        None,
        "Priority pick field",
        "Which field’s value should determine which feature to keep?",
        fields,
        0,
        False,
    )
    if not ok:
        raise Exception("Canceled")

    values = sorted({feat[pick_field] for feat in layer.getFeatures()})
    values_str = [str(v) for v in values]

    chosen_str, ok = QInputDialog.getItem(
        None,
        f"Choose preferred {pick_field} value",
        f"Features with {pick_field} = … will be kept first:",
        values_str,
        0,
        False,
    )
    if not ok:
        raise Exception("Canceled")
    idx = values_str.index(chosen_str)
    preferred_value = values[idx]

    geom = layer.wkbType()
    crs = layer.crs().authid()
    uri = f"{QgsWkbTypes.displayString(geom)}?crs={crs}"

    unique_layer = QgsVectorLayer(uri, "unique_by_priority", "memory")
    dups_layer = QgsVectorLayer(uri, "duplicates", "memory")

    dp_u = unique_layer.dataProvider()
    dp_d = dups_layer.dataProvider()
    dp_u.addAttributes(layer.fields())
    dp_d.addAttributes(layer.fields())
    unique_layer.updateFields()
    dups_layer.updateFields()

    groups = {}
    for feat in layer.getFeatures():
        key = feat[group_field]
        groups.setdefault(key, []).append(feat)

    for feats in groups.values():
        preferred_feats = [f for f in feats if f[pick_field] == preferred_value]
        if preferred_feats:
            keeper = preferred_feats[0]
        else:
            keeper = feats[0]
        dp_u.addFeatures([QgsFeature(keeper)])
        for f in feats:
            if f.id() != keeper.id():
                dp_d.addFeatures([QgsFeature(f)])

    QgsProject.instance().addMapLayer(unique_layer)
    QgsProject.instance().addMapLayer(dups_layer)
