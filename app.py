import streamlit as st
import wikipediaapi
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado AI Pro", page_icon="🎬", layout="wide")

# VYLEPŠENÝ DESIGN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .main { background-color: #0e1117; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { 
        background-color: #FF8C00; 
        color: black; 
        border-radius: 15px; 
        font-weight: bold; 
        height: 3em; 
        width: 100%;
        transition: 0.3s;
        border: none;
        text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #FFA500; transform: scale(1.02); }
    h1 { color: #FF8C00; font-family: 'Orbitron', sans-serif; text-align: center; border-bottom: 2px solid #FF8C00; padding-bottom: 10px; }
    .stTextInput>div>div>input { background-color: #1c1f26; color: #FF8C00; border: 1px solid #FF8C00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 ULTRADO v2.5 PRO")

vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Např. Minecraft video, Vlog z venku...")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Nástroje pro střih")
    if st.button("✂️ YouCut Expert"):
        st.info("TIP: Použij funkci 'Klíčové snímky' (Keyframes) pro plynulý zoom na tvůj obličej.")
    if st.button("🏷️ Generátor Hashtagů"):
        t = vstup if vstup else "tvorba"
        st.code(f"#{t} #youcut #ultrado #fyp #editing #viral")

with col2:
    st.subheader("✍️ Obsah a Scénář")
    if st.button("📖 Najít fakta (Wiki)"):
        if vstup:
            wiki = wikipediaapi.Wikipedia(language='cs', user_agent='UltradoWeb/1.0')
            page = wiki.page(vstup)
            if page.exists():
                st.write(f"**{page.title}**: {page.summary[:300]}...")
            else: st.error("Nenalezeno.")
        else: st.warning("Nejdřív něco napiš nahoru!")
    
    if st.button("🚀 Šílený Hook (Úvod)"):
        hooks = [f"Tohle je důvod, proč tvůj {vstup} nikoho nezajímá...", f"3 triky pro {vstup}, které ti změní život!"]
        st.warning(random.choice(hooks) if vstup else "Napiš téma!")

st.divider()
if st.button("📝 VYGENEROVAT RYCHLÝ SCÉNÁŘ"):
    if vstup:
        st.success(f"Scénář pro {vstup} je připraven!")
        st.write("1. **0:00-0:05** - Šokující vizuál a otázka.")
        st.write("2. **0:05-0:20** - Rychlý střih (každé 2 sekundy).")
        st.write("3. **0:20-0:30** - Call to action (Dávej odběr!).")
    else:
        st.error("Musíš zadat téma!")
    
