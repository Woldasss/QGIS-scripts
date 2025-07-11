from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsVectorLayer,
    QgsWkbTypes
)
from qgis.PyQt.QtWidgets import QInputDialog

# 1. Grab the active layer
layer = iface.activeLayer()
if not layer:
    raise Exception("Select a layer first")

# 2. Ask for the grouping (dedupe) field
fields = [f.name() for f in layer.fields()]
group_field, ok = QInputDialog.getItem(
    None,
    "Duplicate grouping field",
    "Group features by (duplicates share the same value):",
    fields,
    0,
    False
)
if not ok:
    raise Exception("Canceled")

# 3. Ask for the “pick” field
pick_field, ok = QInputDialog.getItem(
    None,
    "Priority pick field",
    "Which field’s value should determine which feature to keep?",
    fields,
    0,
    False
)
if not ok:
    raise Exception("Canceled")

# 4. Gather unique values of that pick-field
values = sorted({ feat[pick_field] for feat in layer.getFeatures() })
# Convert to strings in case of numeric types
values_str = [str(v) for v in values]

# 5. Prompt which value to prefer
chosen_str, ok = QInputDialog.getItem(
    None,
    f"Choose preferred {pick_field} value",
    f"Features with {pick_field} = … will be kept first:",
    values_str,
    0,
    False
)
if not ok:
    raise Exception("Canceled")
# Map back to original type
idx = values_str.index(chosen_str)
preferred_value = values[idx]

# 6. Prepare two memory layers (same geometry + schema)
geom = layer.wkbType()
crs  = layer.crs().authid()
uri  = f"{QgsWkbTypes.displayString(geom)}?crs={crs}"

unique_layer = QgsVectorLayer(uri, "unique_by_priority", "memory")
dups_layer   = QgsVectorLayer(uri, "duplicates",          "memory")

dp_u = unique_layer.dataProvider()
dp_d = dups_layer.dataProvider()
dp_u.addAttributes(layer.fields())
dp_d.addAttributes(layer.fields())
unique_layer.updateFields()
dups_layer.updateFields()

# 7. Group features and apply the preference rule
#    build a dict: key → list of features
groups = {}
for feat in layer.getFeatures():
    key = feat[group_field]
    groups.setdefault(key, []).append(feat)

# 8. For each group, pick one to unique_layer and the rest to dups_layer
for feats in groups.values():
    # find all in this group matching the preferred value
    preferred_feats = [f for f in feats if f[pick_field] == preferred_value]
    if preferred_feats:
        keeper = preferred_feats[0]
    else:
        keeper = feats[0]
    # add the keeper
    dp_u.addFeatures([QgsFeature(keeper)])
    # everything else goes to duplicates
    for f in feats:
        if f.id() != keeper.id():
            dp_d.addFeatures([QgsFeature(f)])

# 9. Add result layers back into the map
QgsProject.instance().addMapLayer(unique_layer)
QgsProject.instance().addMapLayer(dups_layer)
