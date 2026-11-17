import csv
import json
import os

# Mise à jour avec le nom exact du fichier officiel
CSV_FILE = 'fr-esr-parcoursup.csv'
JSON_OUTPUT = 'data.json'

def process_parcoursup():
    data = []
    if not os.path.exists(CSV_FILE):
        print(f"Erreur : Le fichier {CSV_FILE} est introuvable dans le dépôt.")
        return

    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            try:
                etab = row.get('Établissement', row.get('g_ea_lib', 'Inconnu'))
                ville = row.get('Ville de l\'établissement', row.get('ville_etab', ''))
                acad = row.get('Académie', row.get('academie_rectorat', ''))
                filiere = row.get('Filière de formation détaillée', row.get('fil_lib_precise', ''))
                
                def clean_int(val):
                    try: return int(val.replace(',', '.'))
                    except: return 0

                def clean_float(val):
                    try: return float(val.replace(',', '.'))
                    except: return 0.0

                item = {
                    "id": row.get('g_ຖ_uai', row.get('cod_uai', str(len(data)))),
                    "etab": etab.strip(),
                    "ville": ville.strip(),
                    "acad": acad.strip(),
                    "filiere": filiere.strip(),
                    "cap": clean_int(row.get('Capacité d\'accueil de la formation', row.get('cap_cap', '0'))),
                    "voeux": clean_int(row.get('Nombre total de vœux formulés', row.get('voe_tot', '0'))),
                    "taux_acc": clean_float(row.get('Taux d\'accès', row.get('taux_acc', '0'))),
                    "boursiers": clean_float(row.get('Part des boursiers du secondaire (en %)', row.get('pct_boursiers', '0'))),
                    "mentions": {
                        "tb_fel": clean_float(row.get('Part des ad. bacheliers généraux en TB avec félicitations', '0')),
                        "tb": clean_float(row.get('Part des ad. bacheliers généraux en TB sans félicitations', row.get('pct_tb', '0'))),
                        "b": clean_float(row.get('Part des ad. bacheliers généraux en B', row.get('pct_b', '0'))),
                        "ab": clean_float(row.get('Part des ad. bacheliers généraux en AB', row.get('pct_ab', '0'))),
                        "sans": clean_float(row.get('Part des ad. bacheliers généraux sans mention', row.get('pct_sans_ment', '0')))
                    }
                }
                data.append(item)
            except Exception:
                continue

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"Succès : {len(data)} formations exportées vers {JSON_OUTPUT}.")

if __name__ == '__main__':
    process_parcoursup()
