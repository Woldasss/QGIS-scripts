from qgis.core import QgsProject, QgsField, QgsVectorDataProvider
from qgis.PyQt.QtCore import QVariant
import re


def extract_uuid(href):
    if not href:
        return None
    m = re.search(r"[0-9a-fA-F-]{36}", str(href))
    return m.group(0) if m else None


def run(iface):
    print("⏳ Rozpoczęcie przypisywania właścicieli i użytkowników wieczystych...")

    project = QgsProject.instance()
    parcel_layer = project.mapLayersByName("EGB_DzialkaEwidencyjna")
    owners_layer = project.mapLayersByName("EGB_UdzialWeWlasnosci")
    users_layer = project.mapLayersByName("EGB_UdzialWeWladaniu")
    inst_layer = project.mapLayersByName("EGB_Instytucja")
    person_layer = project.mapLayersByName("EGB_OsobaFizyczna")

    layers = {
        "EGB_DzialkaEwidencyjna": parcel_layer,
        "EGB_UdzialWeWlasnosci": owners_layer,
        "EGB_UdzialWeWladaniu": users_layer,
        "EGB_Instytucja": inst_layer,
        "EGB_OsobaFizyczna": person_layer,
    }
    for name, layer_list in layers.items():
        if not layer_list or len(layer_list) == 0:
            print(f"❗ Błąd: Warstwa '{name}' nie jest załadowana w projekcie.")
            raise Exception(f"Layer {name} not found")
        else:
            layers[name] = layer_list[0]

    parcel_layer = layers["EGB_DzialkaEwidencyjna"]
    owners_layer = layers["EGB_UdzialWeWlasnosci"]
    users_layer = layers["EGB_UdzialWeWladaniu"]
    inst_layer = layers["EGB_Instytucja"]
    person_layer = layers["EGB_OsobaFizyczna"]

    prov = parcel_layer.dataProvider()
    if prov.capabilities() & QgsVectorDataProvider.AddAttributes:
        new_fields = [
            QgsField("wlasciciel_nazwa", QVariant.String, len=255),
            QgsField("uzytkownik_nazwa", QVariant.String, len=255),
        ]
        if prov.addAttributes(new_fields):
            parcel_layer.updateFields()
            print("✅ Dodano pola 'wlasciciel_nazwa' i 'uzytkownik_nazwa' do warstwy działek.")
        else:
            print("❗ Błąd: Nie udało się dodać nowych pól do warstwy działek.")
    else:
        print("❗ Błąd: Dostawca danych warstwy działek nie obsługuje dodawania pól.")
        raise Exception("Cannot add fields to parcel layer")

    inst_name_by_uuid = {}
    for feat in inst_layer.getFeatures():
        uuid = feat["lokalnyId"] if "lokalnyId" in feat.fields().names() else extract_uuid(feat.attributes())
        full_name = None
        if "nazwaPelna" in feat.fields().names():
            full_name = feat["nazwaPelna"]
        if (not full_name or str(full_name).strip() == "") and "nazwaSkrocona" in feat.fields().names():
            full_name = feat["nazwaSkrocona"]
        if full_name is None:
            full_name = ""
        inst_name_by_uuid[str(uuid)] = str(full_name)

    person_name_by_uuid = {}
    for feat in person_layer.getFeatures():
        uuid = feat["lokalnyId"] if "lokalnyId" in feat.fields().names() else extract_uuid(feat.attributes())
        parts = []
        if "pierwszeImie" in feat.fields().names():
            val = feat["pierwszeImie"]
            if val:
                parts.append(str(val))
        if "drugieImie" in feat.fields().names():
            val = feat["drugieImie"]
            if val:
                parts.append(str(val))
        if "pierwszyCzlonNazwiska" in feat.fields().names():
            val = feat["pierwszyCzlonNazwiska"]
            if val:
                parts.append(str(val))
        if "drugiCzlonNazwiska" in feat.fields().names():
            val = feat["drugiCzlonNazwiska"]
            if val:
                parts.append(str(val))
        full_name = " ".join(parts)
        person_name_by_uuid[str(uuid)] = full_name

    print(
        f"Znaleziono {owners_layer.featureCount()} udziałów we własności oraz {users_layer.featureCount()} udziałów we władaniu."
    )

    owners_map = {}
    users_map = {}

    for feat in owners_layer.getFeatures():
        jrg_ref = (
            feat["JRG_href"]
            if "JRG_href" in feat.fields().names()
            else feat["JRG2_href"]
            if "JRG2_href" in feat.fields().names()
            else None
        )
        if not jrg_ref or str(jrg_ref).upper() == "NULL":
            continue
        name = ""
        if "instytucja1_href" in feat.fields().names() and feat["instytucja1_href"]:
            uuid = extract_uuid(feat["instytucja1_href"])
            name = inst_name_by_uuid.get(str(uuid), "")
            if name == "":
                print(f"⚠️ UWAGA: Nie znaleziono nazwy instytucji o UUID {uuid}")
        elif "osobaFizyczna_href" in feat.fields().names() and feat["osobaFizyczna_href"]:
            uuid = extract_uuid(feat["osobaFizyczna_href"])
            name = person_name_by_uuid.get(str(uuid), "")
            if name == "":
                print(f"⚠️ UWAGA: Nie znaleziono nazwy osoby o UUID {uuid}")
        else:
            print(f"⚠️ UWAGA: Udział (ID {feat.id()}) pominięty – nieobsługiwany typ podmiotu.")
            continue
        key = str(jrg_ref)
        if key not in owners_map:
            owners_map[key] = name
        else:
            if name not in owners_map[key]:
                owners_map[key] += ", " + name

    for feat in users_layer.getFeatures():
        jrg_ref = (
            feat["JRG_href"]
            if "JRG_href" in feat.fields().names()
            else feat["JRG2_href"]
            if "JRG2_href" in feat.fields().names()
            else None
        )
        if not jrg_ref or str(jrg_ref).upper() == "NULL":
            continue
        name = ""
        if "instytucja1_href" in feat.fields().names() and feat["instytucja1_href"]:
            uuid = extract_uuid(feat["instytucja1_href"])
            name = inst_name_by_uuid.get(str(uuid), "")
            if name == "":
                print(f"⚠️ UWAGA: Nie znaleziono nazwy instytucji (użytkownika) o UUID {uuid}")
        elif "osobaFizyczna_href" in feat.fields().names() and feat["osobaFizyczna_href"]:
            uuid = extract_uuid(feat["osobaFizyczna_href"])
            name = person_name_by_uuid.get(str(uuid), "")
            if name == "":
                print(f"⚠️ UWAGA: Nie znaleziono nazwy osoby (użytkownika) o UUID {uuid}")
        else:
            print(f"⚠️ UWAGA: Udział w władaniu (ID {feat.id()}) pominięty – nieobsługiwany typ podmiotu.")
            continue
        key = str(jrg_ref)
        if key not in users_map:
            users_map[key] = name
        else:
            if name not in users_map[key]:
                users_map[key] += ", " + name

    owner_idx = parcel_layer.fields().indexOf("wlasciciel_nazwa")
    user_idx = parcel_layer.fields().indexOf("uzytkownik_nazwa")
    total = parcel_layer.featureCount()
    count = 0
    attr_changes = {}
    for feat in parcel_layer.getFeatures():
        count += 1
        jrg_ref = feat["JRG2_href"]
        if not jrg_ref:
            continue
        jrg_key = str(jrg_ref)
        owner_names = owners_map.get(jrg_key, "")
        user_names = users_map.get(jrg_key, "")
        attr_changes[feat.id()] = {
            owner_idx: owner_names,
            user_idx: user_names,
        }
        if count % 1000 == 0:
            if not prov.changeAttributeValues(attr_changes):
                print(f"⚠️ UWAGA: Problem przy aktualizacji atrybutów dla części działek (do ID {feat.id()}).")
            attr_changes.clear()
            print(f"... przetworzono {count} / {total} działek ...")

    if attr_changes:
        if not prov.changeAttributeValues(attr_changes):
            print("⚠️ UWAGA: Problem przy końcowej aktualizacji atrybutów działek.")

    print("✅ Własność i użytkowanie wieczyste przypisane.")
