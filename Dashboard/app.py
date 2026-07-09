"""
Tableau de Bord Analytique - Santé Publique en Afrique de l'Ouest
==================================================================
Indicateurs cibles : incidence du paludisme, mortalité maternelle,
couverture des soins prénataux (2000-2022, 9 pays d'Afrique de l'Ouest).

Reproductibilité : placer ce fichier et "data.csv" dans le même dossier
(ou adapter DATA_FILENAME ci-dessous), puis lancer :
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- 0. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Dashboard Santé Publique - Afrique de l'Ouest",
    page_icon="🩺",
    layout="wide"
)

# --- 1. CONSTANTES DE RÉFÉRENCE (documentées, pas de "magie") ---

# Noms d'affichage en français, accentués, pour un public non-technique.
# La clé technique de jointure reste "Entity" (nom OWID d'origine).
NOMS_AFFICHAGE = {
    "Benin": "Bénin", "Burkina Faso": "Burkina Faso", "Cote d'Ivoire": "Côte d'Ivoire",
    "Ghana": "Ghana", "Mali": "Mali", "Niger": "Niger", "Nigeria": "Nigeria",
    "Senegal": "Sénégal", "Togo": "Togo",
}

# Tous les pays du périmètre appartiennent à la région OMS Afrique (AFRO).
REGION_OMS = "AFRO"

# Groupe de revenus - Classification Banque Mondiale FY26 (GNI Atlas 2024),
# en vigueur du 1er juillet 2025 au 30 juin 2026. À revérifier chaque année
# (mise à jour annuelle au 1er juillet) : https://datahelpdesk.worldbank.org/knowledgebase/articles/906519
GROUPE_REVENUS = {
    "Benin": "Revenu intermédiaire, tranche inférieure",
    "Burkina Faso": "Revenu faible",
    "Cote d'Ivoire": "Revenu intermédiaire, tranche inférieure",
    "Ghana": "Revenu intermédiaire, tranche inférieure",
    "Mali": "Revenu faible",
    "Niger": "Revenu faible",
    "Nigeria": "Revenu intermédiaire, tranche inférieure",
    "Senegal": "Revenu intermédiaire, tranche inférieure",
    "Togo": "Revenu faible",
}

INDICATEURS_CIBLES = [
    "Incidence du paludisme",
    "Mortalité maternelle",
    "Couverture soins prénataux",
]

DATA_FILENAME = "../Data_Final/data.csv"  # le fichier doit être à côté de app.py (ou adapter le chemin)


# --- 2. CHARGEMENT ET PRÉPARATION DES DONNÉES ---
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Nettoyage ciblé : on ne supprime une ligne que si SA valeur est manquante,
    # jamais sur la base d'une colonne annexe (contrairement à un dropna() global,
    # qui purgerait silencieusement des lignes valides en format long).
    df = df.dropna(subset=["Valeur"]).copy()

    # Contrôle qualité (visible en cas d'anomalie future, pas juste une purge silencieuse)
    doublons = df.duplicated(subset=["Entity", "Year", "Indicateur"]).sum()
    if doublons > 0:
        st.sidebar.warning(f"⚠️ {doublons} doublons détectés (Entity+Year+Indicateur) et ignorés.")
        df = df.drop_duplicates(subset=["Entity", "Year", "Indicateur"])

    # Enrichissement : nom d'affichage FR, région OMS, groupe de revenus
    df["Pays"] = df["Entity"].map(NOMS_AFFICHAGE).fillna(df["Entity"])
    df["Region_OMS"] = REGION_OMS
    df["Groupe_Revenus"] = df["Entity"].map(GROUPE_REVENUS).fillna("Non renseigné")

    return df


data_path = "../Data_Final/data.csv"
try:
    df_raw = load_data(data_path)
except FileNotFoundError:
    st.error(
        f"Fichier introuvable : `{data_path}`.\n\n"
        f"Place `{DATA_FILENAME}` dans le même dossier que `app.py`, "
        f"ou modifie `DATA_FILENAME` en tête de script."
    )
    st.stop()
except Exception as e:
    st.error(f"Erreur lors du chargement de '{DATA_FILENAME}': {e}")
    st.stop()

# --- Titre Principal ---
st.title("🩺 Tableau de Bord Analytique : Santé Publique en Afrique de l'Ouest")
st.markdown("""
Ce tableau de bord interactif permet de suivre et de comparer l'évolution d'indicateurs clés de santé publique,
avec un focus particulier sur le **Sénégal** et ses voisins d'Afrique de l'Ouest (2000-2022).
""")

# --- Barre Latérale (Filtres Globaux) ---
st.sidebar.header("🔍 Filtres Globaux")

liste_pays = sorted(df_raw["Pays"].unique())
pays_affiches_defaut = [NOMS_AFFICHAGE.get(p, p) for p in
                        ["Senegal", "Benin", "Burkina Faso", "Mali", "Niger"]]

pays_selectionnes_fr = st.sidebar.multiselect(
    "Sélectionnez les pays à analyser :",
    options=liste_pays,
    default=pays_affiches_defaut,
)

groupe_revenus_options = sorted(df_raw["Groupe_Revenus"].unique())
groupes_selectionnes = st.sidebar.multiselect(
    "Filtrer par groupe de revenus (Banque Mondiale, FY26) :",
    options=groupe_revenus_options,
    default=groupe_revenus_options,
)

annee_min, annee_max = int(df_raw["Year"].min()), int(df_raw["Year"].max())
annee_range = st.sidebar.slider(
    "Plage d'années :",
    min_value=annee_min,
    max_value=annee_max,
    value=(annee_min, annee_max),
)

st.sidebar.caption(
    "Région OMS : toutes les données couvrent la région **AFRO** (Afrique) de l'OMS."
)

# Filtrage du dataset global selon la barre latérale (utilisé partout, y compris la carte)
df_filtered = df_raw[
    (df_raw["Pays"].isin(pays_selectionnes_fr)) &
    (df_raw["Groupe_Revenus"].isin(groupes_selectionnes)) &
    (df_raw["Year"].between(annee_range[0], annee_range[1]))
]

if df_filtered.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés dans la barre latérale.")

# --- 3. CRÉATION DES ONGLETS ---
tab1, tab2, tab3 = st.tabs([
    "📈 Évolution Temporelle",
    "📊 Comparaison entre Pays",
    "🌍 Analyse Géographique / Cartographie",
])

# =====================================================================
# ONGLET 1 : ÉVOLUTION TEMPORELLE
# =====================================================================
with tab1:
    st.header("📈 Évolution Temporelle des Indicateurs")
    st.markdown("Suivez la trajectoire historique des variables cibles pour les pays sélectionnés.")

    indicateur_choisi = st.selectbox(
        "Choisissez l'indicateur à visualiser :",
        options=INDICATEURS_CIBLES,
        key="sub_tab1",
    )

    df_line = df_filtered[df_filtered["Indicateur"] == indicateur_choisi]

    if not df_line.empty:
        unite = df_line["Unite"].iloc[0]

        fig_line = px.line(
            df_line.sort_values("Year"),
            x="Year", y="Valeur", color="Pays",
            markers=True,
            title=f"Évolution de : {indicateur_choisi} ({annee_range[0]} - {annee_range[1]})",
            labels={"Year": "Année", "Valeur": f"Valeur ({unite})", "Pays": "Pays"},
        )
        fig_line.update_layout(hovermode="x unified", legend_title_text="Pays")
        st.plotly_chart(fig_line, use_container_width=True)

        # Focus KPIs pour le Sénégal
        if "Sénégal" in pays_selectionnes_fr:
            st.subheader("Focus Sénégal 🇸🇳")
            df_senegal = df_line[df_line["Pays"] == "Sénégal"].sort_values("Year")
            if not df_senegal.empty:
                col1, col2, col3 = st.columns(3)
                val_initiale = df_senegal["Valeur"].iloc[0]
                val_finale = df_senegal["Valeur"].iloc[-1]
                annee_init = int(df_senegal["Year"].iloc[0])
                annee_fin = int(df_senegal["Year"].iloc[-1])
                evolution = val_finale - val_initiale
                evolution_pct = (evolution / val_initiale * 100) if val_initiale else float("nan")

                col1.metric(label=f"Valeur en {annee_init}", value=f"{val_initiale:.1f} {unite}")
                col2.metric(label=f"Valeur en {annee_fin}", value=f"{val_finale:.1f} {unite}")
                col3.metric(
                    label="Évolution",
                    value=f"{evolution:+.1f} {unite}",
                    delta=f"{evolution_pct:+.1f}%",
                    delta_color="inverse" if ("Mortalité" in indicateur_choisi or "Incidence" in indicateur_choisi) else "normal",
                )
    else:
        st.warning("Aucune donnée disponible pour cet indicateur avec les filtres sélectionnés.")

# =====================================================================
# ONGLET 2 : COMPARAISON ENTRE PAYS
# =====================================================================
with tab2:
    st.header("📊 Comparaison Transversale entre Pays")
    st.markdown("Comparez la situation de plusieurs nations africaines à une année précise.")

    if not df_filtered.empty:
        annee_comparaison = st.selectbox(
            "Sélectionnez l'année de comparaison :",
            options=sorted(df_filtered["Year"].unique(), reverse=True),
            key="sub_tab2",
        )

        indicateurs_comparaison = INDICATEURS_CIBLES + ["Dépenses de santé", "Espérance de vie"]
        indicateurs_comparaison = [i for i in indicateurs_comparaison if i in df_filtered["Indicateur"].unique()]

        indicateur_choisi_comp = st.selectbox(
            "Choisissez l'indicateur pour la comparaison :",
            options=indicateurs_comparaison,
            key="sub_tab2_ind",
        )

        df_bar = df_filtered[
            (df_filtered["Year"] == annee_comparaison) &
            (df_filtered["Indicateur"] == indicateur_choisi_comp)
        ].sort_values("Valeur", ascending=False)

        if not df_bar.empty:
            unite_bar = df_bar["Unite"].iloc[0]

            fig_bar = px.bar(
                df_bar, x="Pays", y="Valeur", color="Pays",
                title=f"Classement des pays pour '{indicateur_choisi_comp}' en {annee_comparaison}",
                labels={"Pays": "Pays", "Valeur": f"Valeur ({unite_bar})"},
                text_auto=".1f",
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("Données brutes de comparaison")
            st.dataframe(
                df_bar[["Pays", "Code", "Year", "Valeur", "Unite", "Groupe_Revenus"]].reset_index(drop=True),
                use_container_width=True,
            )
        else:
            st.info(f"Aucune donnée disponible pour '{indicateur_choisi_comp}' en {annee_comparaison}.")
    else:
        st.info("Ajustez les filtres pour afficher une comparaison.")

# =====================================================================
# ONGLET 3 : ANALYSE GÉOGRAPHIQUE / CARTOGRAPHIE
# =====================================================================
with tab3:
    st.header("🌍 Carte Choroplèthe Régionale & Continentale")

    st.subheader("Vue Macro : Afrique de l'Ouest")
    st.markdown(
        "Visualisation de l'indicateur à l'échelle des pays sélectionnés dans la barre latérale, "
        "cartographiés grâce à leurs codes ISO3."
    )

    if not df_filtered.empty:
        annee_carte = st.selectbox(
            "Sélectionnez l'année de la carte :",
            options=sorted(df_filtered["Year"].unique(), reverse=True),
            key="sub_tab3",
        )

        indicateur_carte = st.selectbox(
            "Choisissez l'indicateur cartographique :",
            options=[i for i in INDICATEURS_CIBLES if i in df_filtered["Indicateur"].unique()],
            key="sub_tab3_ind",
        )

        df_map = df_filtered[
            (df_filtered["Year"] == annee_carte) &
            (df_filtered["Indicateur"] == indicateur_carte)
        ]

        if not df_map.empty:
            echelle_couleur = "YlGnBu" if indicateur_carte == "Couverture soins prénataux" else "Reds"

            fig_map = px.choropleth(
                df_map,
                locations="Code", color="Valeur", hover_name="Pays",
                color_continuous_scale=echelle_couleur,
                title=f"Carte de : {indicateur_carte} en {annee_carte}",
                labels={"Valeur": df_map["Unite"].iloc[0]},
                scope="africa",
            )
            fig_map.update_geos(
                showcountries=True, countrycolor="Black",
                showsubunits=True, subunitcolor="Blue",
                lonaxis_range=[-25, 15],
                lataxis_range=[0, 25],
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Données insuffisantes pour générer la carte avec les filtres actuels.")
    else:
        st.info("Ajustez les filtres pour afficher la carte.")

    st.divider()

    st.subheader("📍 Zoom Régional : Sénégal")
    st.info("""
    **Note sur les données géographiques infranationales :** les données disponibles (OWID, OMS, World Health Data)
    sont agrégées à l'échelle nationale (par pays). Pour une carte choroplèthe détaillée par **régions sénégalaises**
    (Dakar, Saint-Louis, Thiès, etc.), il faudrait joindre un fichier de géométrie GeoJSON des régions du Sénégal
    ainsi qu'un tableau de données régionales — non disponible dans le périmètre actuel du projet.
    """)

st.divider()
st.caption(
    "Sources : Our World in Data (OWID, CC BY 4.0) · World Health Data (Kaggle, enrichissement) · "
    "Classification de revenus : Banque Mondiale FY26. Périmètre : 9 pays d'Afrique de l'Ouest, 2000-2022."
)
