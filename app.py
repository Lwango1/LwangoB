import streamlit as st
import pandas as pd
import os
import datetime

# --- FICHIERS DE SAUVEGARDE PERMANENTE ---
USER_FILE = "users.csv"
ART_FILE = "articles.csv"
VENTE_FILE = "ventes.csv"
MSG_FILE = "messages_v2.csv" # Utilisation d'une nouvelle version pour les messages

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
        st.header("📦 Catalogue Articles")
        nom_art = st.text_input("Nom de la pièce ou moto")
        if st.button("Ajouter définitivement"):
            if nom_art:
                save_line(ART_FILE, [nom_art], ["nom_article"])
                st.success(f"{nom_art} ajouté !")
        st.subheader("Liste actuelle")
        st.table(load_data(ART_FILE, ["nom_article"]))

    # --- ONGLET MESSAGERIE AVANCÉE ---
    elif menu == "💬 Messagerie Team":
        st.header("💬 Envoyer un message")
        
        # Charger les utilisateurs pour le répertoire
        db_u = load_data(USER_FILE, ["nom", "tel"])
        collegues = db_u[db_u['nom'] != st.session_state.user_name]['nom'].tolist()
        
        # Choix du type de message
        type_msg = st.radio("Type de message", ["Privé (Un seul collègue)", "Groupe (Toute l'équipe)"], horizontal=True)
        
        if type_msg == "Privé (Un seul collègue)":
            if not collegues:
                st.info("Aucun autre collègue inscrit pour le moment.")
                dest = None
            else:
                dest = st.selectbox("Choisir le destinataire", collegues)
        else:
            dest = "GROUPE"

        contenu = st.text_area("Ecrire votre message")
        
        if st.button("Envoyer"):
            if contenu and (dest or type_msg == "Groupe (Toute l'équipe)"):
                date_m = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                save_line(MSG_FILE, [date_m, st.session_state.user_name, dest, contenu], ["date", "exp", "dest", "msg"])
                st.success("Message envoyé !")
            else:
                st.error("Le message est vide ou aucun destinataire sélectionné.")

        st.divider()
        st.subheader("📥 Boîte de réception")
        
        db_m = load_data(MSG_FILE, ["date", "exp", "dest", "msg"])
        
        # Filtrer pour voir : 
        # 1. Les messages qui me sont adressés
        # 2. Les messages de groupe
        # 3. Les messages que j'ai envoyés
        filtre = (db_m['dest'] == st.session_state.user_name) | (db_m['dest'] == "GROUPE") | (db_m['exp'] == st.session_state.user_name)
        mes_echanges = db_m[filtre]

        if mes_echanges.empty:
            st.write("Pas encore de messages.")
        else:
            for i, row in mes_echanges.iloc[::-1].iterrows():
                tag = "📢 [GROUPE]" if row['dest'] == "GROUPE" else f"🔒 [PRIVÉ pour {row['dest']}]"
                if row['exp'] == st.session_state.user_name:
                    color = "blue"
                    exp_name = "Moi"
                else:
                    color = "green"
                    exp_name = row['exp']
                
                st.markdown(f"**{tag}** | _{row['date']}_")
                st.info(f"**{exp_name}** : {row['msg']}")
