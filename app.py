import streamlit as st
import pandas as pd
import os
import datetime

# --- FICHIERS DE SAUVEGARDE ---
USER_FILE = "users_data.csv"
ART_FILE = "articles_data.csv"
VEND_FILE = "ventes_data.csv"

# Fonction pour charger/créer les fichiers
def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# Chargement permanent
df_users = load_data(USER_FILE, ["nom", "tel"])
df_arts = load_data(ART_FILE, ["nom_article"])
df_ventes = load_data(VEND_FILE, ["date", "article", "vendeur"])

# --- CONFIGURATION ---
st.set_page_config(page_title="LwangoB Pro", layout="centered")

if 'utilisateur_connecte' not in st.session_state:
    st.session_state.utilisateur_connecte = None

# --- CONNEXION ---
if st.session_state.utilisateur_connecte is None:
    st.title("🔐 Connexion LwangoB")
    t1, t2 = st.tabs(["Se connecter", "S'inscrire"])
    
    with t1:
        u = st.text_input("Nom")
        p = st.text_input("Téléphone", type="password")
        if st.button("Entrer"):
            if not df_users[(df_users['nom'] == u) & (df_users['tel'] == p)].empty:
                st.session_state.utilisateur_connecte = u
                st.rerun()
            else: st.error("Inconnu")
            
    with t2:
        nu = st.text_input("Nom complet")
        nt = st.text_input("Numéro")
        if st.button("Créer compte"):
            new_u = pd.DataFrame([[nu, nt]], columns=["nom", "tel"])
            pd.concat([df_users, new_u]).to_csv(USER_FILE, index=False)
            st.success("Enregistré ! Connectez-vous.")

else:
    # --- INTERFACE PRINCIPALE ---
    st.sidebar.title(f"👤 {st.session_state.utilisateur_connecte}")
    page = st.sidebar.radio("Menu", ["Ventes", "Gestion Stock"])

    if page == "Ventes":
        st.header("📲 Enregistrer une Vente")
        if df_arts.empty:
            st.warning("Ajoutez d'abord des articles dans 'Gestion Stock'")
        else:
            art = st.selectbox("Article", df_arts['nom_article'].tolist())
            if st.button("Valider la vente"):
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                new_v = pd.DataFrame([[now, art, st.session_state.utilisateur_connecte]], columns=["date", "article", "vendeur"])
                pd.concat([df_ventes, new_v]).to_csv(VEND_FILE, index=False)
                st.toast("Vente enregistrée dans la base !")
        
        st.subheader("Historique (Permanent)")
        st.table(load_data(VEND_FILE, ["date", "article", "vendeur"]).head(10))

    elif page == "Gestion Stock":
        st.header("📦 Catalogue Articles")
        new_art = st.text_input("Nom du nouvel article")
        if st.button("Ajouter définitivement"):
            new_a = pd.DataFrame([[new_art]], columns=["nom_article"])
            pd.concat([df_arts, new_a]).to_csv(ART_FILE, index=False)
            st.success("Article sauvegardé !")
