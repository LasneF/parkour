import csv
import json
import os

CSV_FILE = 'fr-esr-parcoursup.csv'
JSON_OUTPUT = 'data.json'

def process_parcoursup():
    if not os.path.exists(CSV_FILE):
        print(f"Erreur : Le fichier {CSV_FILE} est introuvable dans le dépôt.")
        return

    data = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for index, row in enumerate(reader):
            try:
                etab = ''
                ville = ''
                acad = ''
                filiere = ''
                uid = str(index)

                for k, v in row.items():
                    if not v: continue
                    k_lower = k.lower()
                    if 'établissement' in k_lower and not etab: etab = v
                    elif 'ville' in k_lower and not ville: ville = v
                    elif 'académie' in k_lower and not acad: acad = v
                    elif 'filière' in k_lower and not filiere: filiere = v
                    elif 'uai' in k_lower and not uid: uid = v

                def clean_float(val):
                    if val is None: return 0.0
                    try:
                        s = str(val).replace('\xa0', '').replace(' ', '').replace(',', '.').replace('%', '').strip()
                        return float(s)
                    except:
                        return 0.0

                def clean_int(val):
                    if val is None: return 0
                    try:
                        s = str(val).replace('\xa0', '').replace(' ', '').replace(',', '.').strip()
                        return int(float(s))
                    except:
                        return 0

                bourse_val = 0.0
                tb_fel = 0.0
                tb = 0.0
                b = 0.0
                ab = 0.0
                sans = 0.0

                for k, v in row.items():
                    if not v: continue
                    k_low = k.lower()
                    
                    if 'boursier' in k_low and ('part' in k_low or 'taux' in k_low or '%' in k_low or 'pct' in k_low):
                        val_f = clean_float(v)
                        if val_f <= 100.0:
                            bourse_val = val_f

                    if 'félicitation' in k_low:
                        tb_fel = clean_float(v)
                    elif 'très bien' in k_low or 'tres bien' in k_low:
                        if 'sans' not in k_low:
                            tb = clean_float(v)
                    elif 'mention bien' in k_low or ' en b ' in k_low or k_low.endswith(' b '):
                        b = clean_float(v)
                    elif 'mention assez' in k_low or ' en ab ' in k_low:
                        ab = clean_float(v)
                    elif 'sans mention' in k_low:
                        sans = clean_float(v)

                item = {
                    "id": str(uid).strip(),
                    "etab": str(etab).strip() or "Établissement inconnu",
                    "ville": str(ville).strip(),
                    "acad": str(acad).strip(),
                    "filiere": str(filiere).strip() or "Formation",
                    "cap": clean_int(row.get('Capacité d\'accueil de la formation') or row.get('cap_cap')),
                    "voeux": clean_int(row.get('Nombre total de vœux formulés') or row.get('voe_tot')),
                    "taux_acc": clean_float(row.get('Taux d\'accès') or row.get('taux_acc')),
                    "boursiers": bourse_val,
                    "mentions": {
                        "tb_fel": tb_fel,
                        "tb": tb,
                        "b": b,
                        "ab": ab,
                        "sans": sans
                    }
                }

                # --- TRACE CIBLÉE SUR L'ESTACA ---
                if "estaca" in item["etab"].lower():
                    print("--- TRACE RECORD ESTACA TROUVÉ ---")
                    print(json.dumps(item, indent=2, ensure_ascii=False))
                    print("-----------------------------------")

                data.append(item)
            except Exception:
                continue

    print(f"Total formations extraites : {len(data)}")
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print("Génération de data.json terminée.")

if __name__ == '__main__':
    process_parcoursup()
