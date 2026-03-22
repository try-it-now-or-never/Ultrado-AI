import streamlit as st
import time
import random

# --- DATA BRAWLERŮ (Jméno: [Rarita, Mince/h, Gemy/h]) ---
RARITY_SETTINGS = {
    "Common": {"chance": 90, "refund": 10},
    "Rare": {"chance": 8, "refund": 40},
    "Epic": {"chance": 1.9, "refund": 150},
    "Legendary": {"chance": 0.099, "refund": 500},
    "Zakladatel": {"chance": 0.001, "refund": 2000}
}

BRAWLERS = {
    "YouCut Bot": "Common", "Sběrač Pixelů": "Common", "Kluk Střihač": "Common",
    "Boxík": "Common", "Filtrová Víla": "Rare", "Brawl Expert": "Rare",
    "Ultrido Velitel": "Epic", "Zlatý Střihač": "Epic", "Data-Drak": "Epic",
    "Drahokamový Titán": "Legendary", "Brawl Král": "Legendary",
    "Zakladatel (TY)": "Zakladatel"
}

# --- LOGIKA TĚŽBY (Income Function) ---
def get_current_income():
    now = time.time()
    diff = now - st.session_state.last_claim
   
    # 12 HODIN LIMIT (v sekundách 43200)
    is_offline_capped = False
    if diff > 43200:
        diff = 43200
        is_offline_capped = True
       
    total_c = 0
    # Výpočet: Každý brawler dává fixní částku (tady pro demo 10-1000)
    # V online režimu 100%, v offline (když je zavřený web) by to bylo 50%
    # Tady simulujeme průměr nebo čistý online flow
    for b in st.session_state.inventory:
        total_c += (10 / 3600) * diff # Příklad: 10 coinů/h na každého
       
    return round(total_c, 2), is_offline_capped

# --- INICIALIZACE ---
if 'coins' not in st.session_state:
    st.session_state.coins = 200
    st.session_state.inventory = []
    st.session_state.last_claim = time.time()

# --- ADMIN FUNKCE ---
def activate_admin():
    st.session_state.coins = 999999
    st.session_state.inventory = list(BRAWLERS.keys())
    st.success("ADMIN MODE: Vše odemčeno!")

# --- UI ---
st.title("🟠 Ultrido Tycoon")
st.sidebar.header("Můj Profil")
st.sidebar.write(f"🪙 Mince: {int(st.session_state.coins)}")

# Tajné pole pro Admina
secret = st.sidebar.text_input("Kód", type="password")
if secret == "admin530":
    if st.sidebar.button("AKTIVOVAT VŠE"):
        activate_admin()

# Těžba sekce
income, capped = get_current_income()
st.subheader(f"Aktuálně vytěženo: {income} 🪙")
if capped:
    st.warning("⚠️ Sklad je plný (limit 12h)! Vyzvedni si mince.")

if st.button("💰 VYZVEDNOUT"):
    st.session_state.coins += income
    st.session_state.last_claim = time.time()
    st.rerun()

st.divider()

# Shop sekce
st.header("📦 Shop")
if st.button("Otevřít Brawl Box (100 🪙)"):
    if st.session_state.coins >= 100:
        st.session_state.coins -= 100
        # Logika šancí
        roll = random.random() * 100
        if roll < 0.1: res = "Zakladatel (TY)"
        elif roll < 1: res = "Drahokamový Titán"
        else: res = "YouCut Bot"
       
        if res in st.session_state.inventory:
            st.session_state.coins += 10
            st.info(f"Duplikát {res}! Dostal jsi 10 🪙")
        else:
            st.session_state.inventory.append(res)
            st.balloons()
            st.success(f"PADL TI: {res}!")
    else:
        st.error("Nemáš dost mincí!")

st.write("Tvůj Inventář:", st.session_state.inventory)
