# Parcoursup Explorer

Application statique de recherche et de comparaison des formations Parcoursup.

Version en ligne : https://lasnef.github.io/parkour/

## Utiliser la page

- **Rechercher** par établissement, commune ou intitulé de formation. La recherche se combine avec le filtre **Filière de formation**, qui utilise les catégories du CSV, tandis que le tableau conserve les intitulés détaillés.
- **Trier** par établissement et ville, filière, nombre de candidats, capacité, nombre d'admis, taux d'accès ou rang des mentions. Les valeurs indisponibles restent en fin de liste. Par défaut, les meilleurs scores apparaissent en premier. Les résultats sont affichés par pages de 15.
- **Consulter le taux d'accès** dans le tableau et les détails : il provient directement de la colonne « Taux d'accès » du CSV et est affiché en pourcentage. Il est indiqué NA pour moins de 10 admis et N/D si le nombre d'admis ou le taux manque.
- **Ouvrir Détails** pour voir le nombre d'admis rapporté à la capacité d'accueil (par exemple `20 / 25`), le rang et le score, la part des néo-bacheliers boursiers et la répartition des mentions au bac. La fiche indique la session des données et propose le lien officiel Parcoursup lorsqu'il est disponible. « Admis / places » compare deux effectifs, ce n'est pas un taux d'admission.
- **Comparer** en recherchant une deuxième formation dans **Détails**. Les deux distributions s'affichent côte à côte sur le même histogramme. La légende affiche le nom de chaque établissement et son score entre parenthèses. Le bouton **Retirer** revient au graphique d'une seule formation.

La page [index.html](./index.html) charge `data.json` depuis le même dossier. Les filtres, le tri et la comparaison s'exécutent dans le navigateur, sans API ni base de données côté serveur. Alpine.js gère les interactions, Chart.js affiche l'histogramme et Tailwind CSS gère la mise en forme. Ces trois bibliothèques sont chargées depuis des CDN : même avec le serveur local, la page nécessite un accès à Internet pour les récupérer.

## Traitement des données

1. [build.py](./build.py) lit [fr-esr-parcoursup.csv](./fr-esr-parcoursup.csv) en UTF-8, avec `;` comme séparateur, et identifie les colonnes utilisées à partir de leurs intitulés.
2. Le script nettoie les valeurs numériques (espaces, virgules décimales, signes `%`) et extrait les champs utiles au site : identifiants, établissement, commune, académie, intitulé détaillé, catégorie de filière, capacité, effectifs des candidats et des admis, taux d'accès, session, lien officiel Parcoursup, part des néo-bacheliers boursiers et répartition des mentions. L'effectif des candidats est exporté dans `voeux`. Pour le filtre par filière, le script utilise le second en-tête `Filière de formation`, qui correspond aux catégories regroupées.
3. Le script calcule `score_mentions` et `rang_mentions`, et exporte le seuil `THRESHOLD_SIZE` pour l'affichage des indicateurs. Il vérifie qu'au moins une formation a été extraite et que la capacité totale est d'au moins 1 000 places, puis écrit le fichier généré `data.json`. Le CSV d'origine n'est pas modifié ; le JSON est régénéré à chaque build et n'est pas suivi par Git.

### Classement par mentions

Quand les données sont suffisantes, une formation reçoit un score sur 100 à partir des mentions au bac des admis néo-bacheliers :

> **Score = 25 × (% Assez Bien + 2 × % Bien + 3 × % Très Bien + 4 × % Très Bien avec félicitations) ÷ somme des cinq pourcentages**

« Sans mention » vaut 0 point, mais son pourcentage est inclus au dénominateur. Diviser par la somme plutôt que par 100 tient compte des écarts dans les données, notamment dus aux arrondis. Le score est arrondi à deux décimales. Le rang est calculé sur l'ensemble des formations éligibles, du score le plus élevé au plus faible ; les scores égaux partagent le même rang (par exemple 1, 1, 3). Le filtre ne recalcule pas le rang. Les formations ayant moins de 10 admis sont exclues du classement et leur rang est indiqué NA ; celles dont le nombre d'admis est inconnu sont également exclues et leur rang est indiqué N/D. Leur score et leur répartition restent affichés si les données sont suffisantes. Si un des cinq pourcentages manque ou est hors de l'intervalle de 0 à 100, ou si les cinq valent zéro, le score et le rang sont indisponibles.

Le taux d'accès n'intervient pas dans la formule. Ce score décrit le profil des admis, pas la qualité pédagogique ; une petite cohorte peut obtenir un score élevé.

## Lancer en local

Python 3.10 ou plus récent est nécessaire. Aucune dépendance Python externe n'est requise.

Depuis la racine du dépôt, générer les données puis démarrer le serveur :

```powershell
python build.py
python -m http.server 8000
```

Ouvrir ensuite http://localhost:8000. Garder le serveur en cours d'exécution pendant la navigation et l'arrêter avec `Ctrl+C`.

Ne pas ouvrir `index.html` directement avec `file://` : le navigateur bloque alors le chargement de `data.json`.

## Pipeline GitHub Actions et déploiement

Le workflow [deploy.yml](./.github/workflows/deploy.yml) se déclenche sur les pull requests qui ciblent `main` et les pushs sur `main`. Il tourne sur Ubuntu avec Python 3.10 :

1. Lance les tests Python avec `python -m unittest discover -s tests`.
2. Exécute `python build.py` et vérifie avec `python -m json.tool data.json` que le fichier généré est un JSON valide.
3. Prépare le dossier `site/` avec seulement `index.html` et `data.json`.
4. Sur un push sur `main` uniquement, configure GitHub Pages, téléverse le dossier `site/` comme artefact, puis le déploie si les étapes précédentes ont réussi. Une pull request valide le build sans publier le site.

Dans les paramètres du dépôt (**Settings → Pages**), la source de publication doit être réglée sur **GitHub Actions**.

## Améliorations possibles

Les idées d'affichage et les évolutions techniques sont regroupées dans [AMELIORATIONS.md](./AMELIORATIONS.md).

## Annexe — Colonnes du CSV source

Les 118 intitulés de [fr-esr-parcoursup.csv](./fr-esr-parcoursup.csv) figurent ci-dessous dans l'ordre du fichier. Les deux colonnes nommées `Filière de formation` sont conservées dans la liste, même si leurs intitulés sont identiques.

- Session
- Statut de l’établissement de la filière de formation (public, privé…)
- Code UAI de l'établissement
- Établissement
- Code départemental de l’établissement
- Département de l’établissement
- Région de l’établissement
- Académie de l’établissement
- Commune de l’établissement
- Filière de formation
- Sélectivité
- Filière de formation très agrégée
- Filière de formation détaillée
- Filière de formation
- Filière de formation détaillée bis
- Filière de formation très détaillée
- Coordonnées GPS de la formation
- Capacité de l’établissement par formation
- Effectif total des candidats pour une formation
- Dont effectif des candidates pour une formation
- Effectif total des candidats en phase principale
- Dont effectif des candidats ayant postulé en internat
- Effectif des candidats néo bacheliers généraux en phase principale
- Dont effectif des candidats boursiers néo bacheliers généraux en phase principale
- Effectif des candidats néo bacheliers technologiques en phase principale
- Dont effectif des candidats boursiers néo bacheliers technologiques en phase principale
- Effectif des candidats néo bacheliers professionnels en phase principale
- Dont effectif des candidats boursiers néo bacheliers professionnels en phase principale
- Effectif des autres candidats en phase principale
- Effectif total des candidats en phase complémentaire
- Effectif des candidats néo bacheliers généraux en phase complémentaire
- Effectif des candidats néo bacheliers technologique en phase complémentaire
- Effectif des candidats néo bacheliers professionnels en phase complémentaire
- Effectifs des autres candidats en phase complémentaire
- Effectif total des candidats classés par l’établissement en phase principale
- Effectif des candidats classés par l’établissement en phase complémentaire
- Effectif des candidats classés par l’établissement en internat (CPGE)
- Effectif des candidats classés par l’établissement hors internat (CPGE)
- Effectif des candidats néo bacheliers généraux classés par l’établissement
- Dont effectif des candidats boursiers néo bacheliers généraux classés par l’établissement
- Effectif des candidats néo bacheliers technologiques classés par l’établissement
- Dont effectif des candidats boursiers néo bacheliers technologiques classés par l’établissement
- Effectif des candidats néo bacheliers professionnels classés par l’établissement
- Dont effectif des candidats boursiers néo bacheliers professionnels classés par l’établissement
- Effectif des autres candidats classés par l’établissement
- Effectif total des candidats ayant reçu une proposition d’admission de la part de l’établissement
- Effectif total des candidats ayant accepté la proposition de l’établissement (admis)
- Dont effectif des candidates admises
- Effectif des admis en phase principale
- Effectif des admis en phase complémentaire
- Dont effectif des admis ayant reçu leur proposition d’admission à l'ouverture de la procédure principale
- Dont effectif des admis ayant reçu leur proposition d’admission avant le baccalauréat
- Dont effectif des admis ayant reçu leur proposition d’admission avant la fin de la procédure principale
- Dont effectif des admis en internat
- Dont effectif des admis boursiers néo bacheliers
- Effectif des admis néo bacheliers
- Effectif des admis néo bacheliers généraux
- Effectif des admis néo bacheliers technologiques
- Effectif des admis néo bacheliers professionnels
- Effectif des autres candidats admis
- Dont effectif des admis néo bacheliers sans information sur la mention au bac
- Dont effectif des admis néo bacheliers sans mention au bac
- Dont effectif des admis néo bacheliers avec mention Assez Bien au bac
- Dont effectif des admis néo bacheliers avec mention Bien au bac
- Dont effectif des admis néo bacheliers avec mention Très Bien au bac
- Dont effectif des admis néo bacheliers avec mention Très Bien avec félicitations au bac
- Effectif des admis néo bacheliers généraux ayant eu une mention au bac
- Effectif des admis néo bacheliers technologiques ayant eu une mention au bac
- Effectif des admis néo bacheliers professionnels ayant eu une mention au bac
- Dont effectif des admis issus du même établissement (BTS/CPGE)
- Dont effectif des admises issues du même établissement (BTS/CPGE)
- Dont effectif des admis issus de la même académie
- Dont effectif des admis issus de la même académie (Paris/Créteil/Versailles réunies)
- % d’admis ayant reçu leur proposition d’admission à l'ouverture de la procédure principale
- % d’admis ayant reçu leur proposition d’admission avant le baccalauréat
- % d’admis ayant reçu leur proposition d’admission avant la fin de la procédure principale
- % d’admis dont filles
- % d’admis néo bacheliers issus de la même académie
- % d’admis néo bacheliers issus de la même académie (Paris/Créteil/Versailles réunies)
- % d’admis néo bacheliers issus du même établissement (BTS/CPGE)
- % d’admis néo bacheliers boursiers
- % d’admis néo bacheliers
- % d’admis néo bacheliers sans information sur la mention au bac
- % d’admis néo bacheliers sans mention au bac
- % d’admis néo bacheliers avec mention Assez Bien au bac
- % d’admis néo bacheliers avec mention Bien au bac
- % d’admis néo bacheliers avec mention Très Bien au bac
- % d’admis néo bacheliers avec mention Très Bien avec félicitations au bac
- % d’admis néo bacheliers généraux
- Dont % d’admis avec mention (BG)
- % d’admis néo bacheliers technologiques
- Dont % d’admis avec mention (BT)
- % d’admis néo bacheliers professionnels
- Dont % d’admis avec mention (BP)
- Effectif des candidats en terminale générale ayant reçu une proposition d’admission de la part de l’établissement
- Dont effectif des candidats boursiers en terminale générale ayant reçu une proposition d’admission de la part de l’établissement
- Effectif des candidats en terminale technologique ayant reçu une proposition d’admission de la part de l’établissement
- Dont effectif des candidats boursiers en terminale technologique ayant reçu une proposition d’admission de la part de l’établissement
- Effectif des candidats en terminale professionnelle ayant reçu une proposition d’admission de la part de l’établissement
- Dont effectif des candidats boursiers en terminale générale professionnelle ayant reçu une proposition d’admission de la part de l’établissement
- Effectif des autres candidats ayant reçu une proposition d’admission de la part de l’établissement
- Regroupement 1 effectué par les formations pour les classements
- Rang du dernier appelé du groupe 1
- Regroupement 2 effectué par les formations pour les classements
- Rang du dernier appelé du groupe 2
- Regroupement 3 effectué par les formations pour les classements
- Rang du dernier appelé du groupe 3
- list_com
- tri
- cod_aff_form
- Concours communs et banque d'épreuves
- Lien de la formation sur la plateforme Parcoursup
- Taux d’accès
- Part des terminales générales qui étaient en position de recevoir une proposition en phase principale
- Part des terminales technologiques qui étaient en position de recevoir une proposition en phase principale
- Part des terminales professionnelles qui étaient en position de recevoir une proposition en phase principale
- etablissement_id_paysage
- composante_id_paysage
