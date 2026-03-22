import streamlit as st
import time
import random
import json
import os

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Ultrido Tycoon FULL", page_icon="🟠", layout="wide")

# --- CSS PRO ANIMACE (Třesení boxu a vzhled karet) ---
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
    .box-card {
        border: 3px solid #ffcc00;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        background-color: #1e1e26;
        margin-bottom: 10px;
    }
    .box-shake {
        animation: shake 0.5s;
        animation-iteration-count: infinite;
        border-color: #ff4b4b;
        background-color: #3e2723;
    }
    .brawler-card {
        padding: 15px;
        border-radius: 12px;
        background: #262730;
        border-top: 4px solid #ffcc00;
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- KOMPLETNÍ DATA BRAWLERŮ ---
# Formát: "Jméno": [Rarita, Mince/h, Gemy/h, Relativní šance v rámci rarity]
# (Čím vyšší šance, tím častěji padá oproti ostatním ve stejné skupině)
BRAWLER_STATS = {
    # Common
    "YouCut Bot":      ["Common", 20, 0, 100],
    "Sběrač Pixelů":   ["Common", 25, 0, 80],
    "Kluk Střihač":    ["Common", 30, 0, 60],
    "Boxík":           ["Common", 15, 0, 120],
    
    # Rare
    "Filtrová Víla":   ["Rare", 60, 0, 100],
    "Brawl Expert":    ["Rare", 80, 0, 70],
    
    # Epic (Gemy max 1/h)
    "Ultrido Velitel": ["Epic", 150, 0.5, 100],
    "Zlatý Střihač":   ["Epic", 200, 0.8, 65],
    "Data-Drak":       ["Epic", 250, 1.0, 40],
    
    # Legendary (Gemy max 5/h)
    "Drahokamový Titán":["Legendary", 800, 3.5, 100],
    "Brawl Král":      ["Legendary", 1200, 5.0, 50],
    
    # Zakladatel (Gemy 7/h)
    "Zakladatel (TY)": ["Zakladatel", 5000, 7.0, 100]
}

SAVE_FILE = "ultrido_save.json"

# --- SYSTÉM UKLÁDÁNÍ ---
def save_game():
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                st.session_state.coins = data.get("coins", 200)
                st.session_state.gems = data.get("gems", 0)
                st.session_state.inventory = data.get("inventory", {})
                st.session_state.last_claim = data.get("last_claim", time.time())
        except: pass

# --- INICIALIZACE SESSION ---
if 'coins' not in st.session_state:
    st.session_state.coins = 200
    st.session_state.gems = 0
    st.session_state.inventory = {}
    st.session_state.last_claim = time.time()
    load_game()

# --- VÝPOČET PŘÍJMU ---
def get_income():
    c_h, g_h = 0, 0
    for name, count in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            c_h += BRAWLER_STATS[name][1] * count
            g_h += BRAWLER_STATS[name][2] * count
    return c_h, g_h

# --- OTEVÍRÁNÍ BOXU (Logika + Animace) ---
def open_box(box_type):
    # Definice šancí rarit pro každý box
    if box_type == "Brawl Box":
        weights = {"Common": 84, "Rare": 15, "Epic": 1, "Legendary": 0, "Zakladatel": 0}
    elif box_type == "Big Box":
        weights = {"Common": 45, "Rare": 35, "Epic": 15, "Legendary": 5, "Zakladatel": 0}
    else: # Mega Box
        weights = {"Common": 10, "Rare": 25, "Epic": 40, "Legendary": 23, "Zakladatel": 2}

    # Animace
    placeholder = st.empty()
    placeholder.markdown(f'<div class="box-card box-shake"><h2>📦 OTEVÍRÁM {box_type.upper()}...</h2></div>', unsafe_allow_html=True)
    time.sleep(1.8)
    placeholder.empty()

    # Výběr rarity
    rarity = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    
    # Výběr konkrétní postavy (zohledňuje relativní šanci - silnější jsou vzácnější)
    possible = [name for name, d in BRAWLER_STATS.items() if d[0] == rarity]
    sub_weights = [BRAWLER_STATS[name][3] for name in possible]
    result = random.choices(possible, weights=sub_weights)[0]

    # Přidání do invu / Duplikát
    if result in st.session_state.inventory:
        refund = BRAWLER_STATS[result][1] * 5 # Refund je 5x hodinový výnos
        st.session_state.coins += refund
        st.info(f"Máš duplikát! **{result}** se změnil na {refund} 🪙")
    else:
        st.session_state.inventory[result] = 1
        st.balloons()
        st.success(f"NOVÁ POSTAVA: **{result}** ({rarity})!")
    
    save_game()

# --- HLAVNÍ UI ---
st.title("🟠 Ultrido Tycoon: Pro Edition")

# Horní lišta se staty
c_h, g_h = get_income()
col_a, col_b, col_c = st.columns(3)
col_a.metric("Mince", f"{int(st.session_state.coins)} 🪙")
col_b.metric("Gemy", f"{int(st.session_state.gems)} 💎")
col_c.write(f"**Produkce:**\n\n{round(c_h, 1)} 🪙/h | {round(g_h, 1)} 💎/h")

st.divider()

# SEKCE TĚŽBY
st.subheader("⛏️ Sklad a Těžba")
diff = time.time() - st.session_state.last_claim
if diff > 43200: diff = 43200 # 12h limit
mined_c = (c_h / 3600) * diff
mined_g = (g_h / 3600) * diff

c1, c2 = st.columns([2, 1])
c1.write(f"Aktuálně vytěženo: **{round(mined_c, 2)} 🪙** a **{round(mined_g, 2)} 💎**")
if c2.button("💰 VYZVEDNOUT ZISKY", use_container_width=True):
    st.session_state.coins += mined_c
    st.session_state.gems += mined_g
    st.session_state.last_claim = time.time()
    save_game()
    st.rerun()

st.divider()

# SHOP S BOXY
st.header("🛒 Shop s Boxy")
s1, s2, s3 = st.columns(3)

with s1:
    st.markdown('<div class="box-card"><h3>📦 Brawl Box</h3><p>Cena: 100 🪙</p><small>Max: Epic (1%)</small></div>', unsafe_allow_html=True)
    if st.button("KOUPIT BRAWL BOX", key="b1"):
        if st.session_state.coins >= 100:
            st.session_state.coins -= 100
            open_box("Brawl Box")
            st.rerun()
        else: st.error("Nedostatek mincí!")

with s2:
    st.markdown('<div class="box-card" style="border-color: #ff00ff;"><h3>📦 Big Box</h3><p>Cena: 500 🪙</p><small>Vyšší šance na Legendy</small></div>', unsafe_allow_html=True)
    if st.button("KOUPIT BIG BOX", key="b2"):
        if st.session_state.coins >= 500:
            st.session_state.coins -= 500
            open_box("Big Box")
            st.rerun()
        else: st.error("Nedostatek mincí!")

with s3:
    st.markdown('<div class="box-card" style="border-color: #00ccff;"><h3>💎 Mega Box</h3><p>2000 🪙 / 50 💎</p><small>Šance na Zakladatele (2%)</small></div>', unsafe_allow_html=True)
    btn_c, btn_g = st.columns(2)
    if btn_c.button("ZA MINCE"):
        if st.session_state.coins >= 2000:
            st.session_state.coins -= 2000
            open_box("Mega Box")
            st.rerun()
        else: st.error("Málo mincí!")
    if btn_g.button("ZA GEMY"):
        if st.session_state.gems >= 50:
            st.session_state.gems -= 50
            open_box("Mega Box")
            st.rerun()
        else: st.error("Málo gemů!")

st.divider()

# INVENTÁŘ
st.header("🎒 Tvůj Tým Brawlerů")
if not st.session_state.inventory:
    st.info("Zatím nikoho nemáš. Kup si svůj první box!")
else:
    inv_cols = st.columns(5)
    for i, (name, count) in enumerate(st.session_state.inventory.items()):
        stats = BRAWLER_STATS[name]
        with inv_cols[i % 5]:
            st.markdown(f"""
            <div class="brawler-card">
                <div style="font-size: 1.2em; font-weight: bold;">{name}</div>
                <div style="color: #ffcc00; font-size: 0.8em; margin-bottom: 5px;">{stats[0]}</div>
                <div style="font-size: 0.9em;">🪙 {stats[1]}/h</div>
                <div style="font-size: 0.9em;">💎 {stats[2]}/h</div>
            </div>
            """, unsafe_allow_html=True)

# ADMIN SEKCE V SIDEBARU
with st.sidebar:
    st.write("---")
    secret = st.text_input("Admin Kód", type="password")
    if secret == "admin530":
        if st.button("OBNOVIT VŠE"):
            st.session_state.coins = 999999
            st.session_state.gems = 999
            for name in BRAWLER_STATS:
                st.session_state.inventory[name] = 1
            save_game()
            st.rerun()
