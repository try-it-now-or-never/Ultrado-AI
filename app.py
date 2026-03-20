import streamlit as st
import time
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrado 2.0", page_icon="⚡", layout="wide")

# --- INICIALIZACE (SESSION STATE) ---
if 'money' not in st.session_state: st.session_state.money = 100
if 'gems' not in st.session_state: st.session_state.gems = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'last_claim_time' not in st.session_state: st.session_state.last_claim_time = time.time()
if 'user_name' not in st.session_state: st.session_state.user_name = ""

# --- DATABÁZE VÝDĚLKŮ (za hodinu) ---
# Common/Rare = Coiny, Epic/Legend = Gemy
def get_rates():
    m_rate = sum([10 for b in st.session_state.inventory if "COMMON" in b or "RARE" in b])
    g_rate = sum([2 for b in st.session_state.inventory if "EPIC" in b or "LEGEND" in b])
    return m_rate if m_rate > 0 else 5, g_rate # Základní příjem 5/h i bez brawlerů

# --- LOGIKA FARMOVÁNÍ (VÝPOČET TREZORU) ---
current_time = time.time()
seconds_since_last_claim = current_time - st.session_state.last_claim_time

# Limit 12 hodin (12 * 3600 sekund)
limited_seconds = min(seconds_since_last_claim, 12 * 3600)

m_rate_h, g_rate_h = get_rates()

# Výpočet: (Hodinová sazba / 3600) * sekundy * 0.5 (offline postih)
# Poznámka: Pro jednoduchost simulujeme offline postih na všechno od posledního claimu
pending_money = int((m_rate_h / 3600) * limited_seconds * 0.5)
pending_gems = int((g_rate_h / 3600) * limited_seconds * 0.5)

# --- DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: white; font-family: 'Orbitron', sans-serif; }
    .vault-box { background: linear-gradient(145deg, #1c1f26, #2c313c); padding: 25px; border-radius: 20px; border: 3px solid #FF8C00; text-align: center; margin: 20px 0; }
    .stat-text { color: #FF8C00; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HLAVNÍ PLOCHA ---
st.title(f"⚡ ULTRADO 2.0 - {st.session_state.user_name if st.session_state.user_name else 'Base'}")

# Peněženka
c1, c2 = st.columns(2)
with c1: st.metric("Moje Peníze 💰", f"{st.session_state.money}")
with c2: st.metric("Moje Gemy 💎", f"{st.session_state.gems}")

st.divider()

# TREZOR (FARMENÍ)
st.subheader("🚜 AUTOMATICKÁ FARMA")
st.markdown(f"""
    <div class="vault-box">
        <p>V TREZORU JE PRÁVĚ NASTŘÁDÁNO:</p>
        <span class="stat-text">{pending_money} 💰</span> &nbsp;&nbsp; <span class="stat-text">{pending_gems} 💎</span>
        <br><br>
        <small>Produkce: {m_rate_h}💰/h | {g_rate_h}💎/h (Offline: 50% | Limit: 12h)</small>
    </div>
""", unsafe_allow_html=True)

if st.button("📥 VYZVEDNOUT VÝDĚLEK (CLAIM)", use_container_width=True):
    if pending_money > 0 or pending_gems > 0:
        st.session_state.money += pending_money
        st.session_state.gems += pending_gems
        st.session_state.last_claim_time = time.time()
        st.balloons()
        st.rerun()
    else:
        st.warning("Trezor je zatím skoro prázdný, počkej chvíli!")

st.divider()

# SIDEBAR S INVENTÁŘEM
with st.sidebar:
    if not st.session_state.user_name:
        name = st.text_input("Jméno hráče:")
        if name: st.session_state.user_name = name; st.rerun()
    
    st.header("🎒 INVENTÁŘ")
    if not st.session_state.inventory: st.write("Zatím nikoho nemáš.")
    for b in st.session_state.inventory:
        st.write(f"• {b}")
