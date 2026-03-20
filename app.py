import streamlit as st
import random
import time
from deep_translator import GoogleTranslator
from streamlit_javascript import st_javascript

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado 2.0", page_icon="⚡", layout="wide")

# --- SYSTÉM UKLÁDÁNÍ (LOCAL STORAGE) ---
def load_data():
    # Načte uložená data z prohlížeče
    return st_javascript("JSON.parse(localStorage.getItem('ultrado_v2_save'))")

def save_data():
    save_obj = {
        "money": st.session_state.money,
        "gems": st.session_state.gems,
        "inv": st.session_state.inventory,
        "name": st.session_state.user_name,
        "last": st.session_state.last_claim_time
    }
    st_javascript(f"localStorage.setItem('ultrado_v2_save', JSON.stringify({save_obj}))")

# Inicializace session state
if 'init' not in st.session_state:
    saved = load_data()
    if saved and isinstance(saved, dict):
        st.session_state.money = saved.get("money", 100)
        st.session_state.gems = saved.get("gems", 0)
        st.session_state.inventory = saved.get("inv", [])
        st.session_state.user_name = saved.get("name", "Hráč")
        st.session_state.last_claim_time = saved.get("last", time.time())
    else:
        st.session_state.money = 100
        st.session_state.gems = 0
        st.session_state.inventory = []
        st.session_state.user_name = "Hráč"
        st.session_state.last_claim_time = time.time()
    st.session_state.init = True

# --- DATABÁZE BRAWLERŮ (20 POSTAV) ---
BRAWL_DATA = {
    "COMMON": {"list": ["YouCut Bot (C-1)", "Sběrač Pixelů", "Kluk Střihač", "Zvukový Skřet", "Boxík (Živý)"], "pay": 10},
    "RARE": {"list": ["Filtrová Víla", "Kyber-Editorka", "Brawl Expert", "Glitche-Man", "Lajkovací Golem"], "pay": 30},
    "EPIC": {"list": ["Ultrido Velitel", "Časomág", "Zlatý Střihač", "Hlasový Mág", "Data-Drak"], "pay": 2},
    "LEGEND": {"list": ["Zakladatel (TY)", "Drahokamový Titán", "Algoritmus", "Brawl Král", "YouCut Bůh"], "pay": 15}
}

# --- VÝPOČET FARMENÍ (INCOME FLOW) ---
def get_rates():
    m_h = 10 # Základní bonus
    g_h = 0
    for b_entry in st.session_state.inventory:
        name = b_entry.split(" (")[0]
        for rar, data in BRAWL_DATA.items():
            if name in data["list"]:
                if rar in ["COMMON", "RARE"]: m_h += data["pay"]
                else: g_h += data["pay"]
    return m_h, g_h

m_rate, g_rate = get_rates()
now = time.time()
# 12hodinový limit (43200 sekund)
diff = min(now - st.session_state.last_claim_time, 43200)
# 50% offline postih
p_money = int((m_rate / 3600) * diff * 0.5)
p_gems = int((g_rate / 3600) * diff * 0.5)

# --- DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: white; font-family: 'Orbitron'; }
    .stButton>button { border-radius: 10px; font-weight: bold; width: 100%; }
    .box-card { padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; border: 3px solid; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÍ PANEL (12 FUNKCÍ) ---
with st.sidebar:
    st.title("⚡ ULTRADO MENU")
    st.session_state.user_name = st.text_input("Jméno:", st.session_state.user_name)
    
    with st.expander("📊 1. ODBĚRATELÉ"):
        sub = st.number_input("Aktuálně:", value=0); cil = st.number_input("Cíl:", value=100)
        st.progress(min(100, int((sub/cil)*100)) if cil>0 else 0)
    with st.expander("🌍 2. PŘEKLADAČ"):
        t = st.text_area("CZ:"); 
        if st.button("Přeložit"): st.write(GoogleTranslator(source='cs', target='en').translate(t))
    with st.expander("🔢 3. KALKULAČKA"):
        n1 = st.number_input("N1"); n2 = st.number_input("N2")
        st.write(f"Výsledek: {n1+n2}")
    with st.expander("✅ 4. ÚKOLY"):
        st.checkbox("Nahrát video"); st.checkbox("Edit v YouCut"); st.checkbox("Thumbnail")
    with st.expander("🎵 5. TRENDY"): st.write("Cruel Summer, Greedy, Paint The Town Red")
    with st.expander("✂️ 6. YOUCUT TIPY"): st.info("Zkus 'Curve' pro smooth zpomalení!")
    with st.expander("🎮 7. BRAWL TIPY"): st.warning("V Showdownu hlídej keře!")
    with st.expander("⏱️ 8. SHORTS TIME"): st.write(f"Zbejvá: {60 - st.slider('Délka', 0, 60)}s")
    with st.expander("🔍 9. REŠERŠE"): st.text_input("Téma k vyhledání:")
    with st.expander("🏷️ 10. HASHTAGY"): st.code("#youcut #brawl #ultrado")
    with st.expander("🎒 11. INVENTÁŘ"): 
        for b in st.session_state.inventory: st.write(f"• {b}")
    with st.expander("⚙️ 12. SAVE"): 
        if st.button("Uložit ručně"): save_data(); st.success("Uloženo!")

# --- HLAVNÍ PLOCHA ---
st.title(f"🚀 {st.session_state.user_name.upper()}'S ULTRADO 2.0")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1: st.metric("💰 Peněženka", f"{st.session_state.money}")
with col_m2: st.metric("💎 Gemy", f"{st.session_state.gems}")
with col_m3:
    if st.button("📥 CLAIM (Vyzvednout Farmu)", use_container_width=True):
        st.session_state.money += p_money
        st.session_state.gems += p_gems
        st.session_state.last_claim_time = time.time()
        save_data(); st.balloons(); st.rerun()

st.info(f"Tvoji brawleři vyrobili: {p_money} 💰 a {p_gems} 💎 (Offline: 50% | Max: 12h)")

st.divider()

# --- BOX SIMULÁTOR ---
st.subheader("📦 OBCHOD S BOXY")
bx1, bx2, bx3 = st.columns(3)

def buy_box(cost, cur, rars, style):
    if cur == "M" and st.session_state.money >= cost: st.session_state.money -= cost
    elif cur == "G" and st.session_state.gems >= cost: st.session_state.gems -= cost
    else: st.error("Chudý jak kostelní myš!"); return

    rar = random.choice(rars)
    drop = random.choice(BRAWL_DATA[rar]["list"])
    entry = f"{drop} ({rar})"
    if entry not in st.session_state.inventory: st.session_state.inventory.append(entry)
    st.success(f"PADL TI: {entry}!"); save_data()

with bx1:
    st.markdown('<div class="box-card" style="border-color: #444; background: #111;"><b>BRAWL BOX</b><br>100 💰</div>', unsafe_allow_html=True)
    if st.button("OTEVŘÍT ČERNÝ"): buy_box(100, "M", ["COMMON", "COMMON", "RARE"], "black")

with bx2:
    st.markdown('<div class="box-card" style="border-color: #FF8C00; background: #221a00;"><b>BIG BOX</b><br>500 💰</div>', unsafe_allow_html=True)
    if st.button("OTEVŘÍT ORANŽOVÝ"): buy_box(500, "M", ["RARE", "RARE", "EPIC"], "orange")

with bx3:
    st.markdown('<div class="box-card" style="border-color: #FFD700; background: #000; box-shadow: 0 0 10px gold;"><b>MEGA BOX</b><br>50 💎</div>', unsafe_allow_html=True)
    if st.button("OTEVŘÍT KARBONOVÝ"): buy_box(50, "G", ["EPIC", "EPIC", "LEGEND"], "mega")
