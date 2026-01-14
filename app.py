import streamlit as st
import pandas as pd
import os

# Fichiers de sauvegarde permanente
USER_FILE = "users.csv"

# Fonction pour enregistrer un nouvel utilisateur
def save_user(nom, tel):
    df = pd.DataFrame([[nom, tel]], columns=["nom", "tel"])
    if not os.path.isfile(USER_FILE):
        df.to_csv(USER_FILE, index=False)
    else:
        df.to_csv(USER_FILE, mode='a', header=False, index=False)

st.title("LwangoB Pro")

# Initialisation de la session
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- ÉCRAN D'ACCÈS ---
if not st.session_state.auth:
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab2:
        n = st.text_input("Nom complet", key="reg_nom")
        t = st.text_input("Téléphone", key="reg_tel")
        if st.button("S'inscrire et Entrer"):
            if n and t:
                save_user(n, t)
                # CONNEXION AUTOMATIQUE ICI
                st.session_state.auth = True
                st.session_state.user_name = n
                st.success(f"Bienvenue {n} ! Redirection...")
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs.")

    with tab1:
        un = st.text_input("Votre Nom", key="log_nom")
        ut = st.text_input("Votre Tel", type="password", key="log_tel")
        if st.button("Se connecter"):
            if os.path.isfile(USER_FILE):
                db = pd.read_csv(USER_FILE)
                # Vérification
                user_match = db[(db['nom'] == un) & (db['tel'].astype(str) == ut)]
                if not user_match.empty:
                    st.session_state.auth = True
                    st.session_state.user_name = un
                    st.rerun()
                else:
                    st.error("Identifiants inconnus. Vérifiez le nom ou inscrivez-vous.")
            else:
                st.error("Aucun utilisateur enregistré. Veuillez vous inscrire.")

# --- INTERFACE DE L'APP (UNE FOIS CONNECTÉ) ---
else:
    st.sidebar.success(f"Connecté : {st.session_state.user_name}")
    st.header(f"👋 Bienvenue dans l'interface LwangoB, {st.session_state.user_name}")
    
    # Ajoutez ici vos boutons de gestion de stock et ventes
    if st.button("Déconnexion"):
        st.session_state.auth = False
        st.session_state.user_name = ""
        st.rerun()
