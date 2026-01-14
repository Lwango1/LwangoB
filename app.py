import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="LwangoB - Gestion Moto", layout="centered", page_icon="🏍️")

# --- INITIALISATION DES DONNÉES ---
if 'utilisateurs' not in st.session_state:
    st.session_state.utilisateurs = {"Daniel": "0812345678"}
# Initialisation de la liste des articles modifiable
if 'liste_articles' not in st.session_state:
    st.session_state.liste_articles = ["Moto Yamaha DT 125", "Moto Haojin", "Kit Chaîne"]
if 'mouvements' not in st.session_state:
    st.session_state.mouvements = []
if 'messages_prives' not in st.session_state:
    st.session_state.messages_prives = []
if 'utilisateur_connecte' not in st.session_state:
    st.session_state.utilisateur_connecte = None

# --- 1. SYSTÈME D'INSCRIPTION / CONNEXION ---
if st.session_state.utilisateur_connecte is None:
    st.title("🔐 Connexion LwangoB")
    tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])

    with tab1:
        nom_login = st.text_input("Nom d'utilisateur")
        tel_login = st.text_input("Numéro de téléphone", type="password", key="login_tel")
        if st.button("Entrer dans l'app"):
            if nom_login in st.session_state.utilisateurs and st.session_state.utilisateurs[nom_login] == tel_login:
                st.session_state.utilisateur_connecte = nom_login
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with tab2:
        nouveau_nom = st.text_input("Votre Nom complet")
        nouveau_tel = st.text_input("Votre Numéro de téléphone (ex: 08...)")
        if st.button("Créer mon compte"):
            if nouveau_nom and nouveau_tel:
                st.session_state.utilisateurs[nouveau_nom] = nouveau_tel
                st.success("Compte créé ! Vous pouvez maintenant vous connecter.")
            else:
                st.warning("Veuillez remplir tous les champs.")
else:
    # --- L'APPLICATION UNE FOIS CONNECTÉ ---
    st.sidebar.title(f"👤 {st.session_state.utilisateur_connecte}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.utilisateur_connecte = None
        st.rerun()

    # AJOUT DE L'OPTION "Gestion du Stock" DANS LE MENU
    page = st.sidebar.radio("Menu LwangoB",
                            ["Flux des ventes", "Gestion du Stock", "Messagerie Privée", "Statistiques"])

    # --- 2. PAGE FLUX DES VENTES ---
    if page == "Flux des ventes":
        st.header("📲 Flux de vente")
        with st.form("vente"):
            # Utilisation de la liste dynamique d'articles
            article = st.selectbox("Choisir l'article vendu", st.session_state.liste_articles)
            if st.form_submit_button("Enregistrer la vente"):
                st.session_state.mouvements.insert(0, {
                    "heure": datetime.datetime.now().strftime("%H:%M"),
                    "item": article,
                    "vendeur": st.session_state.utilisateur_connecte
                })
                st.toast("Vente enregistrée !")

        for m in st.session_state.mouvements:
            st.info(f"**{m['heure']}** : {m['item']} vendu par {m['vendeur']}")

    # --- 3. NOUVELLE PAGE : GESTION DU STOCK (AJOUT D'ARTICLES) ---
    elif page == "Gestion du Stock":
        st.header("📦 Gestion des Articles")

        st.subheader("Ajouter un nouvel article au catalogue")
        with st.form("ajout_article"):
            nouvel_art = st.text_input("Nom de l'article (ex: Pneu arrière, Bougie...)")
            if st.form_submit_button("Ajouter au catalogue"):
                if nouvel_art:
                    if nouvel_art not in st.session_state.liste_articles:
                        st.session_state.liste_articles.append(nouvel_art)
                        st.success(f"'{nouvel_art}' ajouté avec succès !")
                    else:
                        st.warning("Cet article existe déjà.")
                else:
                    st.error("Veuillez saisir un nom d'article.")

        st.divider()
        st.subheader("Articles actuellement disponibles")
        # Affichage de la liste sous forme de tableau
        df_articles = pd.DataFrame(st.session_state.liste_articles, columns=["Nom de l'article"])
        st.table(df_articles)

    # --- 4. MESSAGERIE PRIVÉE ---
    elif page == "Messagerie Privée":
        st.header("💬 Envoyer un message")
        contacts = [u for u in st.session_state.utilisateurs.keys() if u != st.session_state.utilisateur_connecte]

        if not contacts:
            st.warning("Aucun autre contact inscrit pour le moment.")
        else:
            destinataire = st.selectbox("Choisir un contact", contacts)
            contenu = st.text_area("Votre message...")

            if st.button("Envoyer"):
                if contenu:
                    st.session_state.messages_prives.append({
                        "expediteur": st.session_state.utilisateur_connecte,
                        "destinataire": destinataire,
                        "texte": contenu,
                        "heure": datetime.datetime.now().strftime("%H:%M")
                    })
                    st.success(f"Message envoyé à {destinataire}")

        st.divider()
        st.subheader("Mes messages reçus")
        mes_reçus = [m for m in st.session_state.messages_prives if
                     m['destinataire'] == st.session_state.utilisateur_connecte]

        if mes_reçus:
            for m in reversed(mes_reçus):
                with st.chat_message("user"):
                    st.write(f"**De : {m['expediteur']}** ({m['heure']})")
                    st.write(m['texte'])
        else:
            st.write("Aucun message reçu.")

    # --- 5. STATISTIQUES ---
    elif page == "Statistiques":
        st.header("📈 Performances")
        st.line_chart([10, 15, 7, 20, 25])