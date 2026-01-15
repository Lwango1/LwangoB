import streamlit as st
import pandas as pd
import os
import datetime

# --- FICHIERS DE SAUVEGARDE PERMANENTE ---
USER_FILE = "users.csv"
ART_FILE = "articles.csv"
VENTE_FILE = "ventes.csv"
MSG_FILE = "messages_v3.csv" 

# Fonction pour charger les données sans erreur
def load_data(file, columns):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# Fonction pour sauvegarder proprement
def save_line(file, data, columns):
    df_new = pd.DataFrame([data], columns=columns)
    if not os.path.isfile(file) or os.stat(file).st_size == 0:
        df_new.to_csv(file, index=False)
    else:
        df_new.to_csv(file, mode='a', header=False, index=False)

# Configuration
st.set_page_config(page_title="LwangoB Pro", page_icon="🏍️")

# Initialisation de la session
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

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
                st.success(f"Bienvenue {n} !")
                st.rerun()
            else:
                st.error("Remplissez les deux cases.")

    with t1:
        un = st.text_input("Nom", key="log_n")
        ut = st.text_input("Tel (Sert de mot de passe)", type="password", key="log_t")
        if st.button("Se connecter"):
            db_u = load_data(USER_FILE, ["nom", "tel"])
            if not db_u.empty:
                # On s'assure que la comparaison se fait en texte (string)
                user_match = db_u[(db_u['nom'] == un) & (db_u['tel'].astype(str) == str(ut))]
                if not user_match.empty:
                    st.session_state.auth = True
                    st.session_state.user_name = un
                    st.rerun()
                else:
                    st.error("Nom ou téléphone incorrect.")
            else:
                st.error("Aucun utilisateur inscrit. Allez sur l'onglet Inscription.")

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
            st.warning("Ajoutez d'abord des articles dans le Stock.")
        else:
            article = st.selectbox("Choisir l'article", db_a['nom_article'].tolist())
            quantite = st.number_input("Quantité", min_value=1, value=1)
            if st.button("Valider la vente"):
                date_v = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                save_line(VENTE_FILE, [date_v, article, quantite, st.session_state.user_name], ["date", "article", "qty", "vendeur"])
                st.success("Vente enregistrée !")
        
        st.subheader("Historique récent")
        st.dataframe(load_data(VENTE_FILE, ["date", "article", "qty", "vendeur"]).tail(10))

    # --- ONGLET STOCK ---
    elif menu == "📦 Gestion Stock":
        st.header("📦 Catalogue Articles")
        nom_art = st.text_input("Nom de la pièce ou moto")
        if st.button("Ajouter définitivement"):
            if nom_art:
                save_line(ART_FILE, [nom_art], ["nom_article"])
                st.success(f"{nom_art} ajouté au stock !")
        st.table(load_data(ART_FILE, ["nom_article"]))

    # --- ONGLET MESSAGERIE ---
    elif menu == "💬 Messagerie Team":
        st.header("💬 Communication")
        
        db_u = load_data(USER_FILE, ["nom", "tel"])
        collegues = db_u[db_u['nom'] != st.session_state.user_name]['nom'].tolist()
        
        type_msg = st.radio("Destinataire :", ["Groupe (Tout le monde)", "Privé (Un collègue)"], horizontal=True)
        
        dest = "GROUPE"
        if type_msg == "Privé (Un collègue)":
            if collegues:
                dest = st.selectbox("Choisir le collègue", collegues)
            else:
                st.info("Vous êtes seul pour le moment.")
                dest = None

        msg_text = st.text_area("Votre message")
        if st.button("Envoyer"):
            if msg_text and dest:
                date_m = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                save_line(MSG_FILE, [date_m, st.session_state.user_name, dest, msg_text], ["date", "exp", "dest", "msg"])
                st.success("Message envoyé !")
                st.rerun()

        st.divider()
        st.subheader("📥 Discussions")
        db_m = load_data(MSG_FILE, ["date", "exp", "dest", "msg"])
        
        if not db_m.empty:
            # Filtre : messages pour moi, messages de groupe, ou messages que j'ai envoyés
            mes_echanges = db_m[(db_m['dest'] == st.session_state.user_name) | 
                                (db_m['dest'] == "GROUPE") | 
                                (db_m['exp'] == st.session_state.user_name)]
            
            for i, row in mes_echanges.iloc[::-1].iterrows():
                tag = "📢 GROUPE" if row['dest'] == "GROUPE" else "🔒 PRIVÉ"
                header = f"**{row['exp']}** ➔ **{row['dest']}** | _{row['date']}_ ({tag})"
                st.write(header)
                st.info(row['msg'])
        else:
            st.write("Aucun message.")
