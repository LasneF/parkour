import csv
import json
import os

CSV_FILE = 'fr-esr-parcoursup.csv'
JSON_OUTPUT = 'data.json'

def clean_num(val, is_float=False):
    if not val:
        return 0.0 if is_float else 0
    try:
        s = str(val).replace('\xa0', '').replace(' ', '').replace(',', '.').replace('%', '').strip()
        return float(s) if is_float else int(float(s))
    except:
        return 0.0 if is_float else 0

def process_parcoursup():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"❌ ERREUR : Le fichier {CSV_FILE} est introuvable.")

    data = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        print(f"✅ Fichier CSV ouvert. {len(reader.fieldnames)} colonnes détectées.")
        
        for index, row in enumerate(reader):
            try:
                # Extraction propre basée sur les vrais libellés OpenDataSoft
                etab = str(row.get('Établissement') or row.get('g_ea_lib') or 'Inconnu').strip()
                ville = str(row.get('Ville de l\'établissement') or row.get('ville_etab') or '').strip()
                # Évite d'afficher un code numérique (ex: 90.0) si c'est le département
                if ville.replace('.', '').isdigit():
                    ville = str(row.get('Département de l’établissement') or '').strip()
                
                acad = str(row.get('Académie de l’établissement') or row.get('academie_rectorat') or '').strip()
                filiere = str(row.get('Filière de formation') or row.get('fil_lib_precise') or 'Formation').strip()
                uid = str(row.get('Code UAI de l\'établissement') or row.get('g_ea_uai') or index)

                # Capacité et vœux ciblés précisément
                cap = clean_num(row.get('Capacité d\'accueil de la formation') or row.get('cap_cap'))
                voeux = clean_num(row.get('Nombre total de vœux formulés') or row.get('voe_tot'))
                taux_acc = clean_num(row.get('Taux d’accès') or row.get('taux_acc'), is_float=True)
                
                # Boursiers
                boursiers = 0.0
                for k, v in row.items():
                    if 'boursier' in k.lower() and v:
                        val_f = clean_num(v, is_float=True)
                        if val_f <= 100.0:
                            boursiers = val_f
                            break

                mentions = {"tb_fel": 0.0, "tb": 0.0, "b": 0.0, "ab": 0.0, "sans": 0.0}
                for k, v in row.items():
                    if not v: continue
                    k_low = k.lower()
                    if 'félicitation' in k_low: mentions["tb_fel"] = clean_num(v, is_float=True)
                    elif ('très bien' in k_low or 'tres bien' in k_low) and 'sans' not in k_low: mentions["tb"] = clean_num(v, is_float=True)
                    elif 'mention bien' in k_low or ' en b ' in k_low: mentions["b"] = clean_num(v, is_float=True)
                    elif 'mention assez' in k_low or ' en ab ' in k_low: mentions["ab"] = clean_num(v, is_float=True)
                    elif 'sans mention' in k_low: mentions["sans"] = clean_num(v, is_float=True)

                item = {
                    "id": uid, "etab": etab, "ville": ville, "acad": acad, "filiere": filiere,
                    "cap": cap, "voeux": voeux, "taux_acc": taux_acc, "boursiers": boursiers, "mentions": mentions
                }
                data.append(item)
            except Exception:
                continue

    # --- TEST UNITAIRE DE VALIDATION (CI/CD Safety Guard) ---
    print(f"📊 Total formations converties : {len(data)}")
    if len(data) == 0:
        raise ValueError("❌ ERREUR TEST UNITAIRE : Aucune formation extraite du CSV !")
    
    total_cap = sum(item["cap"] for item in data)
    print(f"🔍 Somme totale des capacités d'accueil : {total_cap}")
    if total_cap < 1000:
        raise ValueError(f"❌ ERREUR TEST UNITAIRE : Capacité totale anormale ({total_cap}). L'extraction des capacités a échoué.")

    print("✅ TEST UNITAIRE VALIDÉ : Les données sont cohérentes.")

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"✅ Fichier {JSON_OUTPUT} généré avec succès.")

if __name__ == '__main__':
    process_parcoursup()
