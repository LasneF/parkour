import csv
import json
import os

CSV_FILE = 'fr-esr-parcoursup.csv'
JSON_OUTPUT = 'data.json'

def find_field(row, possible_keys):
    """Cherche une clé exacte ou effectue une recherche partielle insensible à la casse"""
    for k in possible_keys:
        if k in row and row[k] is not None and str(row[k]).strip() != '':
            return row[k]
    # Recherche partielle par mot-clé dans les en-têtes
    for k in possible_keys:
        k_lower = k.lower()
        for rk in row.keys():
            if k_lower in rk.lower() and row[rk] is not None and str(row[rk]).strip() != '':
                return row[rk]
    return ''

def process_parcoursup():
    if not os.path.exists(CSV_FILE):
        print(f"Erreur : Le fichier {CSV_FILE} est introuvable dans le dépôt.")
        return

    data = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        print("Colonnes détectées dans le CSV :", reader.fieldnames)
        
        for index, row in enumerate(reader):
            try:
                # Extraction intelligente avec fallbacks larges
                etab = find_field(row, ['Établissement', 'g_ea_lib', 'etablissement']) or 'Établissement inconnu'
                ville = find_field(row, ['Ville de l\'établissement', 'ville_etab', 'ville']) or ''
                acad = find_field(row, ['Académie', 'academie_rectorat', 'academie']) or ''
                filiere = find_field(row, ['Filière de formation détaillée', 'fil_lib_precise', 'filiere', 'Filière de formation']) or 'Formation'
                uid = find_field(row, ['g_ea_uai', 'cod_uai', 'uai', 'Code UAI']) or str(index)

                def clean_int(val):
                    if not val: return 0
                    try:
                        # Nettoie les espaces insécables (\xa0), espaces normaux et virgules
                        s = str(val).replace('\xa0', '').replace(' ', '').replace(',', '.')
                        return int(float(s))
                    except:
                        return 0

                def clean_float(val):
                    if not val: return 0.0
                    try:
                        s = str(val).replace('\xa0', '').replace(' ', '').replace(',', '.')
                        return float(s)
                    except:
                        return 0.0

                item = {
                    "id": str(uid).strip(),
                    "etab": str(etab).strip(),
                    "ville": str(ville).strip(),
                    "acad": str(acad).strip(),
                    "filiere": str(filiere).strip(),
                    "cap": clean_int(find_field(row, ['Capacité d\'accueil', 'cap_cap', 'Capacité'])),
                    "voeux": clean_int(find_field(row, ['Nombre total de vœux', 'voe_tot', 'vœux'])),
                    "taux_acc": clean_float(find_field(row, ['Taux d\'accès', 'taux_acc'])),
                    "boursiers": clean_float(find_field(row, ['boursiers', 'pct_boursiers'])),
                    "mentions": {
                        "tb_fel": clean_float(find_field(row, ['TB avec félicitations', 'pct_tb_fel'])),
                        "tb": clean_float(find_field(row, ['TB sans félicitations', 'pct_tb'])),
                        "b": clean_float(find_field(row, ['en B', 'pct_b'])),
                        "ab": clean_float(find_field(row, ['en AB', 'pct_ab'])),
                        "sans": clean_float(find_field(row, ['sans mention', 'pct_sans_ment']))
                    }
                }
                data.append(item)
            except Exception:
                continue

    print(f"Total formations extraites avec succès : {len(data)}")
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"Succès : {JSON_OUTPUT} généré.")

if __name__ == '__main__':
    process_parcoursup()
