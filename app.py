import streamlit as st
import wikipediaapi
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado AI", page_icon="🎬")

# Oranžovo-černý design
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { background-color: #FF8C00; color: black; border-radius: 10px; font-weight: bold; }
    h1, h2, h3 { color: #FF8C00; }
    input { background-color: #222 !important; color: orange !important; }
    </style>
    """, unsafe_allow_index=True)

st.title("🎬 ULTRADO v2.4")

if 'jmeno' not in st.session_state:
    st.session_state.jmeno = "Tvůrce"

wiki = wikipediaapi.Wikipedia(language='cs', user_agent='UltradoWeb/1.0')

st.sidebar.header("Nastavení")
st.session_state.jmeno = st.sidebar.text_input("Tvoje jméno:", st.session_state.jmeno)

vstup = st.text_input("O čem je tvoje video / Co hledáš?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("YouCut Rady"):
        st.info("RADA: V YouCutu zkus 'Zmrazit' (Freeze) pro vtipné momentky.")
    if st.button("Hashtagy"):
        t = vstup if vstup else "video"
        st.code(f"#{t} #youcut #ultrado #fyp #edit #tvorba")

with col2:
    if st.button("Wikipedie"):
        if vstup:
            page = wiki.page(vstup)
            if page.exists():
                st.write(f"### {page.title}")
                st.write(page.summary[:400] + "...")
            else: st.error("Nenalezeno.")
        else: st.warning("Napiš téma do políčka.")
    if st.button("Kontrola"):
        st.write(f"### Checklist pro {st.session_state.jmeno}:")
        st.write("- [ ] Odstraněno YouCut logo?\n- [ ] Titulky mají kontrast?\n- [ ] Zvuk je OK?")

with col3:
    if st.button("Velikost"):
        try:
            gb = (8 * (float(vstup) * 60)) / 8 / 1024
            st.metric("Velikost (GB)", round(gb, 2))
        except: st.error("Zadej minuty.")
    if st.button("Video Úvody"):
        hooks = [f"Vsadím se, že jsi nevěděl tohle o {vstup}!", f"Nejrychlejší způsob na {vstup}..."]
        st.warning(random.choice(hooks) if vstup else "Napiš téma!")

if st.button("Vytvořit rychlý scénář"):
    if vstup:
        st.write(f"### Scénář pro: {vstup}")
        st.write(f"**Hook:** {random.choice(['Šokující fakt', 'Otázka'])}")
        st.write("**Střed:** Vysvětlení a akce.")
        st.write("**Konec:** Výzva k odběru.")
