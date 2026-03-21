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

# Inicializace session state (paměť aplikace)
if 'money' not in st.session_state:
    saved = load_game()
    st.session_state.money = saved.get("money", 100)
    st.session_state.gems = saved.get("gems", 0)
    st.session_state.inventory = saved.get("inv", [])
    st.session_state.user_name = saved.get("name", "Hráč")
    st.session_state.last_claim_time = saved.get("last", time.time())

# --- DATABÁZE BRAWLERŮ ---
BRAWL_DATA = {
    "COMMON": {"list": ["YouCut Bot (C-1)", "Sběrač Pixelů", "Kluk Střihač", "Zvukový Skřet", "Boxík (Živý)"], "pay": 10},
    "RARE": {"list": ["Filtrová Víla", "Kyber-Editorka", "Brawl Expert", "Glitche-Man", "Lajkovací Golem"], "pay": 30},
    "EPIC": {"list": ["Ultrido Velitel", "Časomág", "Zlatý Střihač", "Hlasový Mág", "Data-Drak"], "pay": 2},
    "LEGEND": {"list": ["Zakladatel (TY)", "Drahokamový Titán", "Algoritmus", "Brawl Král", "YouCut Bůh"], "pay": 15}
}

# --- LOGIKA FARMOVANÍ (OFFLINE PŘÍJEM) ---
def get_rates():
    m_h, g_h = 10, 0
    for b_entry in st.session_state.inventory:
        name_only = b_entry.split(" (")[0]
        for rar, data in BRAWL_DATA.items():
            if name_only in data["list"]:
                if rar in ["COMMON", "RARE"]: m_h += data["pay"]
                else: g_h += data["pay"]
    return m_h, g_h

m_rate, g_rate = get_rates()
now = time.time()
diff = min(now - st.session_state.last_claim_time, 43200) # Stopka po 12h
p_money = int((m_rate / 3600) * diff * 0.5) # 50% výkon offline
p_gems = int((g_rate / 3600) * diff * 0.5)

# --- VZHLED (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: white; font-family: 'Orbitron'; }
    .stButton>button { border-radius: 10px; font-weight: bold; width: 100%; height: 50px; }
    .box-card { padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; border: 3px solid; height: 120px; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÍ PANEL (12 FUNKCÍ + ADMIN) ---
with st.sidebar:
    st.title("⚡ ULTRADO MENU")
    
    # Zadávání jmen a ADMIN LOGIN (Zabezpečený)
starý_n = ulice.stav_relace.uživatelské_jméno
nový_n = ulice.textový_vstup("Tvé jméno:", starý_n)

# Pokud se jméno změní
if nový_n != starý_n:
    # 1. KONTROLA ADMINA (Ultra028)
    if nový_n == "Ultra028":
        # Tady si nastav svoje tajné heslo
        heslo = ulice.textový_vstup("Zadej admin heslo:", tajný=True)
        
        if heslo == "attacker 123": # <--- Tady si přepiš heslo na své
            ulice.stav_relace.uživatelské_jméno = "Ultra028"
            ulice.stav_relace.peníze = 10000
            ulice.stav_relace.drahokamy = 10000
            ulice.úspěch("🔓 ADMIN ÚČET AKTIVOVÁN!")
            uložená_hra()
            ulice.repríza()
        else:
            ulice.varování("Špatné heslo! Přístup zamítnut.")
            # Pokud zadáš špatné heslo, vrátí tě to na staré jméno nebo nulu
            ulice.stav_relace.uživatelské_jméno = "Host" 
            ulice.repríza()

    # 2. KONTROLA BĚŽNÉHO HRÁČE
    else:
        ulice.stav_relace.uživatelské_jméno = nový_n
        # DŮLEŽITÉ: Tady nastavíme startovní hodnoty pro hráče, 
        # aby mu tam nezůstaly peníze z admina!
        ulice.stav_relace.peníze = 100
        ulice.stav_relace.drahokamy = 0
        ulice.informace(f"Vítej ve hře, {nový_n}!")
        uložená_hra()
        ulice.repríza()

ulice.dělič()

# 12 Funkce (zbytek tvého kódu...)
# ...
    
        

    # 12 Funkcí
 with st.expander("📊 1. ODBĚRATELÉ"):
        sub = st.number_input("Aktuálně:", value=0)
        st.write(f"Do milionu zbývá: {1000000 - sub}")
    with st.expander("🌍 2. PŘEKLADAČ"):
        t = st.text_area("CZ:")
        if st.button("Přeložit"): st.write(GoogleTranslator(source='cs', target='en').translate(t))
    with st.expander("🔢 3. KALKULAČKA"):
        n1 = st.number_input("A"); n2 = st.number_input("B")
        st.write(f"Výsledek: {n1+n2}")
    with st.expander("✅ 4. ÚKOLY"):
        st.checkbox("Scénář"); st.checkbox("Nahrávání"); st.checkbox("YouCut Edit")
    with st.expander("🎵 5. TRENDY"): st.write("• Cruel Summer\n• Greedy")
    with st.expander("✂️ 6. YOUCUT TIPY"): st.info("Zkus 'Keyframes' pro animace!")
    with st.expander("🎮 7. BRAWL TIPY"): st.warning("Šetři si super útok!")
    with st.expander("⏱️ 8. SHORTS TIME"): 
        s = st.slider("Sekundy", 0, 60, 15)
        st.write(f"Volno: {60-s}s")
    with st.expander("🔍 9. REŠERŠE"): st.text_input("Wiki téma:")
    with st.expander("🏷️ 10. HASHTAGY"): st.code("#youcut #brawl #ultrado")
    with st.expander("🎒 11. INVENTÁŘ"):
        for b in st.session_state.inventory: st.write(f"• {b}")
    with st.expander("💾 12. RESET"):
        if st.button("Smazat vše"):
            if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
            st.session_state.clear()
            st.rerun()

# --- HLAVNÍ PLOCHA ---
st.title(f"🚀 {st.session_state.user_name.upper()}'S ULTRADO 2.0")

# Statistiky
c1, c2, c3 = st.columns(3)
with c1: st.metric("💰 Peníze", f"{st.session_state.money}")
with c2: st.metric("💎 Gemy", f"{st.session_state.gems}")
with c3:
    if st.button("📥 VYZVEDNOUT VÝDĚLEK", use_container_width=True):
        st.session_state.money += p_money
        st.session_state.gems += p_gems
        st.session_state.last_claim_time = time.time()
        save_game()
        st.balloons(); st.rerun()

st.info(f"Produkce: {m_rate}💰/h | {g_rate}💎/h. V trezoru: {p_money}💰 a {p_gems}💎")

st.divider()

# --- BOX SIMULÁTOR ---
st.subheader("📦 OBCHOD")
b1, b2, b3 = st.columns(3)

def open_box(cost, cur, b_type):
    if cur == "M" and st.session_state.money >= cost: st.session_state.money -= cost
    elif cur == "G" and st.session_state.gems >= cost: st.session_state.gems -= cost
    else: st.error("Nemáš dost peněz!"); return

    # Šance na rarity
    if b_type == "BRAWL": rar = random.choices(["COMMON", "RARE"], weights=[95, 5])[0]
    elif b_type == "BIG": rar = random.choices(["RARE", "EPIC"], weights=[80, 20])[0]
    else: rar = random.choices(["EPIC", "LEGEND"], weights=[93, 7])[0]

    pool = BRAWL_DATA[rar]["list"]
    # Speciální šance na Zakladatele (nejtěžší karta)
    if rar == "LEGEND":
        w = [1 if "Zakladatel" in x else 20 for x in pool]
        drop = random.choices(pool, weights=w)[0]
    else:
        drop = random.choice(pool)

    item = f"{drop} ({rar})"
    if item not in st.session_state.inventory: st.session_state.inventory.append(item)
    save_game()
    
    if "Zakladatel" in item:
        st.balloons()
        st.warning(f"🍀 BOŽSKÝ DROP: {item}!")
    else: st.success(f"Padl ti: {item}")

with b1:
    st.markdown('<div class="box-card" style="border-color: #444; background: #111;"><b>BRAWL BOX</b><br>100 💰</div>', unsafe_allow_html=True)
    if st.button("KOUPIT ČERNÝ"): open_box(100, "M", "BRAWL")
with b2:
    st.markdown('<div class="box-card" style="border-color: #FF8C00; background: #221a00;"><b>BIG BOX</b><br>500 💰</div>', unsafe_allow_html=True)
    if st.button("KOUPIT ORANŽOVÝ"): open_box(500, "M", "BIG")
with b3:
    st.markdown('<div class="box-card" style="border-color: #FFD700; background: #000; box-shadow: 0 0 10px gold;"><b>MEGA BOX</b><br>50 💎</div>', unsafe_allow_html=True)
    if st.button("KOUPIT KARBONOVÝ"): open_box(50, "G", "MEGA")
