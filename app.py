import streamlit as st
import wikipediaapi
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado AI Pro", page_icon="🎬", layout="wide")

# DESIGN (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { 
        background-color: #FF8C00; color: black; border-radius: 12px; 
        font-weight: bold; width: 100%; transition: 0.3s; border: none;
    }
    .stButton>button:hover { background-color: #FFA500; transform: translateY(-2px); }
    h1, h2 { color: #FF8C00; font-family: 'Orbitron', sans-serif; }
    .sidebar .sidebar-content { background-color: #1c1f26; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÍ PANEL (ROLETA) ---
with st.sidebar:
    st.title("⚙️ NASTAVENÍ")
    jmeno_tvurce = st.text_input("Tvé jméno:", "Tvůrce")
    st.divider()
    
    st.subheader("🧪 KREATIVNÍ LABORKA")
    if st.button("🎲 Náhodný nápad na Shorts"):
        napady = ["Den v životě střihače", "Top 3 YouCut triky", "Jak nepokazit barvy", "Můj setup za 0 Kč"]
        st.warning(random.choice(napady))
    
    st.divider()
    st.info(f"Přihlášen jako: {jmeno_tvurce}")
    st.write("Verze: 2.6 (Sidebar Edition)")

# --- HLAVNÍ PLOCHA ---
st.title("🎬 ULTRADO v2.6 PRO")

vstup = st.text_input("💡 O čem bude tvé další video?", placeholder="Napiš téma sem...")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Produkce")
    if st.button("✂️ YouCut Expert"):
        st.info("TIP: Pro plynulý přechod zkus 'Fade out' na konci každého klipu o 0.2s.")
        
    if st.button("📺 Generátor Názvů"):
        if vstup:
            nazvy = [f"Nikdy nezkoušej {vstup}!", f"Jak jsem ovládl {vstup}", f"Pravda o {vstup}, kterou neznáš"]
            st.success(random.choice(nazvy))
        else: st.error("Napiš téma!")

with col2:
    st.subheader("✍️ Obsah")
    if st.button("📖 Fakta z Wikipedie"):
        if vstup:
            wiki = wikipediaapi.Wikipedia(language='cs', user_agent='UltradoWeb/1.0')
            page = wiki.page(vstup)
            if page.exists():
                st.write(f"**{page.title}**: {page.summary[:250]}...")
            else: st.error("Nenalezeno.")
        else: st.warning("Zadej téma!")

    if st.button("🔥 Brutální Hook"):
        hooks = [f"Vsadím se, že o {vstup} jsi tohle nevěděl!", f"Zastav! Pokud tě zajímá {vstup}, poslouchej."]
        st.warning(random.choice(hooks) if vstup else "Chybí téma!")

st.divider()

# SCÉNÁŘ SEKCE
if st.button("📝 VYGENEROVAT RYCHLÝ SCÉNÁŘ"):
    if vstup:
        st.success(f"Plán pro {jmeno_tvurce}:")
        tab1, tab2 = st.tabs(["Střih", "Mluvené slovo"])
        with tab1:
            st.write("- 0:00 - Zoom na obličej\n- 0:05 - Textový popisek\n- 0:15 - Zrychlený záběr")
        with tab2:
            st.write(f"Ahoj, dneska se podíváme na {vstup}. Tohle video tě naučí všechno důležité!")
    else:
        st.error("Musíš zadat téma videa!")
