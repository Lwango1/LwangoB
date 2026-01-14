import streamlit as st
import pandas as pd
import os
import datetime

# --- FICHIERS DE SAUVEGARDE PERMANENTE ---
USER_FILE = "users.csv"
ART_FILE = "articles.csv"
VENTE_FILE = "ventes.csv"

# Fonction pour charger les données
def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# Fonction pour sauvegarder une ligne
def save_line(file, data, columns):
    df_new = pd.DataFrame([data], columns=columns)
    if not os.path.isfile(file):
        df_new.to_csv(file, index=False)
    else:
        df_new.to_csv(file, mode='a', header=False, index=False)

# Initialisation de l'état de session
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

st.set_page_config(page_title="LwangoB Pro", page_icon="🏍️")

# --- SYSTÈME D'ACCÈS ---
if not st.session_state.auth:
    st.title("🔐 Accès LwangoB")
    t1, t2 = st.tabs(["Connexion", "Inscription Rapide"])
    
    with t2:
        n = st.text_input("Nom complet", key="reg_n")
        t = st.text_input("Numéro de téléphone", key="reg_t")
        if st.button("S'inscrire et Entrer"):
            if n and t:
                save_line(USER_FILE, [n, t], ["nom", "tel"])
                st.session_state.auth = True
                st.session_state.user_name = n
                st.rerun()
            else:
                st.error("Remplissez les deux cases.")

    with t1:
        un = st.text_input("Nom", key="log_n")
        ut = st.text_input("Tel", type="password", key="log_t")
        if st.button("Se connecter"):
            db_u = load_data(USER_FILE, ["nom", "tel"])
            if not db_u[(db_u['nom'] == un) & (db_u['tel'].astype(str) == ut)].empty:
                st.session_state.auth = True
                st.session_state.user_name = un
                st.rerun()
            else:
                st.error("Identifiants inconnus")

# --- APPLICATION PRINCIPALE ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("Menu Principal", ["📈 Ventes", "📦 Gestion Stock", "💬 Messagerie Team"])
    
    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()

    # --- ONGLET VENTES ---
    if menu == "📈 Ventes":
        st.header("📲 Enregistrer une vente")
        db_a = load_data(ART_FILE, ["nom_article"])
        
        if db_a.empty:
            st.warning("Allez dans 'Gestion Stock' pour ajouter des articles d'abord.")
        else:
            article = st.selectbox("Choisir l'article", db_a['nom_article'].tolist())
            quantite = st.number_input("Quantité", min_value=1, value=1)
            if st.button("Valider la vente"):
                date_v = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                save_line(VENTE_FILE, [date_v, article, quantite, st.session_state.user_name], ["date", "article", "qty", "vendeur"])
                st.success("Vente enregistrée !")
        
        st.subheader("Dernières transactions")
        st.dataframe(load_data(VENTE_FILE, ["date", "article", "qty", "vendeur"]).tail(10))

    # --- ONGLET STOCK ---
    elif menu == "📦 Gestion Stock":
        st.header("📦 Ajouter des articles au catalogue")
        nom_art = st.text_input("Nom de la pièce ou moto (ex: Bougie, Pneu, Haojin)")
        if st.button("Ajouter définitivement"):
            if nom_art:
                save_line(ART_FILE, [nom_art], ["nom_article"])
                st.success(f"{nom_art} ajouté au stock !")
            else:
                st.error("Entrez un nom d'article.")
        
        st.subheader("Liste actuelle")
        st.table(load_data(ART_FILE, ["nom_article"]))

    # --- ONGLET MESSAGERIE ---
    elif menu == "💬 Messagerie Team":
        st.header("💬 Communication d'équipe")
        msg = st.text_area("Votre message pour l'équipe")
        if st.button("Diffuser le message"):
            st.toast("Message envoyé à l'équipe !")
            # Note: Pour une messagerie persistante réelle, on pourrait créer un messages.csv ici aussi
