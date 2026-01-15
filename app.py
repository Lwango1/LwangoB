import streamlit as st
import pandas as pd
import os
import datetime

# --- FICHIERS DE SAUVEGARDE ---
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
    st.title("🔐 Accès LwangoB Pro")
    t1, t2 = st.tabs(["Se Connecter", "S'inscrire (Nouveau)"])
    
    with t2:
        st.info("Inscrivez-vous ici pour créer votre accès permanent.")
        n = st.text_input("Nom complet", key="reg_n").strip()
        t = st.text_input("Téléphone", key="reg_t").strip()
        if st.button("Créer mon compte et Entrer"):
            if n and t:
                save_line(USER_FILE, [n, t], ["nom", "tel"])
                st.session_state.auth = True
                st.session_state.user_name = n
                st.success(f"Bienvenue {n} ! Votre compte est prêt.")
                st.rerun()
            else:
                st.error("Veuillez remplir les deux cases.")

    with t1:
        un = st.text_input("Votre Nom", key="log_n").strip()
        ut = st.text_input("Votre Téléphone", type="password", key="log_t").strip()
        if st.button("Entrer dans l'App"):
            db_u = load_data(USER_FILE, ["nom", "tel"])
            if not db_u.empty:
                # Comparaison intelligente (ignore les espaces et majuscules)
                db_u['nom_low'] = db_u['nom'].astype(str).str.lower().str.strip()
                db_u['tel_str'] = db_u['tel'].astype(str).str.strip()
                
                user_match = db_u[(db_u['nom_low'] == un.lower()) & (db_u['tel_str'] == ut)]
                
                if not user_match.empty:
                    st.session_state.auth = True
                    st.session_state.user_name = user_match.iloc[0]['nom']
                    st.rerun()
                else:
                    st.error("Identifiants inconnus. Vérifiez ou créez un compte.")
            else:
                st.warning("Aucun utilisateur dans la base. Inscrivez-vous d'abord.")

# --- APPLICATION PRINCIPALE ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    menu = st.sidebar.radio("Navigation", ["📈 Ventes", "📦 Stock", "💬 Messagerie"])
    
    if st.sidebar.button("Quitter l'application"):
        st.session_state.auth = False
        st.rerun()

    # --- ONGLET VENTES ---
    if menu == "📈 Ventes":
        st.header("📲 Nouvelle Vente")
        db_a = load_data(ART_FILE, ["nom_article"])
        if db_a.empty:
            st.warning("Ajoutez des articles dans l'onglet 'Stock' avant de vendre.")
        else:
            article = st.selectbox("Article vendu", db_a['nom_article'].tolist())
            qty = st.number_input("Quantité", min_value=1, value=1)
            if st.button("Enregistrer la vente"):
                dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                save_line(VENTE_FILE, [dt, article, qty, st.session_state.user_name], ["date", "article", "qty", "vendeur"])
                st.success("Vente validée et sauvegardée !")
        
        st.subheader("Historique des ventes")
        st.dataframe(load_data(VENTE_FILE, ["date", "article", "qty", "vendeur"]).iloc[::-1])

    # --- ONGLET STOCK ---
    elif menu == "📦 Stock":
        st.header("📦 Gestion du Catalogue")
        n_art = st.text_input("Nom de l'article à ajouter")
        if st.button("Ajouter au Stock"):
            if n_art:
                save_line(ART_FILE, [n_art], ["nom_article"])
                st.success(f"{n_art} est maintenant disponible.")
                st.rerun()
        
        st.subheader("Articles enregistrés")
        st.table(load_data(ART_FILE, ["nom_article"]))

    # --- ONGLET MESSAGERIE ---
    elif menu == "💬 Messagerie":
        st.header("💬 Boîte de communication")
        db_u = load_data(USER_FILE, ["nom", "tel"])
        collegues = db_u[db_u['nom'] != st.session_state.user_name]['nom'].tolist()
        
        opt = st.radio("Destinataire", ["Tout le groupe", "Un collègue spécifique"], horizontal=True)
        target = "GROUPE"
        if opt == "Un collègue spécifique" and collegues:
            target = st.selectbox("Choisir le destinataire", collegues)
        
        m_txt = st.text_area("Votre message")
        if st.button("Envoyer"):
            if m_txt:
                dt_m = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                save_line(MSG_FILE, [dt_m, st.session_state.user_name, target, m_txt], ["date", "exp", "dest", "msg"])
                st.toast("Message transmis !")
                st.rerun()

        st.divider()
        st.subheader("📥 Messages reçus & Groupe")
        db_m = load_data(MSG_FILE, ["date", "exp", "dest", "msg"])
        if not db_m.empty:
            filtre = (db_m['dest'] == st.session_state.user_name) | (db_m['dest'] == "GROUPE") | (db_m['exp'] == st.session_state.user_name)
            for i, r in db_m[filtre].iloc[::-1].iterrows():
                with st.chat_message("user" if r['exp'] == st.session_state.user_name else "assistant"):
                    lbl = "📢 GROUPE" if r['dest'] == "GROUPE" else "🔒 PRIVÉ"
                    st.write(f"**{r['exp']}** ({r['date']}) - *{lbl}*")
                    st.info(r['msg'])
