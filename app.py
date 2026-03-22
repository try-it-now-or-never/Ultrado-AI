import streamlit as st
import time
import random
import json
import os

# --- KONFIGURACE ---
st.set_page_config(page_title="Ultrido Tycoon Pro", page_icon="🟠", layout="wide")

# --- DATA BRAWLERŮ (Jméno: [Rarita, Mince/h, Gemy/h, Relativní šance v rámci rarity]) ---
# Relativní šance: čím vyšší číslo, tím častěji padá oproti ostatním ve stejné raritě
BRAWLER_STATS = {
    "YouCut Bot":      ["Common", 20, 0, 100],
    "Sběrač Pixelů":   ["Common", 25, 0, 80],
    "Kluk Střihač":    ["Common", 30, 0, 60],
    "Boxík":           ["Common", 15, 0, 120],
    
    "Filtrová Víla":   ["Rare", 60, 0, 100],
    "Brawl Expert":    ["Rare", 80, 0, 70],
    
    "Ultrido Velitel": ["Epic", 150, 0.5, 100],
    "Zlatý Střihač":   ["Epic", 200, 0.8, 60],
    "Data-Drak":       ["Epic", 250, 1.0, 40],
    
    "Drahokamový Titán":["Legendary", 800, 3.0, 100],
    "Brawl Král":      ["Legendary", 1200, 5.0, 50],
    
    "Zakladatel (TY)": ["Zakladatel", 5000, 7.0, 100]
}

# --- SYSTÉM UKLÁDÁNÍ ---
SAVE_FILE = "savegame_v2.json"

def save_progress():
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
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
                st.session_state.gems = data.get("gems", 0)
                st.session_state.inventory = data.get("inventory", {})
                st.session_state.last_claim = data.get("last_claim", time.time())
        except: pass

# --- INICIALIZACE ---
if 'coins' not in st.session_state:
    st.session_state.coins = 200
    st.session_state.gems = 0
    st.session_state.inventory = {}
    st.session_state.last_claim = time.time()
    load_progress()

# --- LOGIKA BOXŮ ---
def open_box(box_type):
    # Definice šancí pro různé boxy
    if box_type == "Brawl Box":
        weights = {"Common": 85, "Rare": 14, "Epic": 1, "Legendary": 0, "Zakladatel": 0}
    elif box_type == "Big Box":
        weights = {"Common": 50, "Rare": 35, "Epic": 12, "Legendary": 3, "Zakladatel": 0}
    elif box_type == "Mega Box":
        weights = {"Common": 10, "Rare": 30, "Epic": 40, "Legendary": 18, "Zakladatel": 2}

    # 1. Vyber raritu
    rarity_list = list(weights.keys())
    rarity_weights = list(weights.values())
    chosen_rarity = random.choices(rarity_list, weights=rarity_weights)[0]
    
    # 2. Vyber brawlera v rámci rarity (zohledňuje "relativní šanci")
    possible = [name for name, data in BRAWLER_STATS.items() if data[0] == chosen_rarity]
    sub_weights = [BRAWLER_STATS[name][3] for name in possible]
    chosen_brawler = random.choices(possible, weights=sub_weights)[0]
    
    # 3. Zpracuj výsledek
    if chosen_brawler in st.session_state.inventory:
        refund = (BRAWLER_STATS[chosen_brawler][1] * 2) # Refund je dvojnásobek hodinovky
        st.session_state.coins += refund
        st.info(f"Duplikát! **{chosen_brawler}** se změnil na {refund} 🪙")
    else:
        st.session_state.inventory[chosen_brawler] = 1
        st.balloons()
        st.success(f"PADL TI: **{chosen_brawler}** ({chosen_rarity})!")
    save_progress()

# --- VÝPOČET PŘÍJMU ---
def get_total_income():
    c_h, g_h = 0, 0
    for name, count in st.session_state.inventory.items():
        c_h += BRAWLER_STATS[name][1] * count
        g_h += BRAWLER_STATS[name][2] * count
    return c_h, g_h

# --- UI ---
st.title("🟠 Ultrido Tycoon: Box Edition")

# Horní lišta
c1, c2, c3 = st.columns(3)
c1.metric("Mince", f"{int(st.session_state.coins)} 🪙")
c2.metric("Gemy", f"{int(st.session_state.gems)} 💎")
c_h, g_h = get_total_income()
c3.write(f"Produkce:\n\n{c_h} 🪙/h | {g_h} 💎/h")

st.divider()

# Těžba
mined_c = (c_h / 3600) * (time.time() - st.session_state.last_claim)
mined_g = (g_h / 3600) * (time.time() - st.session_state.last_claim)

st.subheader("⛏️ Sklad")
st.write(f"Vytěženo: **{round(mined_c, 2)} 🪙** a **{round(mined_g, 2)} 💎**")
if st.button("💰 VYZVEDNOUT VŠE"):
    st.session_state.coins += mined_c
    st.session_state.gems += mined_g
    st.session_state.last_claim = time.time()
    save_progress()
    st.rerun()

st.divider()

# Shop
st.header("📦 Shop")
shop_c = st.columns(3)

with shop_c[0]:
    st.subheader("Brawl Box")
    st.caption("Max: Epic (1%)")
    if st.button("Otevřít (100 🪙)"):
        if st.session_state.coins >= 100:
            st.session_state.coins -= 100
            open_box("Brawl Box")
        else: st.error("Málo mincí!")

with shop_c[1]:
    st.subheader("Big Box")
    st.caption("Lepší šance na Epic/Leg")
    if st.button("Otevřít (500 🪙)"):
        if st.session_state.coins >= 500:
            st.session_state.coins -= 500
            open_box("Big Box")
        else: st.error("Málo mincí!")

with shop_c[2]:
    st.subheader("Mega Box")
    st.caption("Šance na Zakladatele!")
    if st.button("Otevřít (2000 🪙)"):
        if st.session_state.coins >= 2000:
            st.session_state.coins -= 2000
            open_box("Mega Box")
        else: st.error("Málo mincí!")
    if st.button("Otevřít (50 💎)"):
        if st.session_state.gems >= 50:
            st.session_state.gems -= 50
            open_box("Mega Box")
        else: st.error("Málo gemů!")

st.divider()

# Inventář
st.header("🎒 Tvůj Tým")
if st.session_state.inventory:
    inv_cols = st.columns(4)
    for i, (name, count) in enumerate(st.session_state.inventory.items()):
        stats = BRAWLER_STATS[name]
        with inv_cols[i % 4]:
            st.info(f"**{name}**\n\n{stats[0]}\n\n{stats[1]}🪙/h | {stats[2]}💎/h")
