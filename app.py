import streamlit as st
import wikipediaapi
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado 2.0 Full", page_icon="⚡", layout="wide")

# --- DESIGN (CSS) ---
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
    .sidebar .sidebar-content { background-color: #1c1f26; }
    </style>
    """, unsafe_allow_html=True)

# --- PAMĚŤ PRO KALKULAČKU ---
if 'num1' not in st.session_state: st.session_state.num1 = 0.0
if 'num2' not in st.session_state: st.session_state.num2 = 0.0

def reset_calc():
    st.session_state.num1 = 0.0
    st.session_state.num2 = 0.0

# --- BOČNÍ PANEL (ROLETA) ---
with st.sidebar:
    st.title("⚡ ULTRADO 2.0")
    
    # 1. VYHLEDÁVÁNÍ
    st.subheader("🔍 HLEDAT NA SÍTÍCH")
    search_q = st.text_input("Trend pro:", placeholder="Např. parkour...")
    if search_q:
        st.markdown(f"👉 [YouTube](https://www.youtube.com/results?search_query={search_q})")
        st.markdown(f"👉 [TikTok](https://www.tiktok.com/search?q={search_q})")
        st.markdown(f"👉 [Instagram](https://www.instagram.com/explore/tags/{search_q.replace(' ', '')}/)")

    st.divider()

    # 2. HUDBA
    with st.expander("🎵 TOP 100 HUDBA"):
        st.write("Trendy songy:")
        songs = ["1. Cruel Summer", "2. Paint The Town Red", "3. Greedy", "4. Water", "5. Houdini", "6. Lovin On Me"]
        for s in songs: st.write(s)
        st.caption("[Celý žebříček Billboard](https://www.billboard.com/charts/hot-100/)")

    # 3. PŘEKLADAČ
    with st.expander("🌍 PŘEKLADAČ (CZ -> EN)"):
        txt = st.text_area("Text k překladu:")
        if st.button("Přejít k překladu"):
            st.write(f"👉 [Otevřít v Google Překladači](https://translate.google.com/?sl=cs&tl=en&text={txt})")

    # 4. KALKULAČKA
    with st.expander("🔢 KALKULAČKA"):
        n1 = st.number_input("Číslo 1", value=st.session_state.num1, key="n1")
        n2 = st.number_input("Číslo 2", value=st.session_state.num2, key="n2")
        op = st.selectbox("Operace", ["+", "-", "*", "/"])
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Vypočítej"):
                if op == "+": res = n1 + n2
                elif op == "-": res = n1 - n2
                elif op == "*": res = n1 * n2
                elif op == "/": res = n1 / n2 if n2 != 0 else "Nula!"
                st.code(f"= {res}")
        with c2:
            if st.button("Smazat"):
                reset_calc()
                st.rerun()

    st.divider()
    if st.button("🎲 RYCHLÝ NÁPAD"):
        st.warning(random.choice(["Vlog z nákupu", "Můj setup", "YouCut tutoriál"]))

# --- HLAVNÍ PLOCHA ---
st.title("🎬 HLAVNÍ PANEL ULTRADO")

vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Zadej téma videa...")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎥 Produkce")
    if st.button("✂️ YouCut Tipy"):
        st.info("TIP: Použij 'Curve' u rychlosti pro profi zrychlení záběru.")
    if st.button("📺 Návrhy názvů"):
        if vstup:
            st.success(random.choice([f"Šílený {vstup}!", f"Pravda o {vstup}", f"TOP 5 {vstup}"]))
        else: st.error("Napiš téma!")

with col2:
    st.subheader("📚 Rešerše")
    if st.button("📖 Wikipedie"):
        if vstup:
            wiki = wikipediaapi.Wikipedia(language='cs', user_agent='UltradoWeb/1.0')
            page = wiki.page(vstup)
            if page.exists():
                st.write(page.summary[:250] + "...")
            else: st.error("Nenalezeno.")
        else: st.warning("Chybí téma.")

st.divider()

# GENERÁTOR PLÁNU
if st.button("📝 GENERUJ KOMPLETNÍ PLÁN"):
    if vstup:
        st.balloons()
        st.subheader(f"📋 Scénář a plán pro: {vstup}")
        t1, t2 = st.tabs(["Střih a Vizuál", "Mluvené slovo"])
        with t1:
            st.write("- **0:00-0:03** - Rychlý střih a velký titulek.")
            st.write("- **0:03-0:15** - Dynamické záběry s hudbou z Top 100.")
            st.write("- **Konec** - Výzva k odběru (Call to Action).")
        with t2:
            st.write(f"Dneska vám ukážu {vstup} tak, jak jste ho ještě neviděli!")
    else:
        st.error("Nejdřív musíš napsat téma do políčka nahoře!")
