import streamlit as st
import time
import random
import json
import os

# --- KONFIGURACE ---
st.set_page_config(page_title="Ultrido Tycoon", page_icon="🟠", layout="wide")

# --- DATA (Rarita: Šance %, Refund při duplikátu, Výdělek/h) ---
RARITY_SETTINGS = {
    "Common": {"chance": 70, "refund": 10, "income": 20},
    "Rare": {"chance": 20, "refund": 40, "income": 60},
    "Epic": {"chance": 8, "refund": 150, "income": 200},
    "Legendary": {"chance": 1.9, "refund": 500, "income": 800},
    "Zakladatel": {"chance": 0.1, "refund": 2000, "income": 5000}
}

BRAWLERS = {
    "YouCut Bot": "Common", "Sběrač Pixelů": "Common", "Kluk Střihač": "Common",
    "Boxík": "Common", "Filtrová Víla": "Rare", "Brawl Expert": "Rare",
    "Ultrido Velitel": "Epic", "Zlatý Střihač": "Epic", "Data-Drak": "Epic",
    "Drahokamový Titán": "Legendary", "Brawl Král": "Legendary",
    "Zakladatel (TY)": "Zakladatel"
}

# --- SYSTÉM UKLÁDÁNÍ ---
SAVE_FILE = "savegame.json"

def save_progress():
    data = {
        "coins": st.session_state.coins,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                st.session_state.coins = data.get("coins", 200)
                st.session_state.inventory = data.get("inventory", {})
                st.session_state.last_claim = data.get("last_claim", time.time())
        except:
            st.error("Nepodařilo se načíst uloženou hru, začínáš od nuly.")

# --- INICIALIZACE ---
if 'coins' not in st.session_state:
    load_progress()
    if 'coins' not in st.session_state: # Pokud soubor neexistuje
        st.session_state.coins = 200
        st.session_state.inventory = {}
        st.session_state.last_claim = time.time()

# --- VÝPOČTY ---
def get_income_per_hour():
    total = 0
    for name, count in st.session_state.inventory.items():
        rarity = BRAWLERS[name]
        total += RARITY_SETTINGS[rarity]["income"] * count
    return total

def get_current_mined():
    now = time.time()
    diff = now - st.session_state.last_claim
    if diff > 43200: diff = 43200 # 12h limit
    
    income_per_sec = get_income_per_hour() / 3600
    return round(diff * income_per_sec, 2)

# --- UI: SIDEBAR ---
with st.sidebar:
    st.title("👤 Profil Hráče")
    st.metric("Moje Mince", f"{int(st.session_state.coins)} 🪙")
    st.write(f"Zisk: **{get_income_per_hour()}**/h")
    
    st.divider()
    if st.button("Resetovat hru (Smazat save)"):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        st.rerun()

    secret = st.text_input("Admin Kód", type="password")
    if secret == "admin530":
        if st.button("AKTIVOVAT VŠE"):
            st.session_state.coins = 999999
            for name in BRAWLERS:
                st.session_state.inventory[name] = 1
            save_progress()
            st.success("Admin mod aktivován!")

# --- UI: HLAVNÍ STRANA ---
st.title("🟠 Ultrido Tycoon")

# Těžba
st.subheader("⛏️ Těžba")
mined = get_current_mined()
c1, c2 = st.columns([2, 1])
c1.metric("Vytěženo od posledního vyzvednutí", f"{mined} 🪙")

if c2.button("💰 VYZVEDNOUT VŠE", use_container_width=True):
    if mined > 0:
        st.session_state.coins += mined
        st.session_state.last_claim = time.time()
        save_progress()
        st.rerun()
    else:
        st.warning("Zatím není co vyzvednout!")

st.divider()

# Obchod
st.header("📦 Shop")
if st.button("Otevřít Brawl Box (Cena: 100 🪙)", use_container_width=True):
    if st.session_state.coins >= 100:
        st.session_state.coins -= 100
        
        # Gacha logika
        rarities = list(RARITY_SETTINGS.keys())
        weights = [RARITY_SETTINGS[r]["chance"] for r in rarities]
        drawn_rarity = random.choices(rarities, weights=weights, k=1)[0]
        
        # Výběr postavy z dané rarity
        available = [name for name, rar in BRAWLERS.items() if rar == drawn_rarity]
        drawn_brawler = random.choice(available)
        
        # Duplikát vs Nový
        if drawn_brawler in st.session_state.inventory:
            refund = RARITY_SETTINGS[drawn_rarity]["refund"]
            st.session_state.coins += refund
            st.info(f"Máš duplikát! **{drawn_brawler}** se mění na {refund} 🪙")
        else:
            st.session_state.inventory[drawn_brawler] = 1
            st.balloons()
            st.success(f"GRATULACE! Padl ti: **{drawn_brawler}** ({drawn_rarity})")
        
        save_progress()
    else:
        st.error("Nemáš dost mincí!")

st.divider()

# Inventář
st.header("🎒 Tvůj Inventář")
if not st.session_state.inventory:
    st.info("Tvůj inventář je prázdný. Zkus štěstí v obchodě!")
else:
    inv_cols = st.columns(4)
    for i, (name, count) in enumerate(st.session_state.inventory.items()):
        rar = BRAWLERS[name]
        with inv_cols[i % 4]:
            st.markdown(f"### {name}")
            st.markdown(f"*{rar}*")
            st.write(f"Výnos: {RARITY_SETTINGS[rar]['income']} 🪙/h")
