import csv
import json
import math
from pathlib import Path
from urllib.parse import urlsplit


ROOT_DIR = Path(__file__).resolve().parent
CSV_FILE = ROOT_DIR / "fr-esr-parcoursup.csv"
JSON_OUTPUT = ROOT_DIR / "data.json"
THRESHOLD_SIZE = 10

FILIERE_GROUP_COLUMNS = ("Filière de formation", "Filière de formation très agrégée", "fil_lib")
ADMISSION_COLUMNS = (
    "Effectif total des candidats ayant accepté la proposition de l’établissement (admis)",
    "Effectif total des candidats ayant accepté la proposition de l'établissement (admis)",
    "acc_tot",
)

COLUMN_ALIASES = {
    "etab": ("Établissement", "g_ea_lib"),
    "ville": (
        "Commune de l’établissement",
        "Ville de l'établissement",
        "ville_etab",
    ),
    "acad": ("Académie de l’établissement", "Académie de l'établissement", "academie_rectorat"),
    "filiere": (
        "Filière de formation très détaillée",
        "Filière de formation détaillée bis",
        "Filière de formation",
        "fil_lib_precise",
    ),
    "cap": (
        "Capacité de l’établissement par formation",
        "Capacité d'accueil de la formation",
        "cap_cap",
    ),
    "voeux": (
        "Effectif total des candidats pour une formation",
        "Nombre total de vœux formulés",
        "voe_tot",
    ),
}

MENTION_COLUMNS = {
    "tb_fel": (
        "% d’admis néo bacheliers avec mention Très Bien avec félicitations au bac",
        "% d'admis néo bacheliers avec mention Très Bien avec félicitations au bac",
    ),
    "tb": (
        "% d’admis néo bacheliers avec mention Très Bien au bac",
        "% d'admis néo bacheliers avec mention Très Bien au bac",
    ),
    "b": (
        "% d’admis néo bacheliers avec mention Bien au bac",
        "% d'admis néo bacheliers avec mention Bien au bac",
    ),
    "ab": (
        "% d’admis néo bacheliers avec mention Assez Bien au bac",
        "% d'admis néo bacheliers avec mention Assez Bien au bac",
    ),
    "sans": (
        "% d’admis néo bacheliers sans mention au bac",
        "% d'admis néo bacheliers sans mention au bac",
    ),
}

MENTION_WEIGHTS = {"sans": 0, "ab": 1, "b": 2, "tb": 3, "tb_fel": 4}

BOURSIER_COLUMNS = (
    "% d’admis néo bacheliers boursiers",
    "% d'admis néo bacheliers boursiers",
)

TAUX_ACCES_COLUMNS = ("Taux d’accès", "Taux d'accès")


def resolve_columns(fieldnames):
    if not fieldnames:
        raise ValueError(f"Le fichier {CSV_FILE.name} est vide ou ne contient pas d’en-tête.")

    columns = {}
    for field, aliases in COLUMN_ALIASES.items():
        column = next((name for name in aliases if name in fieldnames), None)
        if column is None:
            raise ValueError(
                f"Colonne requise absente pour « {field} ». "
                f"Colonnes recherchées : {', '.join(aliases)}"
            )
        columns[field] = column

    columns["boursiers"] = next(
        (name for name in BOURSIER_COLUMNS if name in fieldnames), None
    )
    columns["admis"] = next((name for name in ADMISSION_COLUMNS if name in fieldnames), None)
    columns["taux_acces"] = next(
        (name for name in TAUX_ACCES_COLUMNS if name in fieldnames), None
    )
    columns["mentions"] = {
        mention: next((name for name in aliases if name in fieldnames), None)
        for mention, aliases in MENTION_COLUMNS.items()
    }
    return columns


def clean_num(value, field, row_number, is_float=False):
    if value is None or not value.strip():
        return 0.0 if is_float else 0

    normalized = (
        value.replace("\xa0", "")
        .replace(" ", "")
        .replace(",", ".")
        .replace("%", "")
        .strip()
    )
    try:
        number = float(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Valeur non numérique dans la colonne « {field} », ligne {row_number} : {value!r}"
        ) from exc

    if not math.isfinite(number):
        raise ValueError(
            f"Valeur non finie dans la colonne « {field} », ligne {row_number} : {value!r}"
        )
    return number if is_float else int(number)


def first_non_empty(row, *columns, default=""):
    for column in columns:
        value = row.get(column)
        if value and value.strip():
            return value.strip()
    return default


def official_parcoursup_url(value):
    if "\\" in value:
        return ""
    try:
        url = urlsplit(value)
        hostname = url.hostname or ""
    except ValueError:
        return ""
    if (
        url.scheme == "https"
        and (hostname == "parcoursup.fr" or hostname.endswith(".parcoursup.fr"))
        and url.username is None
        and url.password is None
    ):
        return value
    return ""


def mention_score(mentions):
    pairs = [(weight, mentions.get(category)) for category, weight in MENTION_WEIGHTS.items()]
    values = [(weight, value) for weight, value in pairs if value is not None and 0 <= value <= 100]
    if len(values) != len(pairs):
        return None
    total = sum(value for _, value in values)
    if not total:
        return None
    return round(25 * sum(weight * value for weight, value in values) / total, 2)


def assign_mention_ranks(formations):
    ranked = []
    for formation in formations:
        score = mention_score(formation["mentions"])
        formation["score_mentions"] = score
        formation["rang_mentions"] = None
        formation["threshold_size"] = THRESHOLD_SIZE
        if score is not None and formation["admis"] is not None and formation["admis"] >= THRESHOLD_SIZE:
            ranked.append((score, formation))

    ranked.sort(key=lambda entry: entry[0], reverse=True)
    previous_score = None
    current_rank = 0
    for position, (score, formation) in enumerate(ranked, start=1):
        if score != previous_score:
            current_rank = position
            previous_score = score
        formation["rang_mentions"] = current_rank


def process_parcoursup():
    if not CSV_FILE.is_file():
        raise FileNotFoundError(f"Le fichier {CSV_FILE.name} est introuvable.")

    with CSV_FILE.open(mode="r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=";")
        columns = resolve_columns(reader.fieldnames)
        print(f"Fichier CSV ouvert. {len(reader.fieldnames)} colonnes détectées.")

        data = []
        for row_number, row in enumerate(reader, start=2):
            etab = first_non_empty(row, columns["etab"], default="Inconnu")
            ville = first_non_empty(row, columns["ville"])
            if ville.replace(".", "").isdigit():
                ville = first_non_empty(
                    row,
                    "Département de l’établissement",
                    "Département de l'établissement",
                )

            admis_column = columns["admis"]
            admis = first_non_empty(row, admis_column) if admis_column else ""
            voeux = first_non_empty(row, columns["voeux"])
            taux_column = columns["taux_acces"]
            taux_acces = first_non_empty(row, taux_column) if taux_column else ""
            mentions = {}
            for mention, column in columns["mentions"].items():
                value = first_non_empty(row, column) if column else ""
                mentions[mention] = (
                    clean_num(value, column or mention, row_number, is_float=True)
                    if value else None
                )
            data.append(
                {
                    "row_id": row_number - 2,
                    "id": first_non_empty(
                        row, "Code UAI de l'établissement", "g_ea_uai", default=str(row_number - 2)
                    ),
                    "etab": etab,
                    "ville": ville,
                    "acad": first_non_empty(row, *COLUMN_ALIASES["acad"]),
                    "filiere": first_non_empty(
                        row, *COLUMN_ALIASES["filiere"], default="Formation"
                    ),
                    # DictReader keeps the last duplicate header: the grouped filière.
                    "filiere_groupe": first_non_empty(row, *FILIERE_GROUP_COLUMNS),
                    "cap": clean_num(row.get(columns["cap"]), columns["cap"], row_number),
                    "admis": clean_num(admis, admis_column, row_number) if admis_column and admis else None,
                    "session": first_non_empty(row, "Session", "session"),
                    "lien_parcoursup": official_parcoursup_url(
                        first_non_empty(row, "Lien de la formation sur la plateforme Parcoursup", "lien_form_psup")
                    ),
                    "voeux": clean_num(voeux, columns["voeux"], row_number) if voeux else None,
                    "taux_acces": (
                        clean_num(taux_acces, taux_column, row_number, is_float=True)
                        if taux_column and taux_acces else None
                    ),
                    "boursiers": clean_num(
                        row.get(columns["boursiers"]) if columns["boursiers"] else None,
                        columns["boursiers"] or "boursiers",
                        row_number,
                        is_float=True,
                    ),
                    "mentions": mentions,
                }
            )

    assign_mention_ranks(data)
    print(f"Total formations converties : {len(data)}")
    if not data:
        raise ValueError("Aucune formation extraite du CSV.")

    total_cap = sum(item["cap"] for item in data)
    print(f"Somme totale des capacités d'accueil : {total_cap}")
    if total_cap < 1000:
        raise ValueError(
            f"Capacité totale anormale ({total_cap}). "
            "Vérifiez la colonne de capacité du CSV."
        )

    with JSON_OUTPUT.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(data, output, ensure_ascii=False, separators=(",", ":"))
    print(f"Fichier {JSON_OUTPUT.name} généré avec succès.")


if __name__ == "__main__":
    process_parcoursup()
