import streamlit as st
import time
import random
import json
import os
from datetime import datetime, timedelta

# --- OCHRANA IMPORTU (Aby aplikace nespadla při chybě v requirements.txt) ---
try:
    import wikipediaapi
    from deep_translator import GoogleTranslator
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="ULTRADO 3.0", page_icon="⚡", layout="wide")

# --- DESIGN (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #FF8C00; font-family: 'Orbitron', sans-serif; }
    
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
    
    .box-card { border: 3px solid #FF8C00; border-radius: 20px; padding: 30px; text-align: center; background-color: #1c1f26; }
    .box-shake { animation: shake 0.5s; animation-iteration-count: infinite; border-color: #ff0000; }
    .reveal-card { background: radial-gradient(circle, #2e2e3e 0%, #1a1a1a 100%); border: 5px solid #FF8C00; border-radius: 25px; padding: 50px; text-align: center; color: white; box-shadow: 0 0 50px rgba(255, 140, 0, 0.4); }
    .brawler-card { padding: 15px; border-radius: 12px; background: #1c1f26; border-top: 4px solid #FF8C00; text-align: center; margin-bottom: 15px; }
    .stButton>button { background-color: #FF8C00; color: black; border-radius: 10px; font-weight: bold; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- DATA ---
RARITY_ORDER = {"Zakladatel": 0, "Legendary": 1, "Epic": 2, "Rare": 3, "Common": 4}
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

SAVE_FILE = "save_v3_final.json"

# --- LOGIKA UKLÁDÁNÍ ---
def save_game():
    data = {"coins": st.session_state.coins, "gems": st.session_state.gems, "inventory": st.session_state.inventory, 
            "last_claim": st.session_state.last_claim, "last_wheel": st.session_state.last_wheel, "subs": st.session_state.subs}
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
                st.session_state.subs = data.get("subs", 0)
        except: pass

# --- INICIALIZACE ---
if 'coins' not in st.session_state:
    st.session_state.coins, st.session_state.gems, st.session_state.inventory = 200, 0, {}
    st.session_state.last_claim, st.session_state.last_wheel = time.time(), 0
    st.session_state.last_drop, st.session_state.subs = None, 0
    load_game()

def get_income():
    c_h, g_h = 0, 0
    for name, count in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            c_h += BRAWLER_STATS[name][1] * count
            g_h += BRAWLER_STATS[name][2] * count
    return c_h, g_h

# --- HRA LOGIKA ---
def open_box(box_type):
    if box_type == "Brawl Box": w = {"Common": 85, "Rare": 14, "Epic": 1, "Legendary": 0, "Zakladatel": 0}
    elif box_type == "Big Box": w = {"Common": 50, "Rare": 35, "Epic": 10, "Legendary": 5, "Zakladatel": 0}
    else: w = {"Common": 15, "Rare": 25, "Epic": 35, "Legendary": 23, "Zakladatel": 2}
    
    placeholder = st.empty()
    placeholder.markdown(f'<div class="box-card box-shake"><h2>📦 OTEVÍRÁM {box_type.upper()}...</h2></div>', unsafe_allow_html=True)
    time.sleep(1.5)
    placeholder.empty()
    
    rarity = random.choices(list(w.keys()), weights=list(w.values()))[0]
    result = random.choice([n for n, d in BRAWLER_STATS.items() if d[0] == rarity])
    
    is_new = result not in st.session_state.inventory
    if is_new: st.session_state.inventory[result] = 1
    else: st.session_state.coins += (BRAWLER_STATS[result][1] * 5)
    
    st.session_state.last_drop = {"name": result, "rarity": rarity, "new": is_new}
    save_game()

# --- REVEAL ---
if st.session_state.last_drop:
    drop = st.session_state.last_drop
    st.markdown(f'<div class="reveal-card"><h1>{"✨ NOVÝ!" if drop["new"] else "DUPLIKÁT"}</h1><h2 style="font-size: 3em;">{drop["name"]}</h2><h3>{drop["rarity"]}</h3></div>', unsafe_allow_html=True)
    if st.button("POKRAČOVAT"): st.session_state.last_drop = None; st.rerun()
    st.stop()

# --- CHYBOVÁ HLÁŠKA PRO KNIHOVNY ---
if not IMPORT_SUCCESS:
    st.error("❌ CHYBA: Knihovny wikipedia-api nebo deep-translator nejsou nainstalovány.")
    st.warning("Ujisti se, že máš na GitHubu soubor 'requirements.txt' se správným obsahem a restartuj Streamlit Cloud (Reboot App).")

# --- UI ---
t1, t2 = st.tabs(["🎮 TYCOON HRA", "🎬 STUDIO"])

with t1:
    c_h, g_h = get_income()
    col1, col2, col3 = st.columns(3)
    col1.metric("Mince", f"{int(st.session_state.coins)} 🪙", f"{c_h}/h")
    col2.metric("Gemy", f"{int(st.session_state.gems)} 💎", f"{g_h}/h")
    col3.metric("Odběratelé", f"{st.session_state.subs}")
    
    st.divider()
    b1, b2, b3 = st.columns(3)
    if b1.button("BRAWL BOX (100 🪙)"):
        if st.session_state.coins >= 100: st.session_state.coins -= 100; open_box("Brawl Box"); st.rerun()
    if b2.button("BIG BOX (500 🪙)"):
        if st.session_state.coins >= 500: st.session_state.coins -= 500; open_box("Big Box"); st.rerun()
    if b3.button("MEGA BOX (50 💎)"):
        if st.session_state.gems >= 50: st.session_state.gems -= 50; open_box("Mega Box"); st.rerun()
        
    st.header("🎒 Inventář")
    if st.session_state.inventory:
        inv = sorted(st.session_state.inventory.items(), key=lambda x: RARITY_ORDER[BRAWLER_STATS[x[0]][0]])
        cols = st.columns(4)
        for i, (name, count) in enumerate(inv):
            with cols[i % 4]:
                st.markdown(f'<div class="brawler-card"><b>{name}</b><br><small>{BRAWLER_STATS[name][0]}</small></div>', unsafe_allow_html=True)

with t2:
    st.header("🎬 Studio")
    vstup = st.text_input("Téma videa:")
    
    if st.button("📖 Wikipedie Hledání"):
        if IMPORT_SUCCESS and vstup:
            try:
                wiki = wikipediaapi.Wikipedia(language='cs', user_agent='Ultrado/1.0')
                page = wiki.page(vstup)
                if page.exists(): st.write(page.summary[:400] + "...")
                else: st.warning("Téma nebylo nalezeno.")
            except: st.error("Chyba při spojení s Wikipedií.")
        elif not IMPORT_SUCCESS: st.error("Funkce vypnuta - chybí knihovna.")

    if st.button("🌍 Přeložit téma do EN"):
        if IMPORT_SUCCESS and vstup:
            st.success(GoogleTranslator(source='cs', target='en').translate(vstup))

with st.sidebar:
    st.title("⚙️ Nastavení")
    st.session_state.subs = st.number_input("Subs:", value=st.session_state.subs)
    if st.button("🔄 RESET"): st.session_state.clear(); st.rerun()
    code = st.text_input("Admin", type="password")
    if code == "admin530" and st.button("CHEAT"):
        st.session_state.coins, st.session_state.gems = 99999, 999
        for n in BRAWLER_STATS: st.session_state.inventory[n] = 1
        save_game(); st.rerun()
