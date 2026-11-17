import csv
import json
import os

CSV_FILE = 'fr-esr-parcoursup.csv'
JSON_OUTPUT = 'data.json'

def clean_num(val, is_float=False):
    if not val:
        return 0.0 if is_float else 0
    try:
        s = str(val).replace('\xa0', '', ).replace(' ', '').replace(',', '.').replace('%', '').strip()
        return float(s) if is_float else int(float(s))
    except Exception as e:
        return 0.0 if is_float else 0

def process_parcoursup():
    if not os.path.exists(CSV_FILE):
        print(f"❌ ERREUR : Le fichier {CSV_FILE} est introuvable dans le dépôt.")
        return

    data = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        print(f"✅ Fichier CSV ouvert avec succès.")
        print(f"📋 Colonnes détectées dans le CSV ({len(reader.fieldnames)} colonnes) :")
        print(reader.fieldnames[:10], "... (et autres)")
        
        for index, row in enumerate(reader):
            try:
                item = {
                    "id": str(row.get('g_ea_uai') or row.get('cod_uai') or index),
                    "etab": str(row.get('Établissement') or row.get('g_ea_lib') or 'Inconnu').strip(),
                    "ville": str(row.get('Ville de l\'établissement') or row.get('ville_etab') or '').strip(),
                    "acad": str(row.get('Académie') or row.get('academie_rectorat') or '').strip(),
                    "filiere": str(row.get('Filière de formation détaillée') or row.get('fil_lib_precise') or 'Formation').strip(),
                    "cap": clean_num(row.get('Capacité d\'accueil de la formation') or row.get('cap_cap')),
                    "voeux": clean_num(row.get('Nombre total de vœux formulés') or row.get('voe_tot')),
                    "taux_acc": clean_num(row.get('Taux d\'accès') or row.get('taux_acc'), is_float=True),
                    "boursiers": clean_num(row.get('Part des boursiers du secondaire (en %)') or row.get('pct_boursiers'), is_float=True),
                    "mentions": {
                        "tb_fel": clean_num(row.get('Part des ad. bacheliers généraux en TB avec félicitations') or row.get('pct_tb_fel'), is_float=True),
                        "tb": clean_num(row.get('Part des ad. bacheliers généraux en TB sans félicitations') or row.get('pct_tb'), is_float=True),
                        "b": clean_num(row.get('Part des ad. bacheliers généraux en B') or row.get('pct_b'), is_float=True),
                        "ab": clean_num(row.get('Part des ad. bacheliers généraux en AB') or row.get('pct_ab'), is_float=True),
                        "sans": clean_num(row.get('Part des ad. bacheliers généraux sans mention') or row.get('pct_sans_ment'), is_float=True)
                    }
                }
                
                # Trace ciblée sur les 2 premiers items ou sur l'ESTACA pour vérifier
                if index < 2 or "estaca" in item["etab"].lower():
                    print(f"🔍 TRACE ITEM [{index}] : {item['etab']} | Cap: {item['cap']} | Boursiers: {item['boursiers']}% | Mentions: {item['mentions']}")

                data.append(item)
            except Exception as e:
                print(f"⚠️ Erreur ligne {index}: {e}")
                continue

    print(f"📊 Total formations converties avec succès : {len(data)}")
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"✅ Fichier {JSON_OUTPUT} généré avec succès.")

if __name__ == '__main__':
    process_parcoursup()
