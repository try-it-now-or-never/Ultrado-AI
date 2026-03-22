import streamlit as st
import time
import random

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Ultrido Tycoon", page_icon="🟠")

# --- DATA BRAWLERŮ ---
RARITY_SETTINGS = {
    "Common": {"chance": 70, "refund": 10, "income": 5},
    "Rare": {"chance": 20, "refund": 40, "income": 15},
    "Epic": {"chance": 8, "refund": 150, "income": 50},
    "Legendary": {"chance": 1.9, "refund": 500, "income": 200},
    "Zakladatel": {"chance": 0.1, "refund": 2000, "income": 1000}
}

BRAWLERS = {
    "YouCut Bot": "Common", "Sběrač Pixelů": "Common", "Kluk Střihač": "Common",
    "Boxík": "Common", "Filtrová Víla": "Rare", "Brawl Expert": "Rare",
    "Ultrido Velitel": "Epic", "Zlatý Střihač": "Epic", "Data-Drak": "Epic",
    "Drahokamový Titán": "Legendary", "Brawl Král": "Legendary",
    "Zakladatel (TY)": "Zakladatel"
}

# --- INICIALIZACE STAVU ---
if 'coins' not in st.session_state:
    st.session_state.coins = 200
    st.session_state.inventory = {} # Použijeme slovník pro počty kusů
    st.session_state.last_claim = time.time()

# --- POMOCNÉ FUNKCE ---
def get_total_income_per_hour():
    total_h = 0
    for name, count in st.session_state.inventory.items():
        rarity = BRAWLERS[name]
        total_h += RARITY_SETTINGS[rarity]["income"] * count
    return total_h

def get_current_mining():
    now = time.time()
    diff_seconds = now - st.session_state.last_claim
    
    # Limit 12 hodin
    is_capped = False
    if diff_seconds > 43200:
        diff_seconds = 43200
        is_capped = True
    
    income_per_second = get_total_income_per_hour() / 3600
    return round(income_per_second * diff_seconds, 2), is_capped

# --- UI / SIDEBAR ---
st.title("🟠 Ultrido Tycoon")

with st.sidebar:
    st.header("👤 Tvůj Profil")
    st.metric("Mince", f"{int(st.session_state.coins)} 🪙")
    st.write(f"Zisk: `{get_total_income_per_hour()}` mincí/h")
    
    st.divider()
    secret = st.text_input("Admin Kód", type="password")
    if secret == "admin530":
        if st.button("AKTIVOVAT VŠE"):
            st.session_state.coins = 999999
            for name in BRAWLERS:
                st.session_state.inventory[name] = st.session_state.inventory.get(name, 0) + 1
            st.success("Admin mod aktivní!")

# --- HLAVNÍ SEKCE: TĚŽBA ---
st.subheader("⛏️ Těžební centrum")
mined, capped = get_current_mining()

col1, col2 = st.columns([2, 1])
col1.metric("Aktuálně k vyzvednutí", f"{mined} 🪙")

if capped:
    st.warning("⚠️ Sklad je plný! (Max 12h)")

if col2.button("💰 VYZVEDNOUT", use_container_width=True):
    if mined > 0:
        st.session_state.coins += mined
        st.session_state.last_claim = time.time()
        st.rerun()
    else:
        st.toast("Zatím jsi nic nevykopal!")

st.divider()

# --- OBCHOD ---
st.header("📦 Shop")
if st.button("Otevřít Brawl Box (100 🪙)", use_container_width=True):
    if st.session_state.coins >= 100:
        st.session_state.coins -= 100
        
        # Logika padání podle šancí
        rarities = list(RARITY_SETTINGS.keys())
        weights = [RARITY_SETTINGS[r]["chance"] for r in rarities]
        chosen_rarity = random.choices(rarities, weights=weights)[0]
        
        # Výběr náhodného brawlera z dané rarity
        possible_brawlers = [name for name, rar in BRAWLERS.items() if rar == chosen_rarity]
        res = random.choice(possible_brawlers)
        
        # Přidání do inventáře
        if res in st.session_state.inventory:
            refund = RARITY_SETTINGS[chosen_rarity]["refund"]
            st.session_state.coins += refund
            st.info(f"Duplikát! **{res}** se změnil na {refund} 🪙")
        else:
            st.session_state.inventory[res] = 1
            st.balloons()
            st.success(f"NOVÝ BRAWLER: **{res}** ({chosen_rarity})!")
    else:
        st.error("Nemáš dost mincí!")

# --- INVENTÁŘ ---
st.header("🎒 Tvůj Inventář")
if not st.session_state.inventory:
    st.info("Zatím nemáš žádné brawlery. Utíkej do shopu!")
else:
    cols = st.columns(3)
    for idx, (name, count) in enumerate(st.session_state.inventory.items()):
        rarity = BRAWLERS[name]
        with cols[idx % 3]:
            st.markdown(f"**{name}**")
            st.caption(f"Rarita: {rarity}")
            st.write(f"Počet: {count}x")
