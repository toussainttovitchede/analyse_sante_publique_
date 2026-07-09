---
title: "Tableau de Bord Analytique — Santé Publique en Afrique de l'Ouest"
subtitle: "Documentation méthodologique — Données, traitement, résultats et limites"
date: "9 juillet 2026"
---

# 1. Contexte et objectifs

Ce projet vise à concevoir un tableau de bord analytique interactif (Streamlit) permettant de visualiser et d'interpréter l'évolution de trois indicateurs de santé publique sur la période **2000-2022**, pour **9 pays d'Afrique de l'Ouest** : Bénin, Burkina Faso, Côte d'Ivoire, Ghana, Mali, Niger, Nigeria, Sénégal, Togo.

**Indicateurs cibles (cahier des charges) :**

- Incidence du paludisme (pour 1 000 habitants à risque)
- Taux de mortalité maternelle (pour 100 000 naissances vivantes)
- Couverture des soins prénataux (%)

**Objectifs spécifiques :** chargement et nettoyage des données open source, analyse exploratoire (tendances, comparaisons, corrélations), construction d'un dashboard multi-onglets, identification des zones et périodes critiques, documentation de la méthodologie et de ses limites.

**Périmètre pays — note méthodologique importante :** le cahier des charges initial mentionnait le Sénégal et 4 pays voisins (dont la Guinée). Le périmètre a été ajusté en cours de projet, à la demande du porteur de projet, vers un panel élargi de 9 pays d'Afrique de l'Ouest, sans la Guinée. Ce changement est documenté ici pour assurer la traçabilité méthodologique des choix de scope.

---

# 2. Sources de données

| Source | Fichier | Contenu | Licence |
|---|---|---|---|
| Our World in Data (OWID) | `malariaIncidenceAfrique2000_2022.csv` | Incidence du paludisme | CC BY 4.0 |
| Our World in Data (OWID) | `Mortality_Maternal.csv` | Mortalité maternelle | CC BY 4.0 |
| Our World in Data (OWID) | `Soins_Prenatal.csv` | Couverture soins prénataux | CC BY 4.0 |
| World Health Data (Kaggle) | `world_health_data.csv` | Enrichissement : espérance de vie, dépenses de santé, mortalité infantile/néonatale/-5 ans | Open Data |

Les 3 sources OWID ont été utilisées comme **source primaire** pour les indicateurs cibles. Le fichier World Health Data a été utilisé en **enrichissement contextuel** pour l'analyse de corrélations, après filtrage sur les 9 pays et la période 2000-2022.

---

# 3. Pipeline de traitement des données

## 3.1 Harmonisation et fusion (format long)

Les 4 sources ont été combinées en un **dataset unique au format long** (`data.csv`), structuré ainsi :

| Colonne | Description |
|---|---|
| `Entity` | Nom de pays (clé technique, anglais, sans accent — clé de jointure d'origine OWID) |
| `Code` | Code ISO3 du pays |
| `Year` | Année (2000-2022) |
| `Indicateur` | Nom de l'indicateur (français) |
| `Valeur` | Valeur numérique |
| `Unite` | Unité de mesure |
| `Source` | Source d'origine de la donnée |

**Résultat final : 1 502 lignes, 8 indicateurs, 0 valeur manquante, 0 doublon** (vérifié sur triplet `Entity` + `Year` + `Indicateur`).

## 3.2 Incident de pipeline documenté

Lors de la construction du dataset, un bug a été identifié puis corrigé : la colonne de valeur de chaque indicateur OWID était renommée différemment avant concaténation (`Value_Malaria`, `%Mortality`, `soins_prenatal`, etc.), ce qui provoquait un éclatement en colonnes distinctes lors du `pd.concat`. La sélection finale sur la colonne `Valeur` ne capturait alors que les données d'enrichissement, laissant les 3 indicateurs cibles à 100% vides. **Correctif appliqué :** harmonisation du nom de colonne (`Valeur`) *avant* la concaténation, pour tous les blocs.

**Enseignement méthodologique à retenir :** lors de toute fusion de tableaux (`pd.concat`) portant sur une variable conceptuellement identique (ici, "la valeur de l'indicateur"), le nom de colonne doit être strictement identique dans tous les blocs fusionnés — sinon pandas traite chaque variante comme une variable distincte, avec perte silencieuse de données (aucune erreur levée).

## 3.3 Nettoyage appliqué

- Suppression ciblée des lignes à valeur manquante (`dropna(subset=['Valeur'])`), et non un `dropna()` global qui aurait purgé des lignes valides sur la base de colonnes annexes
- Vérification systématique des doublons sur la clé `(Entity, Year, Indicateur)`
- Contrôle de plage : aucune valeur de pourcentage hors intervalle [0, 100] détectée
- Harmonisation des accents pour l'affichage (ex. `Cote d'Ivoire` → `Côte d'Ivoire`, `Senegal` → `Sénégal`), `Entity`/`Code` conservés comme clés techniques

---

# 4. Qualité et complétude des données par indicateur

| Indicateur | Lignes | Complétude (pays × 23 années) | Nature de la lacune |
|---|---|---|---|
| Incidence du paludisme | 207 | 100% | Aucune |
| Mortalité maternelle | 207 | 100% | Aucune |
| Mortalité infantile / néonatale / -5 ans | 207 chacun | 100% | Aucune |
| Espérance de vie | 207 | 100% | Aucune |
| Dépenses de santé | 198 | 96% | Ponctuelle, non structurelle |
| **Couverture soins prénataux** | **62** | **30%** | **Structurelle — voir 6.1** |

Le paludisme et la mortalité maternelle bénéficient d'une **couverture annuelle complète** pour les 9 pays, ce qui permet une analyse de tendance fiable année par année. La couverture des soins prénataux reste, par nature de la source (enquêtes démographiques ponctuelles, pas de collecte annuelle), **fortement discontinue** : de 4 points (Niger) à 12 points (Sénégal) sur 23 ans.

---

# 5. Résultats clés de l'analyse exploratoire

## 5.1 Incidence du paludisme — variation 2000 → 2022

| Pays | Variation |
|---|---|
| Sénégal | **−83,5 %** |
| Ghana | −51,0 % |
| Côte d'Ivoire | −42,7 % |
| Burkina Faso | −40,3 % |
| Togo | −37,4 % |
| Nigeria | −25,6 % |
| Niger | −15,1 % |
| Mali | −12,3 % |
| Bénin | −9,5 % |

Le Sénégal enregistre la baisse la plus marquée du panel, largement supérieure aux autres pays. Bénin, Mali et Niger affichent une amélioration nettement plus limitée sur la période.

## 5.2 Mortalité maternelle — variation 2000 → 2022

| Pays | Variation |
|---|---|
| Sénégal | −60,7 % |
| Niger | −57,3 % |
| Ghana | −49,4 % |
| Mali | −48,6 % |
| Burkina Faso | −39,7 % |
| Togo | −26,9 % |
| Nigeria | −10,5 % |
| Bénin | **+3,3 %** |
| Côte d'Ivoire | **+8,4 %** |

**Point critique à signaler :** contrairement à la tendance générale à la baisse, le **Bénin et la Côte d'Ivoire affichent une hausse** de la mortalité maternelle sur 22 ans. Ce sont les deux zones les plus préoccupantes du panel sur cet indicateur et méritent un focus particulier dans le dashboard.

## 5.3 Couverture des soins prénataux — dernière valeur disponible

| Pays | Dernière année | Valeur |
|---|---|---|
| Sénégal | 2019 | 97,6 % |
| Ghana | 2019 | 97,4 % |
| Côte d'Ivoire | 2016 | 93,2 % |
| Niger | 2021 | 83,5 % |
| Bénin | 2018 | 83,2 % |
| Burkina Faso | 2018 | 80,2 % |
| Mali | 2018 | 79,5 % |
| Togo | 2017 | 77,9 % |
| Nigeria | 2018 | 67,0 % |

Le Nigeria présente la couverture la plus faible et la donnée la moins récente avec le Togo — à interpréter avec prudence étant donné l'hétérogénéité des années de référence entre pays (comparaison non strictement synchrone).

---

# 6. Valeurs aberrantes, biais et limites

## 6.1 Détection des valeurs aberrantes — un piège méthodologique évité

Un test IQR (écart interquartile) appliqué **globalement** sur la mortalité maternelle (toutes années et tous pays confondus) détecte 23 "valeurs aberrantes" — qui correspondent en réalité aux **23 années du Nigeria dans leur intégralité** (bornes IQR : [135,4 ; 853,6], Nigeria hors bornes sur toute la série).

**Interprétation retenue :** il ne s'agit pas d'erreurs de saisie mais d'une **différence structurelle réelle** entre pays — le Nigeria présente un niveau de mortalité maternelle durablement supérieur au reste du panel. Un test IQR global sur des données de panel (pays × années) confond systématiquement "hétérogénéité inter-pays légitime" et "anomalie ponctuelle". **Recommandation méthodologique appliquée :** la détection d'anomalies doit se faire *par pays*, sur les ruptures/sauts d'une année sur l'autre au sein d'une même série temporelle, et non sur la distribution empilée de l'ensemble du panel. Aucune rupture suspecte n'a été détectée sur les trajectoires nationales individuelles.

Aucune valeur hors intervalle plausible n'a par ailleurs été détectée sur les indicateurs en pourcentage (soins prénataux, dépenses de santé).

## 6.2 Biais identifiés

- **Biais de sélection du périmètre pays :** le panel de 9 pays a été constitué par choix du porteur de projet et ne constitue pas un échantillon représentatif de l'ensemble de l'Afrique de l'Ouest (16 pays CEDEAO). Les résultats et comparaisons ne doivent pas être généralisés au-delà de ce panel.
- **Biais de synchronisation temporelle (soins prénataux) :** faute de collecte annuelle, les comparaisons inter-pays sur cet indicateur reposent sur des années de référence différentes selon le pays (ex. Sénégal 2019 vs Côte d'Ivoire 2016), ce qui peut surestimer ou sous-estimer des écarts réels si des progrès rapides ont eu lieu entre-temps.
- **Biais de source unique pour les indicateurs cibles :** les 3 indicateurs cibles reposent sur une seule source primaire (OWID). Une validation croisée menée en cours de projet, sur une source alternative de mortalité maternelle (couverture mondiale, hors périmètre final), a montré une corrélation de 0,989 et un écart moyen de -0,1 % avec la série OWID retenue — ce qui renforce la confiance dans la fiabilité de la source principale, sans toutefois constituer une preuve d'absence de biais méthodologique commun aux deux sources (méthodes d'estimation de l'OMS largement partagées).
- **Biais de couverture des enquêtes démographiques :** les données de soins prénataux proviennent d'enquêtes déclaratives (types EDS/MICS), sujettes à un biais de déclaration et à une couverture inégale des zones rurales/urbaines au sein de chaque pays — non observable à l'échelle nationale agrégée utilisée ici.
- **Biais d'agrégation nationale :** toutes les données sont agrégées au niveau pays. D'importantes disparités infranationales (urbain/rural, régions) sont invisibles à cette échelle — pertinent en particulier pour le Sénégal, où le cahier des charges visait initialement une lecture régionale.

## 6.3 Limites connues

- **Absence de données infranationales** : aucune source disponible ne permet une carte choroplèthe par région sénégalaise (Dakar, Saint-Louis, Thiès, etc.). Le dashboard propose en repli une carte choroplèthe à l'échelle des 9 pays.
- **Couverture soins prénataux fortement discontinue** (30% de complétude théorique) : l'interpolation a été jugée non pertinente (risque de créer une fausse impression de continuité) ; le dashboard privilégie une visualisation par points discrets plutôt qu'une ligne de tendance interpolée.
- **Variable "groupe de revenus"** : classification Banque Mondiale FY26 (année fiscale juillet 2025 - juin 2026, GNI Atlas 2024), figée au moment de la rédaction ; à mettre à jour à chaque nouvelle classification annuelle (publiée au 1er juillet).
- **Variable "région OMS"** : constante pour l'ensemble du panel (tous les pays appartiennent à la région AFRO) — peu discriminante en l'état, mentionnée pour conformité avec le cahier des charges plutôt que pour son pouvoir explicatif.
- **Aucune donnée de couverture vaccinale** intégrée à ce stade, malgré sa mention initiale dans le cahier des charges — piste d'enrichissement futur identifiée mais non réalisée dans le périmètre actuel.

---

# 7. Analyse de corrélation entre indicateurs

Une matrice de corrélation a été calculée sur l'ensemble panel-années (Pearson, données appariées disponibles) :

![Matrice de corrélation](correlation_finale.png)

**Corrélations avec la mortalité maternelle, du plus fort au plus faible :**

| Indicateur | Corrélation |
|---|---|
| Espérance de vie | −0,73 |
| Couverture soins prénataux | −0,70 |
| Mortalité infantile | +0,67 |
| Mortalité néonatale | +0,61 |
| Mortalité des moins de 5 ans | +0,60 |
| Dépenses de santé | −0,22 |
| **Incidence du paludisme** | **+0,12** |

**Résultat contre-intuitif à souligner :** la couverture des soins prénataux (−0,70) apparaît comme un corrélat beaucoup plus fort de la mortalité maternelle que l'incidence du paludisme (+0,12), pourtant l'un des deux indicateurs sanitaires vedettes du projet. Cela suggère, sur ce panel, que l'accès aux soins prénataux est un levier de réduction de la mortalité maternelle plus déterminant que la seule pression du paludisme — un résultat à nuancer (corrélation n'est pas causalité, facteurs confondants possibles comme le niveau de développement général du pays) mais pertinent pour orienter la lecture du dashboard.

*Note méthodologique : une corrélation, même forte, ne permet pas d'établir un lien de causalité. Les indicateurs comparés ici évoluent tous avec le niveau de développement sanitaire global d'un pays, ce qui peut gonfler artificiellement certaines corrélations (facteur confondant commun).*

---

# 8. Architecture du dashboard Streamlit

Le dashboard final s'organise en **3 onglets**, avec des filtres globaux (pays, groupe de revenus, période) appliqués de façon cohérente sur l'ensemble des vues :

1. **Évolution temporelle** — courbes par indicateur cible, filtrable par pays/période, avec un focus KPI dédié au Sénégal
2. **Comparaison entre pays** — classement à une année donnée, incluant les indicateurs d'enrichissement (espérance de vie, dépenses de santé)
3. **Cartographie** — choroplèthe à l'échelle des 9 pays (codes ISO3), avec note explicite sur l'impossibilité d'une carte régionale sénégalaise en l'état des données

---

# 9. Synthèse et recommandations

- Le **Sénégal** se distingue comme la meilleure trajectoire du panel sur les deux indicateurs cibles principaux (paludisme et mortalité maternelle), avec les baisses les plus marquées sur la période.
- **Bénin et Côte d'Ivoire** constituent les points de vigilance prioritaires, avec une mortalité maternelle en hausse sur 22 ans malgré la tendance régionale à la baisse — à documenter et surveiller en priorité dans le dashboard.
- La **couverture soins prénataux** apparaît comme le levier le plus fortement corrélé à la réduction de la mortalité maternelle dans ce panel, davantage que la lutte antipaludique — un angle d'analyse à mettre en avant dans les visualisations et les messages clés du dashboard.
- Pistes d'amélioration futures : intégration de données de couverture vaccinale, recherche d'une source infranationale pour le Sénégal, mise à jour annuelle de la classification de revenus.

---

*Documentation rédigée le 9 juillet 2026 — Sources : Our World in Data (CC BY 4.0), World Health Data (Kaggle), Banque Mondiale (classifications FY26).*
