import streamlit as st
import pandas as pd
import os

# Fichiers
USER_FILE = "users.csv"

def save_user(nom, tel):
    df = pd.DataFrame([[nom, tel]], columns=["nom", "tel"])
    if not os.path.isfile(USER_FILE):
        df.to_csv(USER_FILE, index=False)
    else:
        df.to_csv(USER_FILE, mode='a', header=False, index=False)

st.title("LwangoB Pro")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab2:
        n = st.text_input("Nom complet")
        t = st.text_input("Téléphone")
        if st.button("Créer mon compte"):
            save_user(n, t)
            st.success("Compte créé ! Allez sur l'onglet Connexion")
    with tab1:
        un = st.text_input("Votre Nom")
        ut = st.text_input("Votre Tel", type="password")
        if st.button("Se connecter"):
            if os.path.isfile(USER_FILE):
                db = pd.read_csv(USER_FILE)
                if not db[(db['nom'] == un) & (db['tel'].astype(str) == ut)].empty:
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Identifiants inconnus")
else:
    st.write("Bienvenue dans LwangoB !")
    if st.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()
