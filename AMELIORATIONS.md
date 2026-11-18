# Parcoursup Explorer — Améliorations possibles

Ces pistes ne sont pas encore implémentées. L'objectif est d'aider à comparer les formations sans présenter le score des mentions comme une mesure de la qualité de l'enseignement ni les statistiques passées comme des chances individuelles d'admission.

## En priorité : enrichir la fiche Détails

| À afficher | Données disponibles et intérêt |
| --- | --- |
| **Taille de la cohorte et couverture des mentions** | Afficher l'effectif des admis néo-bacheliers et le nombre pour lequel la mention est connue, à partir de l'effectif total et de l'effectif sans information. On ne lit pas de la même façon un score calculé sur 5 ou sur 100 élèves. |
| **Effectifs à côté des pourcentages** | Ajouter sous l'histogramme un tableau des cinq catégories avec les effectifs du CSV et les pourcentages. Il rend la comparaison lisible sans survol, sur mobile comme avec un lecteur d'écran. Distinguer « sans mention » de « mention non renseignée ». |
| **Candidats et propositions** | Compléter l'affichage « Admis / places proposées » par les effectifs de candidats et de candidats ayant reçu une proposition. Présenter éventuellement le nombre de candidats par place sans l'assimiler à une probabilité d'admission. |

## Comparaisons et filtres

- **Repère dans la même filière.** Afficher le score médian et le nombre de formations comparables de la même filière et de la même session, en gardant le rang global distinct. Proposer de limiter la recherche de comparaison à la même filière.
- **Profil des admis.** Ajouter une répartition par type de bac (général, technologique, professionnel) et, en complément, la part de boursiers ou d'admis de la même académie. Indiquer le dénominateur de chaque pourcentage.
- **Calendrier des propositions.** Afficher la part des admis ayant reçu leur proposition à l'ouverture, avant le bac et avant la fin de la phase principale. Présenter ces jalons séparément : les pourcentages sont cumulés, ils ne s'additionnent pas.
- **Rang du dernier appelé par groupe.** L'afficher seulement lorsqu'il est renseigné, avec le nom du groupe et la session. Ce repère historique n'est ni un seuil garanti ni directement comparable entre groupes.
- **Filtres région et statut, puis carte.** Commencer par les filtres région, département et public/privé. Ajouter ensuite une carte optionnelle à partir des coordonnées GPS, en conservant la liste pour les formations sans coordonnées.
- **Comparaison partageable.** Mettre les filtres et les deux formations sélectionnées dans l'URL. Identifier chaque formation avec un identifiant vérifié comme unique et stable pour la session, plutôt qu'avec son numéro de ligne.
- **Évolution par session.** Une fois plusieurs millésimes importés, afficher l'évolution de la capacité, des candidatures et du profil des admis. Vérifier la correspondance des formations et la stabilité des définitions d'une année à l'autre avant de tracer une courbe.

## Fiabiliser le traitement et la page

- **Valider le CSV en CI.** Vérifier les colonnes attendues, distinguer explicitement les deux en-têtes `Filière de formation`, contrôler les bornes des pourcentages et produire un résumé des données manquantes à chaque build.
- **Séparer zéro et donnée manquante.** Conserver les valeurs absentes dans le JSON pour les indicateurs qui les convertissent actuellement en zéro, comme la part de boursiers. Afficher `N/D` plutôt que `0 %` quand la valeur est inconnue.
- **Tester le parcours utilisateur.** Ajouter un test navigateur ciblé : combiner des filtres, ouvrir une fiche, ajouter puis retirer une comparaison et vérifier les libellés de la légende.
- **Rendre les dépendances reproductibles.** Figer les versions des bibliothèques front-end et envisager de servir les fichiers depuis le site pour permettre une utilisation locale sans accès aux CDN.
- **Mesurer avant d'optimiser.** Si l'ajout de données ralentit le premier chargement, mesurer la taille transférée et le temps de rendu avant de séparer les données de recherche et les détails.
