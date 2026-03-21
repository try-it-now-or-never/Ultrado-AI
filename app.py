import streamlit as st
import random
import time
import json
import os
from deep_translator import GoogleTranslator

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado 2.0", page_icon="⚡", layout="wide")

# --- SYSTÉM UKLÁDÁNÍ (SOUBOR) ---
SAVE_FILE = "ultrado_save.json"

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"money": 100, "gems": 0, "inv": [], "name": "Hráč", "last": time.time()}

def save_game():
    data = {
        "money": st.session_state.money,
        "gems": st.session_state.gems,
        "inv": st.session_state.inventory,
        "name": st.session_state.user_name,
        "last": st.session_state.last_claim_time
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

# Inicializace session state
if 'money' not in st.session_state:
    saved = load_game()
    st.session_state.money = saved.get("money", 100)
    st.session_state.gems = saved.get("gems", 0)
    st.session_state.inventory = saved.get("inv", [])
    st.session_state.user_name = saved.get("name", "Hráč")
    st.session_state.last_claim_time = saved.get("last", time.time())

# --- DATA BRAWLERŮ ---
BRAWL_DATA = {
    "COMMON": {"list": ["YouCut Bot (C-1)", "Sběrač Pixelů", "Kluk Střihač", "Zvukový Skřet", "Boxík (Živý)"], "pay": 10},
    "RARE": {"list": ["Filtrová Víla", "Kyber-Editorka", "Brawl Expert", "Glitche-Man", "Lajkovací Golem"], "pay": 30},
    "EPIC": {"list": ["Ultrido Velitel", "Časomág", "Zlatý Střihač", "Hlasový Mág", "Data-Drak"], "pay": 2},
    "LEGEND": {"list": ["Zakladatel (TY)", "Drahokamový Titán", "Algoritmus", "Brawl Král", "YouCut Bůh"], "pay": 15}
}

# --- LOGIKA FARMOVANÍ ---
def get_rates():
    m_h, g_h = 10, 0 # Základní bonus
    for b_entry in st.session_state.inventory:
        name_only = b_entry.split(" (")[0]
        for rar, data in BRAWL_DATA.items():
            if name_only in data["list"]:
                if rar in ["COMMON", "RARE"]: m_h += data["pay"]
                else: g_h += data["pay"]
    return m_h, g_h

m_rate, g_rate = get_rates()
now = time.time()
diff = min(now - st.session_state.last_claim_time, 43200) # 12h limit
p_money = int((m_rate / 3600) * diff * 0.5)
p_gems = int((g_rate / 3600) * diff * 0.5)

# --- CSS DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: white; font-family: 'Orbitron'; }
    .stButton>button { border-radius: 10px; font-weight: bold; width: 100%; }
    .box-card { padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; border: 3px solid; height: 120px; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÍ PANEL (12 FUNKCÍ) ---
with st.sidebar:
    st.title("⚡ ULTRADO MENU")
    new_name = st.text_input("Tvé Jméno:", st.session_state.user_name)
    if new_name != st.session_state.user_name:
        st.session_state.user_name = new_name
        save_game()

    with st.expander("📊 1. ODBĚRATELÉ"):
        sub = st.number_input("Aktuálně:", value=0)
        st.write(f"Cesta k milionu: {1000000 - sub} zbývá!")
    with st.expander("🌍 2. PŘEKLADAČ"):
        t = st.text_area("CZ text:")
        if st.button("Přeložit"): st.write(GoogleTranslator(source='cs', target='en').translate(t))
    with st.expander("🔢 3. KALKULAČKA"):
        n1 = st.number_input("Číslo A"); n2 = st.number_input("Číslo B")
        st.write(f"Součet: {n1+n2}")
    with st.expander("✅ 4. ÚKOLY"):
        st.checkbox("Scénář done"); st.checkbox("Nahráno"); st.checkbox("Edit v YouCut")
    with st.expander("🎵 5. TRENDY"): st.write("• Cruel Summer\n• Greedy\n• Paint The Town Red")
    with st.expander("✂️ 6. YOUCUT TIPY"): st.info("Použij 'Speed Ramp' pro epické záběry!")
    with st.expander("🎮 7. BRAWL TIPY"): st.warning("V Knockoutu nehraj zbrkle!")
    with st.expander("⏱️ 8. SHORTS MĚŘIČ"): 
        sec = st.slider("Délka (s)", 0, 60, 15)
        st.write(f"Do minuty zbývá {60-sec}s")
    with st.expander("🔍 9. REŠERŠE"): st.text_input("Najít na Wiki:")
    with st.expander("🏷️ 10. HASHTAGY"): st.code("#youcut #ultrado #brawlstars")
    with st.expander("🎒 11. INVENTÁŘ"):
        if not st.session_state.inventory: st.write("Zatím nic...")
        for b in st.session_state.inventory: st.write(f"• {b}")
    with st.expander("💾 12. SYSTÉM"):
        if st.button("Smazat Progress"):
            if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
            st.rerun()

# --- HLAVNÍ PLOCHA ---
st.title(f"🚀 {st.session_state.user_name.upper()}'S ULTRADO 2.0")

col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1: st.metric("💰 Peněženka", f"{st.session_state.money}")
with col_stats2: st.metric("💎 Gemy", f"{st.session_state.gems}")
with col_stats3:
    if st.button("📥 VYZVEDNOUT (CLAIM)", use_container_width=True):
        st.session_state.money += p_money
        st.session_state.gems += p_gems
        st.session_state.last_claim_time = time.time()
        save_game()
        st.balloons(); st.rerun()

st.info(f"Farma: {m_rate}💰/h | {g_rate}💎/h. Právě vyfáráno: {p_money}💰 a {p_gems}💎")

st.divider()

# --- BOX SIMULÁTOR ---
st.subheader("📦 OTEVŘI BOX")
bx1, bx2, bx3 = st.columns(3)

def buy_box(cost, cur, rars):
    if cur == "M" and st.session_state.money >= cost: st.session_state.money -= cost
    elif cur == "G" and st.session_state.gems >= cost: st.session_state.gems -= cost
    else: st.error("Nedostatek prostředků!"); return

    rar = random.choice(rars)
    drop = random.choice(BRAWL_DATA[rar]["list"])
    entry = f"{drop} ({rar})"
    if entry not in st.session_state.inventory: st.session_state.inventory.append(entry)
    save_game()
    st.success(f"NOVÝ DROP: {entry}!")

with bx1:
    st.markdown('<div class="box-card" style="border-color: #444; background: #111;"><b>BRAWL BOX</b><br>100 💰</div>', unsafe_allow_html=True)
    if st.button("OTEVŘÍT ČERNÝ"): buy_box(100, "M", ["COMMON", "COMMON", "RARE"])

with bx2:
    st.markdown('<div class="box-card" style="border-color: #FF8C00; background: #221a00;"><b>BIG BOX</b><br>500 💰</div>', unsafe_allow_html=True)
    if st.button("OTEVŘÍT ORANŽOVÝ"): buy_box(500, "M", ["RARE", "EPIC"])

with bx3:
    st.markdown('<div class="box-card" style="border-color: #FFD700; background: #000; box-shadow: 0 0 10px gold;"><b>MEGA BOX</b><br>50 💎</div>', unsafe_allow_html=True)
    if st.button("OTEVŘÍT KARBONOVÝ"): buy_box(50, "G", ["EPIC", "LEGEND"])
