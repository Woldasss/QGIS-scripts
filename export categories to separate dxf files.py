import os

# Input settings
layer_name = "inwestycje_linia_M4"
output_dir = r"C:\Users\pwold\OneDrive\PRACOWNIA PRZESTRZENI\ANALIZY\METRO 4\07 GIS\Wektory\EXPORT"
field_name = "KATEGORIA"

# Get layer safely
layers = QgsProject.instance().mapLayersByName(layer_name)
if not layers:
    raise Exception(f"Layer '{layer_name}' not found.")
input_layer = layers[0]

# Get unique values
field_index = input_layer.fields().indexFromName(field_name)
if field_index == -1:
    raise Exception(f"Field '{field_name}' not found.")

unique_values = input_layer.uniqueValues(field_index)

for value in unique_values:
    # Filter features by value
    expression = f'"{field_name}" = \'{value}\''
    request = QgsFeatureRequest().setFilterExpression(expression)
    feats = list(input_layer.getFeatures(request))

    if not feats:
        print(f"No features for '{value}', skipping.")
        continue

    # Create memory layer with NO attribute fields
    geometry_type = input_layer.wkbType()
    crs = input_layer.crs().authid()
    safe_layer_name = str(value).replace("/", "_").replace("\\", "_").replace(":", "_")
    mem_layer = QgsVectorLayer(f"{QgsWkbTypes.displayString(geometry_type)}?crs={crs}", safe_layer_name, "memory")
    mem_provider = mem_layer.dataProvider()
    mem_provider.addFeatures(feats)

    # DXF output path
    dxf_path = os.path.join(output_dir, f"{safe_layer_name}.dxf")

    # Write DXF
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "DXF"
    options.layerName = safe_layer_name  # use as DXF layer name
    result = QgsVectorFileWriter.writeAsVectorFormatV3(mem_layer, dxf_path, QgsProject.instance().transformContext(), options)

    if result[0] != QgsVectorFileWriter.NoError:
        print(f"Error exporting {value}: {result[1]}")
    else:
        print(f"Exported: {dxf_path}")
