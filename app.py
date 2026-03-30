import streamlit as st
import time
import random
import json
import os
import wikipedie
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="ULTRADO 3.0: TYCOON & STUDIO", page_icon="⚡", layout="wide")

# --- DESIGN (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    /* Globální styl */
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #FF8C00; font-family: 'Orbitron', sans-serif; }
    
    /* Animace boxu */
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
        border: 3px solid #FF8C00; border-radius: 20px;
        padding: 30px; text-align: center; background-color: #1c1f26;
    }
    .box-shake { animation: shake 0.5s; animation-iteration-count: infinite; border-color: #ff0000; }
    
    .reveal-card {
        background: radial-gradient(circle, #2e2e3e 0%, #1a1a1a 100%);
        border: 5px solid #FF8C00; border-radius: 25px;
        padding: 50px; text-align: center; color: white;
        box-shadow: 0 0 50px rgba(255, 140, 0, 0.4);
    }
    
    .brawler-card {
        padding: 15px; border-radius: 12px; background: #1c1f26;
        border-top: 4px solid #FF8C00; text-align: center; margin-bottom: 15px;
    }
    
    /* Tlačítka */
    .stButton>button { background-color: #FF8C00; color: black; border-radius: 10px; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

# --- KONSTANTY A DATA ---
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

SAVE_FILE = "ultrido_mega_save.json"

# --- SYSTÉM UKLÁDÁNÍ ---
def save_game():
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel,
        "subs": st.session_state.get('subs', 0)
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
                st.session_state.subs = data.get("subs", 0)
        except: pass

# --- INICIALIZACE ---
if 'coins' not in st.session_state:
    st.session_state.coins, st.session_state.gems, st.session_state.inventory = 200, 0, {}
    st.session_state.last_claim = time.time()
    st.session_state.last_wheel = 0
    st.session_state.last_drop = None
    st.session_state.subs = 0
    load_game()

def get_income():
    c_h, g_h = 0, 0
    for name, count in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            c_h += BRAWLER_STATS[name][1] * count
            g_h += BRAWLER_STATS[name][2] * count
    return c_h, g_h

# --- HERNÍ LOGIKA ---
def open_box(box_type):
    if box_type == "Brawl Box": weights = {"Common": 84, "Rare": 15, "Epic": 1, "Legendary": 0, "Zakladatel": 0}
    elif box_type == "Big Box": weights = {"Common": 45, "Rare": 35, "Epic": 15, "Legendary": 5, "Zakladatel": 0}
    else: weights = {"Common": 10, "Rare": 25, "Epic": 40, "Legendary": 23, "Zakladatel": 2}

    placeholder = st.empty()
    placeholder.markdown(f'<div class="box-card box-shake"><h2>📦 OTEVÍRÁM {box_type.upper()}...</h2></div>', unsafe_allow_html=True)
    time.sleep(1.8)
    placeholder.empty()

    rarity = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    result = random.choices([n for n, d in BRAWLER_STATS.items() if d[0] == rarity], 
                            weights=[BRAWLER_STATS[n][3] for n in BRAWLER_STATS if BRAWLER_STATS[n][0] == rarity])[0]

    is_new = result not in st.session_state.inventory
    if is_new: st.session_state.inventory[result] = 1
    else: st.session_state.coins += (BRAWLER_STATS[result][1] * 5)
    
    st.session_state.last_drop = {"name": result, "rarity": rarity, "new": is_new}
    save_game()

def spin_wheel():
    placeholder = st.empty()
    placeholder.markdown('<div class="box-card box-shake"><h2>🎡 KOLO ŠTĚSTÍ SE TOČÍ...</h2></div>', unsafe_allow_html=True)
    time.sleep(2)
    placeholder.empty()
    roll = random.random() * 100
    if roll <= 0.01: 
        res = random.choice([n for n, d in BRAWLER_STATS.items() if d[0] == "Rare"])
        typ = "RARE POSTAVA"
    elif roll <= 0.26: 
        st.session_state.gems += 5
        res, typ = "5 GEMŮ", "DRAHOKAMY"
    elif roll <= 5.26: 
        res = random.choice([n for n, d in BRAWLER_STATS.items() if d[0] == "Common"])
        typ = "COMMON POSTAVA"
    elif roll <= 16.26: 
        amt = random.randint(250, 750)
        st.session_state.coins += amt
        res, typ = f"{amt} MINCÍ", "PENÍZE"
    else: res, typ = "Zkus to znovu příště!", "NIC"
    if "POSTAVA" in typ:
        if res in st.session_state.inventory: st.session_state.coins += 50; res = f"Duplikát {res} (+50 🪙)"
        else: st.session_state.inventory[res] = 1
    st.session_state.last_drop = {"name": res, "rarity": typ, "new": True}
    save_game()

# --- REVEAL OKNO ---
if st.session_state.last_drop:
    drop = st.session_state.last_drop
    st.markdown(f'<div class="reveal-card"><h1>🎁 VÝSLEDEK</h1><h2 style="font-size: 3em;">{drop["name"]}</h2><h3>{drop["rarity"]}</h3></div>', unsafe_allow_html=True)
    if st.button("POKRAČOVAT", use_container_width=True):
        st.session_state.last_drop = None
        st.rerun()
    st.stop()

# --- BOČNÍ PANEL (STUDIO NÁSTROJE) ---
with st.sidebar:
    st.title("⚡ ULTRADO STUDIO")
    
    # CESTA KE SLÁVĚ
    st.subheader("📊 CESTA KE SLÁVĚ")
    st.session_state.subs = st.number_input("Aktuální odběratelé:", value=st.session_state.subs)
    cil = st.number_input("Můj cíl (subs):", value=100)
    if cil > 0:
        procenta = min(100, int((st.session_state.subs / cil) * 100))
        st.progress(procenta / 100)
        st.write(f"Postup: {procenta}%")
        if st.session_state.subs >= cil: st.success("CÍL SPLNĚN! 🏆"); st.balloons()

    st.divider()

    # ÚKOLY
    with st.expander("✅ MOJE ÚKOLY"):
        st.checkbox("Vymyslet téma")
        st.checkbox("Natočit video")
        st.checkbox("Sestříhat (YouCut)")
        st.checkbox("Vydat na YouTube")

    # TRENDY A HLEDÁNÍ
    with st.expander("🔍 HLEDAT NA SÍTÍCH"):
        q = st.text_input("Hledat téma:")
        if q:
            st.markdown(f"👉 [YouTube](https://www.youtube.com/results?search_query={q})")
            st.markdown(f"👉 [TikTok](https://www.tiktok.com/search?q={q})")

    # PŘEKLADAČ
    with st.expander("🌍 PŘEKLADAČ"):
        t = st.text_area("Česky:")
        if st.button("Přeložit"):
            if t: st.success(GoogleTranslator(source='cs', target='en').translate(t))

    # KALKULAČKA
    with st.expander("🔢 KALKULAČKA"):
        n1 = st.number_input("Číslo 1", value=0.0)
        n2 = st.number_input("Číslo 2", value=0.0)
        op = st.selectbox("Operace", ["+", "-", "*", "/"])
        if st.button("Vypočítej"):
            if op == "+": res = n1+n2
            elif op == "-": res = n1-n2
            elif op == "*": res = n1*n2
            elif op == "/": res = n1/n2 if n2 != 0 else "Chyba"
            st.code(res)

    st.divider()
    if st.button("🔄 RESET CELÉ HRY"):
        st.session_state.clear(); st.rerun()

# --- HLAVNÍ PLOCHA ---
tab1, tab2 = st.tabs(["🎮 TYCOON HRA", "🎬 PRODUKČNÍ PANEL"])

with tab1:
    c_h, g_h = get_income()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Mince", f"{int(st.session_state.coins)} 🪙")
    col_b.metric("Gemy", f"{int(st.session_state.gems)} 💎")
    col_c.write(f"Produkce: {round(c_h, 1)}🪙/h | {round(g_h, 1)}💎/h")

    # Kolo štěstí
    st.subheader("🎡 Kolo štěstí")
    time_passed = time.time() - st.session_state.last_wheel
    is_free = time_passed >= 86400
    cw1, cw2, cw3 = st.columns(3)
    with cw1:
        if is_free:
            if st.button("🎰 ZDARMA (Daily Reward)", use_container_width=True):
                st.session_state.last_wheel = time.time(); spin_wheel(); st.rerun()
        else:
            st.info(f"Další zdarma za: {str(timedelta(seconds=int(86400 - time_passed))).split('.')[0]}")
    with cw2:
        if st.button("🎰 TOČIT ZA 300 🪙", use_container_width=True):
            if st.session_state.coins >= 300: st.session_state.coins -= 300; spin_wheel(); st.rerun()
    with cw3:
        if st.button("🎰 TOČIT ZA 15 💎", use_container_width=True):
            if st.session_state.gems >= 15: st.session_state.gems -= 15; spin_wheel(); st.rerun()

    st.divider()
    
    # Sklad a Shop
    s_col1, s_col2 = st.columns([1, 2])
    with s_col1:
        st.subheader("⛏️ Sklad")
        diff = min(time.time() - st.session_state.last_claim, 43200)
        mined_c, mined_g = (c_h/3600)*diff, (g_h/3600)*diff
        st.write(f"Vytěženo: {round(mined_c,1)} 🪙")
        if st.button("💰 VYZVEDNOUT VŠE", use_container_width=True):
            st.session_state.coins += mined_c; st.session_state.gems += mined_g
            st.session_state.last_claim = time.time(); save_game(); st.rerun()

    with s_col2:
        st.subheader("📦 Shop")
        sh1, sh2, sh3 = st.columns(3)
        if sh1.button("BRAWL BOX (100 🪙)"):
            if st.session_state.coins >= 100: st.session_state.coins -= 100; open_box("Brawl Box"); st.rerun()
        if sh2.button("BIG BOX (500 🪙)"):
            if st.session_state.coins >= 500: st.session_state.coins -= 500; open_box("Big Box"); st.rerun()
        if sh3.button("MEGA BOX (2000 🪙)"):
            if st.session_state.coins >= 2000: st.session_state.coins -= 2000; open_box("Mega Box"); st.rerun()

    st.divider()
    
    # Inventář
    st.header("🎒 Inventář (Seřazeno)")
    if st.session_state.inventory:
        sorted_inv = sorted(st.session_state.inventory.items(), key=lambda x: RARITY_ORDER[BRAWLER_STATS[x[0]][0]])
        cols = st.columns(5)
        for i, (name, count) in enumerate(sorted_inv):
            stats = BRAWLER_STATS[name]
            r_c = {"Common": "#FFF", "Rare": "#0F0", "Epic": "#F0F", "Legendary": "#FF0", "Zakladatel": "#F40"}[stats[0]]
            with cols[i % 5]:
                st.markdown(f'<div class="brawler-card" style="border-top-color:{r_c}"><b style="color:{r_c}">{name}</b><br><small>{stats[0]}</small><br>{stats[1]}🪙/h</div>', unsafe_allow_html=True)

with tab2:
    st.header("🎬 HLAVNÍ PANEL ULTRADO")
    vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Zadej téma videa...", key="studio_vstup")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎥 Produkce")
        if st.button("✂️ YouCut Tipy"): st.info("Zkus 'Keyframes' pro plynulý zoom!")
        if st.button("📺 Návrhy názvů"):
            if vstup: st.success(random.choice([f"Šílený {vstup}!", f"Jak na {vstup}", f"Tohle o {vstup} nevíš!"]))
        if st.button("🔥 Brutální Hook"):
            if vstup: st.warning(f"Vsadím se, že o {vstup} jsi tohle nevěděl!")

    with col2:
        st.subheader("📚 Rešerše")
        if st.button("📖 Wikipedie"):
            if vstup:
                try:
                    wiki = wikipediaapi.Wikipedia(language='cs', user_agent='Ultrado/1.0')
                    st.write(wiki.page(vstup).summary[:250] + "...")
                except: st.error("Nepodařilo se spojit s Wikipedií.")
        if st.button("🏷️ Hashtagy"):
            st.code(f"#{vstup.replace(' ', '') if vstup else 'video'} #youcut #viral")

    if st.button("📝 GENERUJ KOMPLETNÍ PLÁN"):
        if vstup:
            st.balloons()
            st.subheader(f"📋 Plán pro: {vstup}")
            st.write("1. Úvod: Hook (Zaujmout do 3 sekund)\n2. Střed: Hlavní info/Gameplay\n3. Outro: Výzva k odběru (CTA)!")

# ADMIN KÓD
with st.sidebar:
    st.divider()
    code = st.text_input("Admin Mod", type="password")
    if code == "admin530" and st.button("AKTIVOVAT VŠE"):
        st.session_state.coins, st.session_state.gems = 999999, 999
        for n in BRAWLER_STATS: st.session_state.inventory[n] = 1
        save_game(); st.rerun()
