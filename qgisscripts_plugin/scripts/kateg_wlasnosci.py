from qgis.core import QgsProject, QgsField, edit
from qgis.PyQt.QtCore import QVariant


dzialki_warstwa_nazwa = 'EGB_DzialkaEwidencyjna'
jednostki_warstwa_nazwa = 'EGB_JednostkaRejestrowaGruntow'
wyjatki_warstwa_nazwa = 'wyjatki'


def run(iface):
    print("Warstwy w projekcie QGIS:")
    for lyr in QgsProject.instance().mapLayers().values():
        print('-', lyr.name())

    dzialki_layer = QgsProject.instance().mapLayersByName(dzialki_warstwa_nazwa)
    if not dzialki_layer:
        raise Exception(f"Nie znaleziono warstwy '{dzialki_warstwa_nazwa}' – sprawdź pisownię!")
    dzialki_layer = dzialki_layer[0]

    rej_layer = QgsProject.instance().mapLayersByName(jednostki_warstwa_nazwa)
    if not rej_layer:
        raise Exception(f"Nie znaleziono warstwy '{jednostki_warstwa_nazwa}' – sprawdź pisownię!")
    rej_layer = rej_layer[0]

    wyjatki_layer = QgsProject.instance().mapLayersByName(wyjatki_warstwa_nazwa)
    wyjatki_layer = wyjatki_layer[0] if wyjatki_layer else None

    if dzialki_layer.fields().indexFromName("kategoria_wlasnosci") == -1:
        dzialki_layer.dataProvider().addAttributes([QgsField("kategoria_wlasnosci", QVariant.String, len=50)])
        dzialki_layer.updateFields()
        print("Dodano pole 'kategoria_wlasnosci' do warstwy działek.")

    wyjatki_dict = {}
    if wyjatki_layer:
        for f in wyjatki_layer.getFeatures():
            parcel_id = f["idDzialki"] if "idDzialki" in f.fields().names() else f["gml_id"]
            kat = f["kategoria_wlasnosci"] if "kategoria_wlasnosci" in f.fields().names() else None
            if parcel_id and kat:
                wyjatki_dict[str(parcel_id).strip()] = str(kat).strip()
        print(f"Wczytano {len(wyjatki_dict)} wyjątków.")

    with edit(dzialki_layer):
        for feat in dzialki_layer.getFeatures():
            dzialka_id = feat["idDzialki"] if "idDzialki" in feat.fields().names() else feat["gml_id"]
            if dzialka_id and str(dzialka_id) in wyjatki_dict:
                feat["kategoria_wlasnosci"] = wyjatki_dict[str(dzialka_id)]
                dzialki_layer.updateFeature(feat)
                continue

            user_name = feat["uzytkownik_nazwa"] if "uzytkownik_nazwa" in feat.fields().names() else None
            kat = "Pozostałe"
            if user_name and user_name.strip():
                uname = user_name.strip().upper()
                if "SKARB PAŃSTWA" in uname:
                    kat = "Skarb Państwa"
                elif "WARSZAWA" in uname or "MIEJSKI" in uname or "M.ST." in uname:
                    kat = "Miasto Warszawa"
                elif ";" in user_name or "," in user_name:
                    kat = "Własność mieszana"
                else:
                    kat = "Użytkowanie wieczyste"
            feat["kategoria_wlasnosci"] = kat
            dzialki_layer.updateFeature(feat)

    print("✅ Przypisano kategorie własności. Sprawdź atrybuty warstwy działek!")
