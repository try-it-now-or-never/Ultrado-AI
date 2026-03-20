import streamlit as st
import random
import time
from deep_translator import GoogleTranslator
import wikipediaapi

# --- NASTAVENÍ ---
st.set_page_config(page_title="Ultrado 2.0", page_icon="⚡", layout="wide")

# --- STAV HRY ---
if 'money' not in st.session_state: st.session_state.money = 100
if 'gems' not in st.session_state: st.session_state.gems = 0
if 'inventory' not in st.session_state: st.session_state.inventory = [] # Seznam jmen brawlerů
if 'last_claim_time' not in st.session_state: st.session_state.last_claim_time = time.time()
if 'user_name' not in st.session_state: st.session_state.user_name = "Hráč"

# --- DATA BRAWLERŮ (VÝDĚLKY) ---
BRAWL_DATA = {
    "COMMON": {"list": ["YouCut Bot (C-1)", "Sběrač Pixelů", "Kluk Střihač", "Zvukový Skřet", "Boxík (Živý)"], "pay": 10}, # 10/h
    "RARE": {"list": ["Filtrová Víla", "Kyber-Editorka", "Brawl Expert", "Glitche-Man", "Lajkovací Golem"], "pay": 25}, # 25/h
    "EPIC": {"list": ["Ultrido Velitel", "Časomág", "Zlatý Střihač", "Hlasový Mág", "Data-Drak"], "pay": 2}, # 2 gemy/h
    "LEGEND": {"list": ["Zakladatel (TY)", "Drahokamový Titán", "Algoritmus", "Brawl Král", "YouCut Bůh"], "pay": 10} # 10 gemů/h
}

# --- LOGIKA FARMOVANÍ ---
def calculate_farm():
    m_rate = 0
    g_rate = 0
    for item in st.session_state.inventory:
        for rar, data in BRAWL_DATA.items():
            if item in data["list"]:
                if rar in ["COMMON", "RARE"]: m_rate += data["pay"]
                else: g_rate += data["pay"]
    
    now = time.time()
    diff = min(now - st.session_state.last_claim_time, 12 * 3600) # Max 12h
    offline_mult = 0.5 # 50% offline postih
    
    p_money = int((m_rate / 3600) * diff * offline_mult)
    p_gems = int((g_rate / 3600) * diff * offline_mult)
    return p_money, p_gems, m_rate, g_rate

p_money, p_gems, m_h, g_h = calculate_farm()

# --- CSS DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: white; font-family: 'Orbitron'; }
    .box-black { border: 3px solid #444; background: #111; padding: 15px; border-radius: 10px; text-align: center; }
    .box-orange { border: 3px solid #FF8C00; background: #221a00; padding: 15px; border-radius: 10px; text-align: center; }
    .box-mega { border: 3px solid #FFD700; background: #000; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÍ PANEL (TĚCH 12 FUNKCÍ) ---
with st.sidebar:
    st.title("⚡ ULTRADO 2.0")
    st.session_state.user_name = st.text_input("Jméno:", value=st.session_state.user_name)
    
    with st.expander("📊 ODBĚRATELÉ"):
        akt = st.number_input("Mám:", value=0)
        cil = st.number_input("Cíl:", value=100)
        st.progress(min(100, int((akt/cil)*100)) if cil>0 else 0)

    with st.expander("🌍 PŘEKLADAČ"):
        txt = st.text_area("CZ:")
        if st.button("Přeložit"): st.write(GoogleTranslator(source='cs', target='en').translate(txt))

    with st.expander("🔢 KALKULAČKA"):
        c1 = st.number_input("Číslo 1")
        c2 = st.number_input("Číslo 2")
        if st.button("Sečti"): st.write(c1 + c2)

    with st.expander("✅ ÚKOLY"):
        st.checkbox("Natočit"); st.checkbox("Sestříhat"); st.checkbox("Vydat")

    with st.expander("🎵 TRENDY HUDBA"):
        st.write("1. Cruel Summer\n2. Paint The Town Red")

    with st.expander("⏱️ SHORTS KALKULAČKA"):
        sec = st.number_input("Sekundy celkem:", value=0)
        st.write(f"Zbylo: {60-sec}s")

    with st.expander("🎒 INVENTÁŘ BRAWLERŮ"):
        for b in st.session_state.inventory: st.write(f"• {b}")

# --- HLAVNÍ PLOCHA ---
st.title(f"🎬 PRODUKCE & BOX SIMULÁTOR")

# Statistiky a Claim
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1: st.metric("Peníze 💰", st.session_state.money)
with col_s2: st.metric("Gemy 💎", st.session_state.gems)
with col_s3:
    if st.button("📥 CLAIM (Vyzvednout farmu)"):
        st.session_state.money += p_money
        st.session_state.gems += p_gems
        st.session_state.last_claim_time = time.time()
        st.balloons(); st.rerun()

st.info(f"Tvoji brawleři právě vydělali: {p_money} 💰 a {p_gems} 💎")

st.divider()

# BOX SYSTÉM
st.subheader("📦 OTEVŘI ULTRADO BOXY")
bx1, bx2, bx3 = st.columns(3)

def open_box(rarities, cost_val, cost_type):
    if cost_type == "M" and st.session_state.money >= cost_val: st.session_state.money -= cost_val
    elif cost_type == "G" and st.session_state.gems >= cost_val: st.session_state.gems -= cost_val
    else: st.error("Nemáš dost peněz/gemů!"); return

    rar = random.choice(rarities)
    drop = random.choice(BRAWL_DATA[rar]["list"])
    if drop not in st.session_state.inventory: st.session_state.inventory.append(drop)
    st.success(f"PADL TI: {drop} ({rar})!")

with bx1:
    st.markdown('<div class="box-black"><b>BRAWL BOX</b><br>100 💰</div>', unsafe_allow_html=True)
    if st.button("Otevřít Černý"): open_box(["COMMON", "RARE"], 100, "M")

with bx2:
    st.markdown('<div class="box-orange"><b>BIG BOX</b><br>500 💰</div>', unsafe_allow_html=True)
    if st.button("Otevřít Oranžový"): open_box(["RARE", "EPIC"], 500, "M")

with bx3:
    st.markdown('<div class="box-mega"><b>MEGA BOX</b><br>50 💎</div>', unsafe_allow_html=True)
    if st.button("Otevřít Karbonový"): open_box(["EPIC", "LEGEND"], 50, "G")

st.divider()

# YOUCUT TIPY A ZBYTEK
c_tip1, c_tip2 = st.columns(2)
with c_tip1:
    if st.button("✂️ YouCut Tipy"): st.info("Použij 'Keyframes' pro pohyb textu!")
    if st.button("🏷️ Generuj Hashtagy"): st.code("#youcut #brawlstars #ultrado")
with c_tip2:
    if st.button("🎮 Brawl Stars Tip"): st.warning("V Showdownu si hlídej záda!")
    if st.button("📖 Wikipedie"): st.write("Zadej téma v bočním panelu...")
