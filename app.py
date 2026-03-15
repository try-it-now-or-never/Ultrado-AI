import streamlit as st
import wikipediaapi
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado 2.0", page_icon="⚡", layout="wide")

# DESIGN (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { 
        background-color: #FF8C00; color: black; border-radius: 10px; 
        font-weight: bold; width: 100%; transition: 0.2s; border: none;
    }
    .stButton>button:hover { background-color: #FFA500; transform: scale(1.02); }
    h1, h2, h3 { color: #FF8C00; font-family: 'Orbitron', sans-serif; }
    .stTextInput>div>div>input { background-color: #1c1f26; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÍ PANEL (ROLETA) ---
with st.sidebar:
    st.title("⚡ ULTRADO 2.0")
    st.subheader("🛠️ EXTRA FUNKCE")
    
    # --- KALKULAČKA ---
    with st.expander("🔢 Kalkulačka"):
        num1 = st.number_input("Číslo 1", value=0.0)
        num2 = st.number_input("Číslo 2", value=0.0)
        operace = st.selectbox("Operace", ["+", "-", "*", "/"])
        if st.button("Vypočítej"):
            if operace == "+": vysledek = num1 + num2
            elif operace == "-": vysledek = num1 - num2
            elif operace == "*": vysledek = num1 * num2
            elif operace == "/": vysledek = num1 / num2 if num2 != 0 else "Nelze dělit nulou"
            st.code(f"Výsledek: {vysledek}")

    # --- PŘEKLADAČ ---
    with st.expander("🌍 Překladač (CZ -> EN)"):
        text_to_translate = st.text_area("Text k překladu:")
        if st.button("Přeložit (Demo)"):
            # Poznámka: Pro reálný překlad by byla potřeba knihovna googletrans, 
            # toto je zjednodušená verze pro rychlost.
            st.info("Tip: Pro plnohodnotný překladač propojíme Google API. Teď zkus DeepL nebo Google.")
            st.write(f"Zatím zkopíruj sem: [Google Translate](https://translate.google.com/?sl=cs&tl=en&text={text_to_translate})")

    st.divider()
    if st.button("🎲 Nápad na video"):
        st.warning(random.choice(["Setup tour", "Reakce na komenty", "Challenge v YouCutu"]))

# --- HLAVNÍ PLOCHA ---
st.title("🎬 HLAVNÍ PANEL ULTRADO")

vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Zadej téma videa...")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎥 Produkce")
    if st.button("✂️ YouCut Tipy"):
        st.info("Zkus funkci 'Curve' u rychlosti pro profi zrychlení/zpomalení.")
    if st.button("📺 Návrhy názvů"):
        if vstup:
            st.success(random.choice([f"Šílený {vstup}!", f"Jak na {vstup}", f"TOP 5 {vstup}"]))
        else: st.error("Napiš téma!")

with col2:
    st.subheader("📚 Rešerše")
    if st.button("📖 Wikipedie"):
        if vstup:
            wiki = wikipediaapi.Wikipedia(language='cs', user_agent='UltradoWeb/1.0')
            page = wiki.page(vstup)
            if page.exists():
                st.write(page.summary[:200] + "...")
            else: st.error("Nenalezeno.")
        else: st.warning("Chybí téma.")

st.divider()
if st.button("📝 GENERUJ PLÁN VIDEA"):
    if vstup:
        st.balloons()
        st.write(f"### Plán pro: {vstup}")
        st.write("1. Úvod: 3 sekundy hook\n2. Obsah: Hlavní část\n3. Outro: Odběr")
    else:
        st.error("Zadej téma!")
