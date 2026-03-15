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

# --- INICIALIZACE PAMĚTI PRO KALKULAČKU ---
if 'num1' not in st.session_state: st.session_state.num1 = 0.0
if 'num2' not in st.session_state: st.session_state.num2 = 0.0

def reset_calc():
    st.session_state.num1 = 0.0
    st.session_state.num2 = 0.0

# --- BOČNÍ PANEL (ROLETA) ---
with st.sidebar:
    st.title("⚡ ULTRADO 2.0")
    
    # --- SOCIÁLNÍ SÍTĚ ---
    st.subheader("🔍 HLEDAT NA SÍTÍCH")
    search_query = st.text_input("Hledat trend pro:", placeholder="Např. parkour...")
    if search_query:
        st.write("Odkazy pro rychlý průzkum:")
        st.markdown(f"👉 [YouTube](https://www.youtube.com/results?search_query={search_query})")
        st.markdown(f"👉 [TikTok](https://www.tiktok.com/search?q={search_query})")
        st.markdown(f"👉 [Instagram](https://www.instagram.com/explore/tags/{search_query.replace(' ', '')}/)")

    st.divider()

    # --- HUDBA TOP 100 ---
    with st.expander("🎵 TOP 100 HUDBA (Trendy)"):
        st.write("Inspirace pro podmaz:")
        top_songs = ["1. Cruel Summer - Taylor Swift", "2. Paint The Town Red - Doja Cat", "3. Greedy - Tate McRae", "4. Water - Tyla", "5. Houdini - Dua Lipa"]
        for song in top_songs: st.write(song)
        st.caption("[Billboard Hot 100](https://www.billboard.com/charts/hot-100/)")

    # --- KALKULAČKA S REZETEM ---
    with st.expander("🔢 Kalkulačka"):
        n1 = st.number_input("Číslo 1", value=st.session_state.num1, key="n1")
        n2 = st.number_input("Číslo 2", value=st.session_state.num2, key="n2")
        operace = st.selectbox("Operace", ["+", "-", "*", "/"])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Vypočítej"):
                if operace == "+": res = n1 + n2
                elif operace == "-": res = n1 - n2
                elif operace == "*": res = n1 * n2
                elif operace == "/": res = n1 / n2 if n2 != 0 else "Nula!"
                st.code(f"= {res}")
        with c2:
            if st.button("Smazat"):
                reset_calc()
                st.rerun()

    st.divider()
    if st.button("🎲 Rychlý nápad"):
        st.warning(random.choice(["Vlog z nákupu", "Moje ranní rutina", "Tutoriál na YouCut"]))

# --- HLAVNÍ PLOCHA ---
st.title("🎬 HLAVNÍ PANEL ULTRADO")

vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Zadej téma videa...")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎥 Produkce")
    if st.button("✂️ YouCut Tipy"):
        st.info("Zkus funkci 'Curve' u rychlosti pro profi zrychlení/zpomalení.")
    if st.button("📺 Návrhy názvů"):
        if vstup: st.success(random.choice([f"Šílený {vstup}!", f"Jak na {vstup}", f"TOP 5 {vstup}"]))
        else: st.error("Napiš téma!")

with col2:
    st.subheader("📚 Rešerše")
    if st.button("📖 Wikipedie"):
        if vstup:
            wiki = wikipediaapi.Wikipedia(language='cs', user_agent='UltradoWeb/1.0')
            page = wiki.page(vstup)
            if page.exists(): st.write(page.summary[:200] + "...")
            else: st.error("Nenalezeno.")
        else: st.warning("Chybí téma.")

st.divider()
if st.button("📝 GENERUJ PLÁN VIDEA"):
    if vstup:
        st.balloons()
        st.write(f"### Plán pro: {vstup}")
        st.write("1. Úvod: 3 sekundy hook\n2. Obsah: Hlavní část\n3. Outro: Odběr")
    else: st.error("Zadej téma!")

