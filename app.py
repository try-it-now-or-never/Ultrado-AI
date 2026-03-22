import streamlit as st
import time
import random
import json
import os
from datetime import datetime, timedelta

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Ultrido Tycoon FULL", page_icon="🟠", layout="wide")

# --- POŘADÍ RARIT ---
RARITY_ORDER = {"Zakladatel": 0, "Legendary": 1, "Epic": 2, "Rare": 3, "Common": 4}

# --- CSS PRO ANIMACE ---
st.markdown("""
<style>
    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        40% { transform: translate(1px, -1px) rotate(1deg); }
        50% { transform: translate(-1px, 2px) rotate(-1deg); }
        60% { transform: translate(-3px, 1px) rotate(0deg); }
        70% { transform: translate(3px, 1px) rotate(-1deg); }
        80% { transform: translate(-1px, -1px) rotate(1deg); }
        90% { transform: translate(1px, 2px) rotate(0deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    .box-card, .wheel-card {
        border: 3px solid #ffcc00;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        background-color: #1e1e26;
        margin-bottom: 10px;
    }
    .box-shake { animation: shake 0.5s; animation-iteration-count: infinite; border-color: #ff4b4b; }
    .reveal-card {
        background: radial-gradient(circle, #2e2e3e 0%, #1a1a1a 100%);
        border: 5px solid #ffcc00; border-radius: 25px;
        padding: 50px; text-align: center; color: white;
        box-shadow: 0 0 50px rgba(255, 204, 0, 0.4);
    }
    .brawler-card {
        padding: 15px; border-radius: 12px; background: #262730;
        border-top: 4px solid #ffcc00; text-align: center; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA BRAWLERŮ ---
BRAWLER_STATS = {
    "YouCut Bot":      ["Common", 20, 0, 100],
    "Sběrač Pixelů":   ["Common", 25, 0, 80],
    "Kluk Střihač":    ["Common", 30, 0, 60],
    "Boxík":           ["Common", 15, 0, 120],
    "Filtrová Víla":   ["Rare", 60, 0, 100],
    "Brawl Expert":    ["Rare", 80, 0, 70],
    "Ultrido Velitel": ["Epic", 150, 0.5, 100],
    "Zlatý Střihač":   ["Epic", 200, 0.8, 65],
    "Data-Drak":       ["Epic", 250, 1.0, 40],
    "Drahokamový Titán":["Legendary", 800, 3.5, 100],
    "Brawl Král":      ["Legendary", 1200, 5.0, 50],
    "Zakladatel (TY)": ["Zakladatel", 5000, 7.0, 100]
}

SAVE_FILE = "ultrido_save.json"

def save_game():
    data = {
        "coins": st.session_state.coins, "gems": st.session_state.gems,
        "inventory": st.session_state.inventory, "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel
    }
    with open(SAVE_FILE, "w") as f: json.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                st.session_state.coins = data.get("coins", 200)
                st.session_state.gems = data.get("gems", 0)
                st.session_state.inventory = data.get("inventory", {})
                st.session_state.last_claim = data.get("last_claim", time.time())
                st.session_state.last_wheel = data.get("last_wheel", 0)
        except: pass

if 'coins' not in st.session_state:
    st.session_state.coins, st.session_state.gems, st.session_state.inventory = 200, 0, {}
    st.session_state.last_claim = time.time()
    st.session_state.last_wheel = 0
    st.session_state.last_drop = None
    load_game()

def get_income():
    c_h, g_h = 0, 0
    for name, count in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            c_h += BRAWLER_STATS[name][1] * count
            g_h += BRAWLER_STATS[name][2] * count
    return c_h, g_h

# --- KOLO ŠTĚSTÍ LOGIKA ---
def spin_wheel():
    placeholder = st.empty()
    placeholder.markdown('<div class="box-card box-shake"><h2>🎡 KOLO ŠTĚSTÍ SE TOČÍ...</h2></div>', unsafe_allow_html=True)
    time.sleep(2)
    placeholder.empty()

    roll = random.random() * 100
    # Šance: 0.01% Rare, 0.25% Gemy, 5% Common, zbytek Mince (11% šance na výhru mincí celkem)
    
    if roll <= 0.01: # Rare postava
        possible = [n for n, d in BRAWLER_STATS.items() if d[0] == "Rare"]
        res = random.choice(possible)
        typ = "RARE POSTAVA"
    elif roll <= 0.26: # Gemy (0.25%)
        st.session_state.gems += 5
        res, typ = "5 GEMŮ", "DRAHOKAMY"
    elif roll <= 5.26: # Common postava (5%)
        possible = [n for n, d in BRAWLER_STATS.items() if d[0] == "Common"]
        res = random.choice(possible)
        typ = "COMMON POSTAVA"
    elif roll <= 16.26: # Mince (10% pro 250 až 1% pro 750)
        # Vážený výběr mincí
        amount = random.randint(250, 750)
        st.session_state.coins += amount
        res, typ = f"{amount} MINCÍ", "PENÍZE"
    else:
        res, typ = "Zkus to znovu příště!", "NIC"

    # Zpracování postavy pokud padla
    if "POSTAVA" in typ:
        if res in st.session_state.inventory:
            st.session_state.coins += 50
            res = f"Duplikát {res} (+50 🪙)"
        else:
            st.session_state.inventory[res] = 1
    
    st.session_state.last_drop = {"name": res, "rarity": typ, "new": True}
    save_game()

# --- REVEAL OKNO ---
if st.session_state.last_drop:
    drop = st.session_state.last_drop
    st.markdown(f'<div class="reveal-card"><h1>🎁 VÝHRA Z KOLA ŠTĚSTÍ!</h1><h2 style="font-size: 3em;">{drop["name"]}</h2><h3>{drop["rarity"]}</h3></div>', unsafe_allow_html=True)
    if st.button("POKRAČOVAT"):
        st.session_state.last_drop = None
        st.rerun()
    st.stop()

# --- UI ---
st.title("🟠 Ultrido Tycoon: Lucky Wheel")

c_h, g_h = get_income()
col_a, col_b, col_c = st.columns(3)
col_a.metric("Mince", f"{int(st.session_state.coins)} 🪙")
col_b.metric("Gemy", f"{int(st.session_state.gems)} 💎")
col_c.write(f"Produkce: {round(c_h, 1)}/h | {round(g_h, 1)}/h")

st.divider()

# KOLO ŠTĚSTÍ SEKCE
st.header("🎡 Kolo štěstí")
time_passed = time.time() - st.session_state.last_wheel
is_free = time_passed >= 86400 # 24 hodin

w1, w2, w3 = st.columns(3)
with w1:
    if is_free:
        if st.button("🎰 ZDARMA (Daily Reward)", use_container_width=True):
            st.session_state.last_wheel = time.time()
            spin_wheel()
            st.rerun()
    else:
        next_spin = timedelta(seconds=int(86400 - time_passed))
        st.info(f"Další free spin za: {str(next_spin).split('.')[0]}")

with w2:
    if st.button("🎰 TOČIT ZA 300 🪙", use_container_width=True):
        if st.session_state.coins >= 300:
            st.session_state.coins -= 300
            spin_wheel()
            st.rerun()
        else: st.error("Málo mincí!")

with w3:
    if st.button("🎰 TOČIT ZA 15 💎", use_container_width=True):
        if st.session_state.gems >= 15:
            st.session_state.gems -= 15
            spin_wheel()
            st.rerun()
        else: st.error("Málo gemů!")

st.divider()

# SHOP A TĚŽBA (Zkráceno pro přehlednost, ale vše tam je)
st.subheader("⛏️ Sklad")
diff = min(time.time() - st.session_state.last_claim, 43200)
mined_c, mined_g = (c_h/3600)*diff, (g_h/3600)*diff
if st.button(f"💰 VYZVEDNOUT ({round(mined_c,1)} 🪙 | {round(mined_g,1)} 💎)"):
    st.session_state.coins += mined_c
    st.session_state.gems += mined_g
    st.session_state.last_claim = time.time()
    save_game()
    st.rerun()

st.header("📦 Shop")
def buy_box(name, cost, currency="coins"):
    if (st.session_state.coins if currency=="coins" else st.session_state.gems) >= cost:
        if currency=="coins": st.session_state.coins -= cost
        else: st.session_state.gems -= cost
        
        # Logika boxů (zjednodušená volání tvých rarit)
        if name == "Brawl Box": weights = {"Common": 84, "Rare": 15, "Epic": 1, "Legendary": 0, "Zakladatel": 0}
        elif name == "Big Box": weights = {"Common": 45, "Rare": 35, "Epic": 15, "Legendary": 5, "Zakladatel": 0}
        else: weights = {"Common": 10, "Rare": 25, "Epic": 40, "Legendary": 23, "Zakladatel": 2}
        
        placeholder = st.empty()
        placeholder.markdown(f'<div class="box-card box-shake"><h2>📦 OTEVÍRÁM {name}...</h2></div>', unsafe_allow_html=True)
        time.sleep(1.5)
        placeholder.empty()

        rarity = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        res = random.choice([n for n, d in BRAWLER_STATS.items() if d[0] == rarity])
        
        is_new = res not in st.session_state.inventory
        if is_new: st.session_state.inventory[res] = 1
        else: st.session_state.coins += (BRAWLER_STATS[res][1]*5)
        
        st.session_state.last_drop = {"name": res, "rarity": rarity, "new": is_new}
        save_game()
        st.rerun()

sh1, sh2, sh3 = st.columns(3)
with sh1: 
    if st.button("BRAWL BOX (100 🪙)"): buy_box("Brawl Box", 100)
with sh2: 
    if st.button("BIG BOX (500 🪙)"): buy_box("Big Box", 500)
with sh3: 
    if st.button("MEGA BOX (2000 🪙)"): buy_box("Mega Box", 2000)
    if st.button("MEGA BOX (50  💎)"): buy_box("Mega Box", 50, "gems")

st.divider()

# INVENTÁŘ SEŘAZENÝ
st.header("🎒 Inventář (Seřazeno podle rarity)")
if st.session_state.inventory:
    sorted_inv = sorted(st.session_state.inventory.items(), key=lambda x: RARITY_ORDER[BRAWLER_STATS[x[0]][0]])
    cols = st.columns(5)
    for i, (name, count) in enumerate(sorted_inv):
        stats = BRAWLER_STATS[name]
        rar_color = {"Common": "#FFF", "Rare": "#0F0", "Epic": "#F0F", "Legendary": "#FF0", "Zakladatel": "#F40"}[stats[0]]
        with cols[i % 5]:
            st.markdown(f'<div class="brawler-card" style="border-top-color:{rar_color}"><b style="color:{rar_color}">{name}</b><br><small>{stats[0]}</small><br>{stats[1]}🪙/h</div>', unsafe_allow_html=True)

with st.sidebar:
    if st.button("🔄 RESET"):
        st.session_state.coins, st.session_state.gems, st.session_state.inventory = 200, 0, {}
        st.session_state.last_wheel, st.session_state.last_claim = 0, time.time()
        save_game(); st.rerun()
    code = st.text_input("Admin", type="password")
    if code == "admin530" and st.button("ACTIVATE"):
        st.session_state.coins, st.session_state.gems = 99999, 999
        for n in BRAWLER_STATS: st.session_state.inventory[n] = 1
        save_game(); st.rerun()
