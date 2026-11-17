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
        print(f"❌ ERREUR : Le fichier {CSV_FILE} est introuvable.")
        return

    data = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        print(f"✅ Fichier CSV ouvert. {len(reader.fieldnames)} colonnes détectées.")
        
        for index, row in enumerate(reader):
            try:
                # Variables d'extraction par défaut
                etab = "Inconnu"
                ville = ""
                acad = ""
                filiere = "Formation"
                uid = str(index)
                cap = 0
                voeux = 0
                taux_acc = 0.0
                boursiers = 0.0
                
                mentions = {
                    "tb_fel": 0.0,
                    "tb": 0.0,
                    "b": 0.0,
                    "ab": 0.0,
                    "sans": 0.0
                }

                # Analyse dynamique et intelligente de chaque colonne de la ligne
                for k, v in row.items():
                    if v is None: continue
                    k_low = k.lower()
                    val_str = str(v).strip()

                    # Identifiants & Infos générales
                    if ('établissement' in k_low or 'etab' in k_low) and 'ville' not in k_low and 'acad' not in k_low and 'statut' not in k_low:
                        if etab == "Inconnu" or len(val_str) > len(etab): etab = val_str
                    elif 'ville' in k_low and not ville:
                        ville = val_str
                    elif 'académie' in k_low or 'academie' in k_low:
                        acad = val_str
                    elif 'filière' in k_low or 'filiere' in k_low:
                        if len(val_str) > len(filiere) or filiere == "Formation": filiere = val_str
                    elif 'uai' in k_low:
                        uid = val_str

                    # Indicateurs numériques
                    elif 'capacité' in k_low or 'cap_cap' in k_low:
                        cap = clean_num(val_str)
                    elif 'vœux' in k_low or 'voeux' in k_low or 'voe_tot' in k_low:
                        voeux = clean_num(val_str)
                    elif 'taux d’accès' in k_low or 'taux d\'accès' in k_low or 'taux_acc' in k_low:
                        taux_acc = clean_num(val_str, is_float=True)
                    elif 'boursier' in k_low and ('part' in k_low or '%' in k_low or 'pct' in k_low or 'taux' in k_low):
                        val_f = clean_num(val_str, is_float=True)
                        if val_f <= 100.0: boursiers = val_f

                    # Mentions au bac
                    elif 'félicitation' in k_low or 'fel' in k_low:
                        mentions["tb_fel"] = clean_num(val_str, is_float=True)
                    elif ('très bien' in k_low or 'tres bien' in k_low) and 'sans' not in k_low and 'félicitation' not in k_low:
                        mentions["tb"] = clean_num(val_str, is_float=True)
                    elif 'mention bien' in k_low or ' en b ' in k_low or k_low.endswith(' b '):
                        mentions["b"] = clean_num(val_str, is_float=True)
                    elif 'mention assez' in k_low or ' en ab ' in k_low:
                        mentions["ab"] = clean_num(val_str, is_float=True)
                    elif 'sans mention' in k_low:
                        mentions["sans"] = clean_num(val_str, is_float=True)

                item = {
                    "id": uid,
                    "etab": etab,
                    "ville": ville,
                    "acad": acad,
                    "filiere": filiere,
                    "cap": cap,
                    "voeux": voeux,
                    "taux_acc": taux_acc,
                    "boursiers": boursiers,
                    "mentions": mentions
                }

                # Trace ciblée pour vérifier l'ESTACA dans les logs de l'action
                if index < 2 or "estaca" in etab.lower():
                    print(f"🔍 TRACE [{index}] {etab} | Cap: {cap} | Vœux: {voeux} | Taux Acc: {taux_acc}% | Boursiers: {boursiers}% | Mentions: {mentions}")

                data.append(item)
            except Exception as e:
                continue

    print(f"📊 Total formations converties : {len(data)}")
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"✅ Fichier {JSON_OUTPUT} généré avec succès.")

if __name__ == '__main__':
    process_parcoursup()
