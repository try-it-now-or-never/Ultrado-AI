import streamlit as st
import wikipediaapi
import random
from deep_translator import GoogleTranslator

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado 2.0", page_icon="⚡", layout="wide")

# --- DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #FF8C00; color: black; border-radius: 10px; font-weight: bold; width: 100%; border: none; }
    h1, h2, h3 { color: #FF8C00; font-family: 'Orbitron', sans-serif; }
    .stTextInput>div>div>input { background-color: #1c1f26; color: white; border: 1px solid #FF8C00; }
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
    
    # 1. SLEDOVAČ ODBĚRATELŮ (CÍLE)
    st.subheader("📊 CESTA KE SLÁVĚ")
    aktualni = st.number_input("Mám odběratelů:", value=0)
    cil = st.number_input("Můj cíl (subs):", value=100)
    if cil > 0:
        procenta = min(100, int((aktualni / cil) * 100))
        st.progress(procenta / 100)
        st.write(f"Jsi na {procenta}% cesty k {cil} subs!")
        if aktualni >= cil and aktualni > 0:
            st.success("CÍL SPLNĚN! 🏆")
            st.balloons()

    st.divider()

    # 2. HLEDÁNÍ NA SÍTÍCH
    with st.expander("🔍 HLEDAT TRENDY"):
        q = st.text_input("Téma k hledání:")
        if q:
            st.markdown(f"👉 [YouTube](https://www.youtube.com/results?search_query={q})")
            st.markdown(f"👉 [TikTok](https://www.tiktok.com/search?q={q})")

    # 3. HUDBA TOP 100
    with st.expander("🎵 HUDEBNÍ TRENDY"):
        songs = ["1. Cruel Summer", "2. Paint The Town Red", "3. Greedy", "4. Water", "5. Houdini", "6. Lovin On Me"]
        for s in songs: st.write(s)
        st.caption("[Billboard Top 100](https://www.billboard.com/charts/hot-100/)")

    # 4. PŘEKLADAČ
    with st.expander("🌍 PŘEKLADAČ"):
        t = st.text_area("Český text:")
        if st.button("Přeložit do EN"):
            if t:
                preklad = GoogleTranslator(source='cs', target='en').translate(t)
                st.success(preklad)

    # 5. KALKULAČKA
    with st.expander("🔢 KALKULAČKA"):
        n1 = st.number_input("Číslo 1", value=st.session_state.num1, key="n1")
        n2 = st.number_input("Číslo 2", value=st.session_state.num2, key="n2")
        op = st.selectbox("Operace", ["+", "-", "*", "/"])
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Vypočítej"):
                if op == "+": res = n1+n2
                elif op == "-": res = n1-n2
                elif op == "*": res = n1*n2
                elif op == "/": res = n1/n2 if n2 != 0 else "Nula!"
                st.code(res)
        with c2:
            if st.button("Reset"):
                reset_calc()
                st.rerun()

    st.divider()
    if st.button("🎲 NÁHODNÝ NÁPAD"):
        st.warning(random.choice(["Vlog", "Tutorial", "Gaming", "Shorts"]))

# --- HLAVNÍ PLOCHA ---
st.title("🎬 HLAVNÍ PANEL")
vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Napiš téma videa...")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🎥 Produkce")
    if st.button("✂️ YouCut Tipy"): st.info("Zkus 'Curve' u rychlosti pro profi efekt!")
    if st.button("📺 Návrhy názvů"):
        if vstup: st.success(random.choice([f"Šílený {vstup}!", f"Jak na {vstup}", f"Pravda o {vstup}"]))
    if st.button("🔥 Brutální Hook"):
        if vstup: st.warning(f"Vsadím se, že o {vstup} jsi tohle nevěděl!")

with col2:
    st.subheader("📚 Rešerše")
    if st.button("📖 Wikipedie"):
        if vstup:
            wiki = wikipediaapi.Wikipedia(language='cs', user_agent='Ultrado/1.0')
            page = wiki.page(vstup)
            if page.exists(): st.write(page.summary[:250] + "...")
            else: st.error("Nenalezeno.")
    if st.button("🏷️ Hashtagy"):
        st.code(f"#{vstup if vstup else 'video'} #youcut #viral #fyp")

st.divider()
if st.button("📝 GENERUJ KOMPLETNÍ PLÁN"):
    if vstup:
        st.balloons()
        st.subheader(f"📋 Plán pro: {vstup}")
        st.write("1. Úvod: Šokující začátek\n2. Střed: Hlavní info\n3. Konec: Odběr!")
    else: st.error("Zadej téma!")
