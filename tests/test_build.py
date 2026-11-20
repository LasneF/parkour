import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import build
from build import assign_mention_ranks, mention_score


class FormationDetailsTests(unittest.TestCase):
    def test_build_exports_session_admissions_capacity_and_official_link(self):
        required_fields = [aliases[0] for aliases in build.COLUMN_ALIASES.values()]
        link = "https://dossierappel.parcoursup.fr/Candidats/public/fiches/afficherFicheFormation?g_ta_cod=2519"
        with TemporaryDirectory() as directory:
            source = Path(directory) / "formations.csv"
            output = Path(directory) / "data.json"
            with source.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, delimiter=";")
                writer.writerow([
                    *required_fields, "Session",
                    "Effectif total des candidats ayant accepté la proposition de l’établissement (admis)",
                    "Lien de la formation sur la plateforme Parcoursup",
                    "Taux d’accès",
                ])
                writer.writerow(["Lycée A", "Paris", "Paris", "BTS", 1000, 1300, 2025, 720, link, "28,5"])
                writer.writerow(["Lycée B", "Lyon", "Lyon", "BTS", 15, 40, 2025, 0, "", "0"])
                writer.writerow(["Lycée C", "Nice", "Nice", "BTS", 20, "", "", "", "https://parcoursup.fr.example.org", ""])
            with patch.object(build, "CSV_FILE", source), patch.object(build, "JSON_OUTPUT", output):
                build.process_parcoursup()
            rows = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(
            [(row["admis"], row["cap"], row["session"], row["lien_parcoursup"]) for row in rows],
            [(720, 1000, "2025", link), (0, 15, "2025", ""), (None, 20, "", "")],
        )
        self.assertEqual([row["voeux"] for row in rows], [1300, 40, None])
        self.assertEqual([row["taux_acces"] for row in rows], [28.5, 0, None])
        self.assertEqual([row["threshold_size"] for row in rows], [10, 10, 10])


class MentionRankingTests(unittest.TestCase):
    def test_pure_profiles_follow_the_mention_weights(self):
        formations = [
            {"mentions": {"tb_fel": 0, "tb": 0, "b": 0, "ab": 0, "sans": 100}},
            {"mentions": {"tb_fel": 0, "tb": 0, "b": 0, "ab": 100, "sans": 0}},
            {"mentions": {"tb_fel": 0, "tb": 0, "b": 100, "ab": 0, "sans": 0}},
            {"mentions": {"tb_fel": 0, "tb": 100, "b": 0, "ab": 0, "sans": 0}},
            {"mentions": {"tb_fel": 100, "tb": 0, "b": 0, "ab": 0, "sans": 0}},
        ]
        for formation in formations:
            formation["admis"] = 10

        assign_mention_ranks(formations)

        self.assertEqual(
            [formation["rang_mentions"] for formation in reversed(formations)],
            [1, 2, 3, 4, 5],
        )
        self.assertEqual(
            [formation["score_mentions"] for formation in formations],
            [0, 25, 50, 75, 100],
        )

    def test_weighted_average_accounts_for_the_whole_distribution(self):
        few_top_mentions = {"tb_fel": 10, "tb": 0, "b": 0, "ab": 0, "sans": 90}
        mostly_tb = {"tb_fel": 0, "tb": 90, "b": 10, "ab": 0, "sans": 0}

        self.assertEqual(mention_score(few_top_mentions), 10)
        self.assertEqual(mention_score(mostly_tb), 72.5)

    def test_score_normalizes_percentages_that_do_not_sum_to_100(self):
        mentions = {"tb_fel": 0, "tb": 0, "b": 34, "ab": 0, "sans": 65}
        self.assertEqual(mention_score(mentions), 17.17)

    def test_equal_normalized_profiles_share_a_competition_rank(self):
        formations = [
            {"mentions": {"tb_fel": 0, "tb": 10, "b": 20, "ab": 30, "sans": 40}},
            {"mentions": {"tb_fel": 0, "tb": 20, "b": 40, "ab": 60, "sans": 80}},
            {"mentions": {"tb_fel": 0, "tb": 0, "b": 0, "ab": 50, "sans": 50}},
        ]
        for formation in formations:
            formation["admis"] = 10

        assign_mention_ranks(formations)

        self.assertEqual(
            [formation["rang_mentions"] for formation in formations],
            [1, 1, 3],
        )

    def test_missing_mentions_have_no_rank(self):
        formations = [
            {"mentions": {"tb_fel": 0, "tb": 0, "b": 0, "ab": 0, "sans": 0}},
            {"mentions": {"tb_fel": None, "tb": 0, "b": 50, "ab": 25, "sans": 25}},
            {"mentions": {"tb_fel": 0, "tb": 0, "b": 0, "ab": 0, "sans": 100}},
        ]
        for formation in formations:
            formation["admis"] = 10
        assign_mention_ranks(formations)
        self.assertEqual([item["rang_mentions"] for item in formations], [None, None, 1])
        self.assertEqual([item["score_mentions"] for item in formations], [None, None, 0])

    def test_small_and_unknown_cohorts_are_excluded_from_ranking(self):
        strong = {"tb_fel": 100, "tb": 0, "b": 0, "ab": 0, "sans": 0}
        weaker = {"tb_fel": 0, "tb": 0, "b": 100, "ab": 0, "sans": 0}
        formations = [
            {"admis": 0, "mentions": strong},
            {"admis": 9, "mentions": strong},
            {"admis": None, "mentions": strong},
            {"admis": 10, "mentions": weaker},
            {"admis": 11, "mentions": weaker},
        ]

        assign_mention_ranks(formations)

        self.assertEqual([item["rang_mentions"] for item in formations], [None, None, None, 1, 1])
        self.assertEqual([item["score_mentions"] for item in formations], [None, None, None, 50, 50])


if __name__ == "__main__":
    unittest.main()
