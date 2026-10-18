import streamlit as st
import streamlit.components.v1 as components
import time
import random
import json
import os
import hashlib
from datetime import datetime, timedelta
from supabase import create_client, Client

# ---------------- AI IMPORT (GROQ) ----------------

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ---------------- SUPABASE PŘIPOJENÍ ----------------

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    supabase = None

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- IMPORTY ----------------

try:
    import wikipediaapi
    from deep_translator import GoogleTranslator
    IMPORT_ERR = False
except ImportError:
    IMPORT_ERR = True

# ---------------- NASTAVENÍ ----------------

st.set_page_config(
    page_title="Ultrado",
    page_icon="🎮",
    layout="wide"
)

# ---------------- DATABÁZE 25 HALLOWEENSKÝCH POSTAV ----------------

HALLOWEEN_CHARACTERS = [
    # Common (🟢)
    {"id": "h1", "name": "Zombie Střihač", "rarity": "🟢 Common", "type": "coins", "price": 150, "cph": 6, "gph": 0, "desc": "Zelený zombie se sluchátky, uvolněná ruka mu padá na klávesnici."},
    {"id": "h2", "name": "Kameraman Kostlivec", "rarity": "🟢 Common", "type": "coins", "price": 300, "cph": 15, "gph": 0, "desc": "Chrastící kostra drží starou, prachem pokrytou kameru."},
    {"id": "h3", "name": "Pavučinový Zvukař", "rarity": "🟢 Common", "type": "coins", "price": 500, "cph": 25, "gph": 0, "desc": "Postava celá obmotaná pavučinami drží mikrofon pokrytý prachem."},
    {"id": "h4", "name": "Thumbnail Mumie", "rarity": "🟢 Common", "type": "coins", "price": 700, "cph": 38, "gph": 0, "desc": "Mumie se snaží kreslit na tablet, obvazy se jí pletou do stylusu."},
    {"id": "h5", "name": "Netopýří Scenárista", "rarity": "🟢 Common", "type": "coins", "price": 900, "cph": 50, "gph": 0, "desc": "Vlkodlak v lidské formě píše scénář, kolem něj krouží netopýři."},
    
    # Rare (🔵)
    {"id": "h6", "name": "Frankensteinův Střihač", "rarity": "🔵 Rare", "type": "coins", "price": 1500, "cph": 80, "gph": 0, "desc": "Obrovské monstrum se sešívanou kůží, monitory jiskří elektrickými výboji."},
    {"id": "h7", "name": "Duch Animátor 👻", "rarity": "🔵 Rare", "type": "coins", "price": 2200, "cph": 120, "gph": 0, "desc": "Průhledný duch, vznáší se nad klávesnicí a hýbe myší bez doteku."},
    {"id": "h8", "name": "Vampire Dron 🦇", "rarity": "🔵 Rare", "type": "coins", "price": 3000, "cph": 180, "gph": 0, "desc": "Upír v plášti ovládá dron, který vypadá jako mechanický netopýr."},
    {"id": "h9", "name": "Čarodějnice Social Media", "rarity": "🔵 Rare", "type": "coins", "price": 4000, "cph": 250, "gph": 0, "desc": "Čarodějnice míchá lektvar v kotli, ze kterého vylétávají ikony sítí."},
    {"id": "h10", "name": "Kat Režisér", "rarity": "🔵 Rare", "type": "coins", "price": 5500, "cph": 350, "gph": 0, "desc": "Postava v kapuci na režisérské židli místo klapky používá sekeru."},
    
    # Epic (🟣)
    {"id": "h11", "name": "Streamer Vlkodlak", "rarity": "🟣 Epic", "type": "coins", "price": 9000, "cph": 600, "gph": 0, "desc": "Vlkodlak v plné formě kroutí hlavou u RGB mikrofonu a vyje do kamery."},
    {"id": "h12", "name": "VFX Demon", "rarity": "🟣 Epic", "type": "coins", "price": 13000, "cph": 850, "gph": 0, "desc": "Rohatec s rudou kůží, monitory mu hoří pekelným ohněm."},
    {"id": "h13", "name": "Krvavý Producer", "rarity": "🟣 Epic", "type": "coins", "price": 19000, "cph": 1200, "gph": 0, "desc": "Upír v drahém obleku, mixážní pult má červená tlačítka jako kapky krve."},
    {"id": "h14", "name": "Clickbait Smrťák", "rarity": "🟣 Epic", "type": "coins", "price": 27000, "cph": 1800, "gph": 0, "desc": "Smrtka s kosou, na které visí obří svítící žlutý vykřičník."},
    {"id": "h15", "name": "Hrobník Manažer", "rarity": "🟣 Epic", "type": "coins", "price": 38000, "cph": 2500, "gph": 0, "desc": "Hrobník s rýčem stojí u hrobů padlých sponzorů."},
    
    # Legendary (🟡)
    {"id": "h16", "name": "AI Dýňový Bot", "rarity": "🟡 Legendary", "type": "gems", "price": 20, "cph": 4000, "gph": 0.1, "desc": "Robot s dýní místo hlavy, oči svítí červeně, tvoří videa z ektoplazmy."},
    {"id": "h17", "name": "Viral Duch", "rarity": "🟡 Legendary", "type": "gems", "price": 30, "cph": 6000, "gph": 0.2, "desc": "Průhledný duch s řetězy vznášející se na vrcholu grafové křivky."},
    {"id": "h18", "name": "Algoritmus z Pekla", "rarity": "🟡 Legendary", "type": "gems", "price": 50, "cph": 9000, "gph": 0.5, "desc": "Temná bytost s rohy složená z hořícího kódu a pentagramu."},
    {"id": "h19", "name": "Hrad Drákuly Studio", "rarity": "🟡 Legendary", "type": "gems", "price": 75, "cph": 14000, "gph": 1.0, "desc": "Obrovský temný hrad na skále, okna svítí fialově."},
    
    # Event Exclusive (🎃)
    {"id": "h20", "name": "Bezhlavý Editor", "rarity": "🎃 Event", "type": "coins", "price": 2000, "cph": 100, "gph": 0, "desc": "Postava bez hlavy, hlavu má položenou na stole vedle klávesnice."},
    {"id": "h21", "name": "Zombie Kameraman", "rarity": "🎃 Event", "type": "coins", "price": 6500, "cph": 450, "gph": 0, "desc": "Zombie s kamerou, kterému odpadává ruka, ale stále drží spoušť."},
    {"id": "h22", "name": "Pumpkin King 🎃", "rarity": "🎃 Event", "type": "gems", "price": 25, "cph": 4500, "gph": 0.2, "desc": "Postava s hořící dýní místo hlavy drží zlaté YouTube tlačítko."},
    {"id": "h23", "name": "Zombie Scriptwriter", "rarity": "🎃 Event", "type": "gems", "price": 12, "cph": 2200, "gph": 0, "desc": "Zombie píšící na starém psacím stroji bez přestávky."},
    {"id": "h24", "name": "Duch Creator 👻🛠️", "rarity": "🎃 Event", "type": "gems", "price": 120, "cph": 22000, "gph": 2.0, "desc": "Průhledný duch programátora sedící u kódu Ultrada."},
    {"id": "h25", "name": "Zlatá Halloweenská Trofej 🏆", "rarity": "🎃 Event", "type": "gems", "price": 90, "cph": 17000, "gph": 1.5, "desc": "Zlatá dýně se štítkem s YouTube tlačítkem na podstavci."}
]

HW_CHAR_MAP = {c["id"]: c for c in HALLOWEEN_CHARACTERS}

# ---------------- SUPABASE SYSTÉM PŘIHLÁŠENÍ & UKLÁDÁNÍ ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# Standardní nastavení proměnných hry
if "coins" not in st.session_state:
    st.session_state.coins = 200

if "gems" not in st.session_state:
    st.session_state.gems = 0

if "inventory" not in st.session_state:
    st.session_state.inventory = {}

if "last_claim" not in st.session_state:
    st.session_state.last_claim = time.time()

if "last_wheel" not in st.session_state:
    st.session_state.last_wheel = 0

if "subs" not in st.session_state:
    st.session_state.subs = 0

if "last_drop" not in st.session_state:
    st.session_state.last_drop = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Halloweenské proměnné v session state
if "last_daily_claim" not in st.session_state:
    st.session_state.last_daily_claim = ""

if "owned_characters" not in st.session_state:
    st.session_state.owned_characters = []

if "gems_per_hour" not in st.session_state:
    st.session_state.gems_per_hour = 0.0


def save_game():
    """Uloží data do Supabase (pokud je hráč přihlášen) i do localStorage."""
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel,
        "subs": st.session_state.subs,
        "last_daily_claim": st.session_state.last_daily_claim,
        "owned_characters": st.session_state.owned_characters,
        "gems_per_hour": st.session_state.gems_per_hour
    }
    
    # 1. Uložení do Supabase Cloud Databáze
    if st.session_state.logged_in and supabase:
        try:
            supabase.table("players").update({
                "save_data": data,
                "last_daily_claim": st.session_state.last_daily_claim,
                "owned_characters": st.session_state.owned_characters,
                "gems_per_hour": st.session_state.gems_per_hour
            }).eq("username", st.session_state.username).execute()
        except Exception:
            pass

    # 2. Záložní uložení přímo do prohlížeče (localStorage)
    json_str = json.dumps(data)
    js_code = f"""
    <script>
        localStorage.setItem('ultrado_user_save', '{json_str}');
    </script>
    """
    components.html(js_code, height=0, width=0)


# --- OKNO PŘIHLÁŠENÍ (ZOBRAZÍ SE, POKUD HRÁČ NENÍ PŘIHLÁŠEN) ---
if not st.session_state.logged_in:
    st.title("⚡ ULTRADO — Přihlášení")
    
    tab_login, tab_register = st.tabs(["🔑 Přihlášení", "📝 Registrace"])
    
    with tab_login:
        l_user = st.text_input("Uživatelské jméno", key="login_user")
        l_pass = st.text_input("Heslo", type="password", key="login_pass")
        
        if st.button("Přihlásit se"):
            if l_user and l_pass and supabase:
                hashed = hash_password(l_pass)
                res = supabase.table("players").select("*").eq("username", l_user).eq("password_hash", hashed).execute()
                
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.username = l_user
                    user_data = res.data[0].get("save_data") or {}
                    
                    # Načtení dat ze Supabase
                    st.session_state.coins = user_data.get("coins", 200)
                    st.session_state.gems = user_data.get("gems", 0)
                    st.session_state.inventory = user_data.get("inventory", {})
                    st.session_state.last_claim = user_data.get("last_claim", time.time())
                    st.session_state.last_wheel = user_data.get("last_wheel", 0)
                    st.session_state.subs = user_data.get("subs", 0)
                    st.session_state.last_daily_claim = user_data.get("last_daily_claim", res.data[0].get("last_daily_claim", ""))
                    st.session_state.owned_characters = user_data.get("owned_characters", res.data[0].get("owned_characters", []))
                    st.session_state.gems_per_hour = user_data.get("gems_per_hour", res.data[0].get("gems_per_hour", 0.0))
                    
                    st.success(f"Vítej zpět, {l_user}!")
                    st.rerun()
                else:
                    st.error("Nespravné jméno nebo heslo!")
            else:
                st.warning("Vyplň všechna pole.")

    with tab_register:
        r_user = st.text_input("Nové uživatelské jméno", key="reg_user")
        r_pass = st.text_input("Nové heslo", type="password", key="reg_pass")
        
        if st.button("Vytvořit účet"):
            if r_user and r_pass and supabase:
                check = supabase.table("players").select("*").eq("username", r_user).execute()
                if check.data:
                    st.error("Toto jméno už existuje!")
                else:
                    hashed = hash_password(r_pass)
                    default_save = {
                        "coins": 200,
                        "gems": 0,
                        "inventory": {},
                        "last_claim": time.time(),
                        "last_wheel": 0,
                        "subs": 0,
                        "last_daily_claim": "",
                        "owned_characters": [],
                        "gems_per_hour": 0.0
                    }
                    supabase.table("players").insert({
                        "username": r_user,
                        "password_hash": hashed,
                        "save_data": default_save,
                        "last_daily_claim": "",
                        "owned_characters": [],
                        "gems_per_hour": 0.0
                    }).execute()
                    
                    st.success("Účet vytvořen! Nyní se můžeš přihlásit.")
            else:
                st.warning("Vyplň všechna pole.")

        st.caption("ℹ️ Registrací souhlasíš s uložením herních dat pod zvolenou přezdívkou. Nepoužívej jako přezdívku své reálné jméno.")
                
    st.stop()


# ---------------- DATA ----------------

RARITY_ORDER = {
    "Zakladatel": 0,
    "Legendary": 1,
    "Mythic": 2,
    "Epic": 3,
    "Rare": 4,
    "Common": 5
}

BRAWLER_STATS = {
    "YouCut Bot": ["Common", 5, 0],
    "Ultrado Pixel": ["Common", 7, 0],
    "Kluk Střihač": ["Common", 10, 0],
    "Kódový Prach": ["Common", 12, 0],
    "Mikrofonní Šum": ["Common", 15, 0],
    "Hledač Coinů": ["Common", 18, 0],
    "Sběrač Pixelů": ["Common", 20, 0],
    "Ultra Bot": ["Common", 22, 0],
    "Shorts Klikač": ["Common", 25, 0],
    "Filtrová Víla": ["Rare", 35, 0],
    "Digitální Duch": ["Rare", 42, 0],
    "Brawl Expert": ["Rare", 50, 0],
    "Ztracený Pixel": ["Rare", 58, 0],
    "Ultrado Editor": ["Rare", 65, 0],
    "Editor": ["Rare", 70, 0],
    "Zvukový Mistr": ["Rare", 78, 0],
    "Ultra Střihač": ["Rare", 85, 0],
    "Kamera Machr": ["Rare", 90, 0],
    "Ultrido Velitel": ["Epic", 105, 0],
    "Sběrač Coinů": ["Epic", 120, 0],
    "Zlatý Střihač": ["Epic", 135, 0],
    "Tajemný Sidebar": ["Epic", 150, 0],
    "Renderovací Král": ["Epic", 170, 0],
    "Matematický Král": ["Epic", 185, 0],
    "Ultrado Zaměstnanec": ["Epic", 200, 0],
    "Algoritmus Master": ["Epic", 215, 0],
    "Data-Drak": ["Mythic", 250, 0.3],
    "Ultrado Manažer": ["Mythic", 300, 0.4],
    "Kódový Architekt": ["Mythic", 380, 0.5],
    "Kódový Génius": ["Mythic", 450, 0.6],
    "Analytický Magnát": ["Mythic", 520, 0.7],
    "Brawl Taktik": ["Mythic", 580, 0.8],
    "Studio Inženýr": ["Mythic", 640, 0.9],
    "Stream Star": ["Mythic", 700, 1.0],
    "Drahokamový Titán": ["Legendary", 900, 2.0],
    "Zlatý Klikač": ["Legendary", 1100, 2.5],
    "Brawl Král": ["Legendary", 1300, 3.2],
    "Ultrado Titan": ["Legendary", 1500, 3.8],
    "Ultrado MISTR": ["Legendary", 1650, 4.4],
    "Ultrado Vizionář": ["Legendary", 1800, 5.0],
    "Zakladatel Ultrado": ["Zakladatel", 3500, 12.0]
}

# ---------------- POMOCNÉ FUNKCE ----------------

def get_income():
    coins_h = 0
    gems_h = st.session_state.gems_per_hour

    for name, item_data in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            if isinstance(item_data, dict):
                level = item_data.get("level", 1)
            else:
                level = item_data

            multiplier = 1 + (level - 1) * 0.20
            
            coins_h += BRAWLER_STATS[name][1] * multiplier
            gems_h += BRAWLER_STATS[name][2] * multiplier

    # Přičtení příjmu z halloweenských postav
    for char_id in st.session_state.owned_characters:
        if char_id in HW_CHAR_MAP:
            coins_h += HW_CHAR_MAP[char_id]["cph"]
            gems_h += HW_CHAR_MAP[char_id]["gph"]

    return round(coins_h, 1), round(gems_h, 1)


def open_box(box_type):

    if box_type == "Brawl Box":
        chances = {
            "Common": 80,
            "Rare": 18,
            "Epic": 2,
            "Mythic": 0,
            "Legendary": 0,
        }

    elif box_type == "Big Box":
        chances = {
            "Common": 45,
            "Rare": 35,
            "Epic": 14,
            "Mythic": 5,
            "Legendary": 1,
        }

    else:
        chances = {
            "Common": 15,
            "Rare": 25,
            "Epic": 30,
            "Mythic": 20,
            "Legendary": 8,
            "Zakladatel": 2,
        }

    rarity = random.choices(
        list(chances.keys()),
        weights=list(chances.values())
    )[0]

    available = [
        name
        for name, data in BRAWLER_STATS.items()
        if data[0] == rarity
    ]

    reward = random.choice(available)

    if reward not in st.session_state.inventory:
        st.session_state.inventory[reward] = {"level": 1, "duplicates": 0}
    else:
        if isinstance(st.session_state.inventory[reward], int):
            st.session_state.inventory[reward] = {"level": st.session_state.inventory[reward], "duplicates": 0}
            
        st.session_state.inventory[reward]["duplicates"] += 1
        
        current_lvl = st.session_state.inventory[reward]["level"]
        needed_cards = current_lvl * 2
        
        if st.session_state.inventory[reward]["duplicates"] >= needed_cards:
            st.session_state.inventory[reward]["duplicates"] -= needed_cards
            st.session_state.inventory[reward]["level"] += 1

    st.session_state.last_drop = {
        "name": reward,
        "rarity": rarity,
    }

    save_game()

# ---------------- CSS ----------------

st.markdown("""
<style>

.main{
    background:#0e1117;
}

h1,h2,h3{
    color:#ff8c00;
}

.stButton>button{
    background:#ff8c00;
    color:black;
    border-radius:12px;
    border:none;
    font-weight:bold;
}

.brawler-card{
    background:#1c1f26;
    padding:15px;
    border-radius:12px;
    text-align:center;
    margin-bottom:10px;
    border-top:4px solid #ff8c00;
}

.wiki-box {
    max-height: 250px;
    overflow-y: auto;
    background: #1c1f26;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #ff8c00;
    margin-top: 10px;
    margin-bottom: 10px;
    color: #e0e0e0;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("⚡ ULTRADO 3.0")
    st.write(f"👤 Přihlášen: **{st.session_state.username}**")
    
    if st.button("🚪 Odhlásit se"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.divider()

    st.subheader("📊 Cesta ke slávě")

    st.session_state.subs = st.number_input(
        "Odběratelů",
        value=st.session_state.subs,
        step=1
    )

    cil = st.number_input(
        "Cíl",
        value=100,
        step=1
    )

    if cil > 0:
        progress = min(
            st.session_state.subs / cil,
            1.0
        )

        st.progress(progress)

        if progress >= 1:
            st.success("Cíl splněn! 🏆")

    st.divider()

    with st.expander("✅ Úkoly"):

        st.checkbox("Vymyslet téma")
        st.checkbox("Natočit video")
        st.checkbox("Sestříhat video")
        st.checkbox("Vydat video")

    with st.expander("🌍 Překladač"):

        text = st.text_area("Česky")

        if st.button("Přeložit"):

            if IMPORT_ERR:
                st.error("Chybí knihovna deep-translator.")
            else:
                vysledek = GoogleTranslator(
                    source="cs",
                    target="en"
                ).translate(text)

                st.success(vysledek)

    st.divider()

    if st.button("🔄 Reset hry"):
        st.session_state.clear()
        js_reset = """
        <script>
            localStorage.removeItem('ultrado_user_save');
            window.location.href = window.location.pathname;
        </script>
        """
        components.html(js_reset, height=0, width=0)
        st.rerun()


# ==============================================================================
# HALLOWEENSKÝ BANNER S ODPOČTEM (NAHORU NAD ZÁLOŽKY)
# ==============================================================================
event_end_date = datetime(2026, 11, 8, 23, 59, 59)
now = datetime.now()

if now <= event_end_date:
    time_left = event_end_date - now
    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #ff6600, #9900cc);
            padding: 10px 15px;
            border-radius:12px;
    text-align:center;
    margin-bottom:10px;
    border-top:4px solid #ff8c00;
 }

.wiki-box {
    max-height: 250px;
    overflow-y: auto;
    background: #1c1f26;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #ff8c00;
    margin-top: 10px;
    margin-bottom: 10px;
    color: #e0e0e0;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("⚡ ULTRADO 3.0")
    st.write(f"👤 Přihlášen: **{st.session_state.username}**")
    
    if st.button("🚪 Odhlásit se"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.divider()

    st.subheader("📊 Cesta ke slávě")

    st.session_state.subs = st.number_input(
        "Odběratelů",
        value=st.session_state.subs,
        step=1
    )

    cil = st.number_input(
        "Cíl",
        value=100,
        step=1
    )

    if cil > 0:
        progress = min(
            st.session_state.subs / cil,
            1.0
        )

        st.progress(progress)

        if progress >= 1:
            st.success("Cíl splněn! 🏆")

    st.divider()

    with st.expander("✅ Úkoly"):

        st.checkbox("Vymyslet téma")
        st.checkbox("Natočit video")
        st.checkbox("Sestříhat video")
        st.checkbox("Vydat video")

    with st.expander("🌍 Překladač"):

        text = st.text_area("Česky")

        if st.button("Přeložit"):

            if IMPORT_ERR:
                st.error("Chybí knihovna deep-translator.")
            else:
                vysledek = GoogleTranslator(
                    source="cs",
                    target="en"
                ).translate(text)

                st.success(vysledek)

    st.divider()

    if st.button("🔄 Reset hry"):
        st.session_state.clear()
        js_reset = """
        <script>
            localStorage.removeItem('ultrado_user_save');
            window.location.href = window.location.pathname;
        </script>
        """
        components.html(js_reset, height=0, width=0)
        st.rerun()


# ==============================================================================
# HALLOWEENSKÝ BANNER S ODPOČTEM (NAHORU NAD ZÁLOŽKY)
# ==============================================================================
event_end_date = datetime(2026, 11, 8, 23, 59, 59)
now = datetime.now()

if now <= event_end_date:
    time_left = event_end_date - now
    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #ff6600, #9900cc);
            padding: 10px 15px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
            margin-bottom: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        ">
            🎃 HALLOWEENSKÝ EVENT BĚŽÍ! | Zbývá: {days} dní, {hours} hod a {minutes} min (končí 8. 11.) 🎃
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- TABS ----------------

tab_game, tab_studio, tab_ai = st.tabs([
    "🎮 TYCOON",
    "🎬 PRODUKČNÍ PANEL",
    "💬 AI CHAT"
])
with tab_game:

    coins_h, gems_h = get_income()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🪙 Mince",
        int(st.session_state.coins),
        f"+{coins_h}/h"
    )

    c2.metric(
        "💎 Gemy",
        int(st.session_state.gems),
        f"+{gems_h}/h"
    )

    c3.metric(
        "👥 Odběratelé",
        st.session_state.subs
    )

    st.divider()

    st.subheader("🎡 Daily odměna")

    elapsed = time.time() - st.session_state.last_wheel

    if elapsed >= 86400:

        if st.button("Vytočit zdarma"):

            reward = random.randint(100, 500)

            st.session_state.coins += reward

            st.session_state.last_wheel = time.time()

            save_game()

            st.success(f"Získal jsi {reward} mincí!")

            st.rerun()

    else:

        st.info(
            "Daily odměna zatím není dostupná."
        )

    st.divider()

    # ==========================================================================
    # 🛒 DENNÍ OBCHOD & HALLOWEENSKÁ NABÍDKA
    # ==========================================================================
    today_str = datetime.now().strftime("%Y-%m-%d")

    with st.expander("🛒 **DENNÍ OBCHOD & HALLOWEENSKÁ NABÍDKA**", expanded=False):
        
        # --- 🎁 1. DENNÍ DÁREK ZDARMA ---
        st.subheader("🎁 Denní dárek zdarma")
        last_claim = st.session_state.get("last_daily_claim", "")

        if last_claim == today_str:
            st.info("✅ Dnešní dárek zdarma už máš vyzvednutý! Přijď zase zítra.")
        else:
            if st.button("🎁 Vyzvednout dnešní odměnu zdarma", type="primary", use_container_width=True):
                reward_type = random.choices(["coins", "gems"], weights=[80, 20])[0]
                
                if reward_type == "coins":
                    amount = int(random.triangular(25, 200, 40))
                    st.session_state.coins += amount
                    st.success(f"🎉 Získal jsi zdarma **{amount} mincí** 🪙!")
                else:
                    amount = int(random.triangular(1, 30, 3))
                    st.session_state.gems += amount
                    st.success(f"💎 Vzácný drop! Získal jsi **{amount} gemů** 💎!")
                
                st.session_state.last_daily_claim = today_str
                save_game()
                st.rerun()

        st.divider()

        # --- 🎃 2. DENNÍ ROTACE POSTAV ---
        if datetime.now() <= event_end_date:
            st.subheader("🎃 Dnešní exkluzivní nabídka (24h)")
            st.caption("Postavy se mění každý den o půlnoci. Zakoupené postavy se z nabídky vyřadí!")

            available_chars = [c for c in HALLOWEEN_CHARACTERS if c["id"] not in st.session_state.owned_characters]

            if not available_chars:
                st.balloons()
                st.success("🏆 Úžasné! Vlastníš už všechny Halloweenské postavy!")
            else:
                random.seed(today_str)
                daily_count = min(2, len(available_chars))
                daily_offers = random.sample(available_chars, daily_count)
                random.seed()

                col1, col2 = st.columns(2)
                cols = [col1, col2]

                for i, char in enumerate(daily_offers):
                    with cols[i]:
                        st.markdown(f"### {char['name']}")
                        st.caption(f"Vzácnost: **{char['rarity']}**")
                        st.write(f"*{char['desc']}*")
                        
                        yield_str = f"🪙 **+{char['cph']}** / hod"
                        if char['gph'] > 0:
                            yield_str += f" | 💎 **+{char['gph']}** / hod"
                        st.markdown(f"📈 **Příjem:** {yield_str}")
                        
                        price_icon = "🪙" if char["type"] == "coins" else "💎"
                        price_text = f"{char['price']} {price_icon}"

                        if st.button(f"Koupit za {price_text}", key=f"buy_{char['id']}", use_container_width=True):
                            has_currency = (st.session_state.coins >= char['price']) if char['type'] == "coins" else (st.session_state.gems >= char['price'])
                            
                            if has_currency:
                                if char['type'] == "coins":
                                    st.session_state.coins -= char['price']
                                else:
                                    st.session_state.gems -= char['price']
                                
                                st.session_state.owned_characters.append(char['id'])
                                st.session_state.gems_per_hour = float(st.session_state.gems_per_hour) + char['gph']
                                save_game()

                                st.success(f"🎉 Úspěšně jsi zakoupil {char['name']}!")
                                st.rerun()
                            else:
                                st.error("Nemáš dostatek financí na tuto postavu!")
        else:
            st.warning("🎃 Halloweenský event již skončil. Těš se na další sezónní akci!")

    st.divider()

    # ---------------- SHOP ----------------

    st.subheader("🛒 Shop")

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("📦 Brawl Box\n100 🪙", use_container_width=True):
            if st.session_state.coins >= 100:
                st.session_state.coins -= 100
                open_box("Brawl Box")
                st.rerun()
            else:
                st.error("Nemáš dost mincí.")

    with b2:
        if st.button("📦 Big Box\n500 🪙", use_container_width=True):
            if st.session_state.coins >= 500:
                st.session_state.coins -= 500
                open_box("Big Box")
                st.rerun()
            else:
                st.error("Nemáš dost mincí.")

    with b3:
        if st.button("📦 Mega Box\n50 💎", use_container_width=True):
            if st.session_state.gems >= 50:
                st.session_state.gems -= 50
                open_box("Mega Box")
                st.rerun()
            else:
                st.error("Nemáš dost gemů.")

    st.divider()

    # ---------------- SKLAD ----------------

    st.subheader("⛏️ Sklad")

    seconds = min(
        time.time() - st.session_state.last_claim,
        43200
    )

    mined_coins = (coins_h / 3600) * seconds
    mined_gems = (gems_h / 3600) * seconds

    st.write(f"Vytěženo: {round(mined_coins,1)} 🪙 | {round(mined_gems,1)} 💎")

    if st.button("💰 Vyzvednout"):

        st.session_state.coins += mined_coins
        st.session_state.gems += mined_gems

        st.session_state.last_claim = time.time()

        save_game()

        st.success("Odměna vyzvednuta!")

        st.rerun()

    st.divider()

    # ---------------- INVENTÁŘ ----------------

    st.subheader("🎒 Tvůj tým")

    if st.session_state.inventory or st.session_state.owned_characters:

        cols = st.columns(5)
        col_idx = 0

        colors = {
            "Common": "#ffffff",
            "Rare": "#00ff66",
            "Epic": "#ff00ff",
            "Mythic": "#ff0000",
            "Legendary": "#ffff00",
            "Zakladatel": "#ff5500",
            "🟢 Common": "#00ff66",
            "🔵 Rare": "#0088ff",
            "🟣 Epic": "#aa00ff",
            "🟡 Legendary": "#ffff00",
            "🎃 Event": "#ff6600"
        }

        # 1. Halloweenské postavy
        for char_id in st.session_state.owned_characters:
            if char_id in HW_CHAR_MAP:
                char = HW_CHAR_MAP[char_id]
                rarity = char["rarity"]
                
                with cols[col_idx % 5]:
                    st.markdown(
                        f"""
                        <div class="brawler-card" style="border-top-color:{colors.get(rarity, '#ff6600')}">
                            <b style="color:{colors.get(rarity, '#ff6600')}">{char['name']}</b><br>
                            <small>{rarity}</small><br>
                            <span style="color:#ff8c00; font-weight:bold;">🎃 HALLOWEEN</span><br>
                            <small>🪙 +{char['cph']}/h | 💎 +{char['gph']}/h</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                col_idx += 1

        # 2. Standardní Brawleři
        inventory = sorted(
            st.session_state.inventory.items(),
            key=lambda x: RARITY_ORDER.get(
                BRAWLER_STATS[x[0]][0], 99
            )
        )

        for name, item_data in inventory:
            rarity = BRAWLER_STATS[name][0]

            if isinstance(item_data, dict):
                lvl = item_data.get("level", 1)
                dups = item_data.get("duplicates", 0)
            else:
                lvl = item_data
                dups = 0

            needed = lvl * 2

            with cols[col_idx % 5]:

                st.markdown(
                    f"""
                    <div class="brawler-card"
                    style="border-top-color:{colors.get(rarity, '#ffffff')}">
                        <b style="color:{colors.get(rarity, '#ffffff')}">
                        {name}
                        </b><br>
                        <small>{rarity}</small><br>
                        <span style="color:#ff8c00; font-weight:bold;">Lv. {lvl}</span><br>
                        <small>Karty: {dups}/{needed}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            col_idx += 1

    else:

        st.info("Zatím nemáš žádné postavy.")

with tab_studio:

    st.title("🎬 HLAVNÍ PANEL ULTRADO")

    tema = st.text_input(
        "💡 Co dnes tvoříme?",
        placeholder="Například: Brawl Stars, Minecraft..."
    )

    col1, col2 = st.columns(2)

    # ---------------- PRODUKCE ----------------

    with col1:

        st.subheader("🎥 Produkce")

        if st.button("✂️ YouCut Tipy"):

            st.info(
                "Používej Keyframes, Zoom, Motion Blur a Auto Captions."
            )

        if st.button("📺 Návrhy názvů"):

            if tema:

                navrhy = [
                    f"Šokující {tema}!",
                    f"Nejlepší {tema} roku 2026!",
                    f"Tohle o {tema} nevíš!",
                    f"{tema} ale jinak!",
                    f"TOP TIPY pro {tema}"
                ]

                st.success(random.choice(navrhy))

        if st.button("🔥 Hook"):

            if tema:

                hooky = [
                    f"Vsadím se, že tohle o {tema} nevíš.",
                    f"Počkej do konce videa...",
                    f"Tohle změnilo úplně všechno.",
                    f"Nečekal jsem, že se stane právě tohle."
                ]

                st.warning(random.choice(hooky))

    # ---------------- REŠERŠE ----------------

    with col2:

        st.subheader("📚 Rešerše")

        if st.button("📖 Wikipedie"):

            if IMPORT_ERR:

                st.error("Knihovna wikipedia-api není nainstalována.")

            elif tema:

                try:

                    wiki = wikipediaapi.Wikipedia(
                        language="cs",
                        user_agent="Ultrado"
                    )

                    page = wiki.page(tema)

                    if page.exists():
                        wiki_text = page.summary[:1200]
                        st.markdown(
                            f'<div class="wiki-box">{wiki_text}...</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("Stránka nebyla nalezena.")

                except Exception:

                    st.error("Nepodařilo se načíst Wikipedii.")

        if st.button("🏷️ Hashtagy"):

            if tema:

                st.code(
                    f"#{tema.replace(' ','')} "
                    "#viral #shorts #youtube"
                )

    st.divider()

    if st.button("📝 Generovat plán videa"):

        if tema:

            st.success("Plán byl vytvořen.")

            st.markdown(f"""
### 📋 Video: {tema}

1. Hook (0–5 s)

2. Představení tématu

3. Hlavní část

4. Nejlepší moment

5. Výzva k odběru
""")
    st.divider()

    # ---------------- KALKULAČKA ----------------

    with st.expander("🔢 Rychlá kalkulačka"):

        n1 = st.number_input(
            "Číslo 1",
            value=0.0,
            key="calc1"
        )

        n2 = st.number_input(
            "Číslo 2",
            value=0.0,
            key="calc2"
        )

        op = st.selectbox(
            "Operace",
            ["+", "-", "*", "/"],
            key="calc_op"
        )

        if st.button("Spočítat"):
            if op == "+":
                res = n1 + n2
            elif op == "-":
                res = n1 - n2
            elif op == "*":
                res = n1 * n2
            elif op == "/":
                res = n1 / n2 if n2 != 0 else "Nelze dělit nulou!"
            st.write(f"**Výsledek:** {res}")


# ---------------- AI CHAT ----------------

with tab_ai:
    st.title("💬 AI Asistent Ultrado")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_query = st.chat_input("Zeptej se AI asistenta...")

    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            if not GROQ_AVAILABLE:
                st.error("Knihovna Groq není nainstalována.")
            else:
                groq_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
                if not groq_key:
                    st.error("Chybí GROQ_API_KEY v st.secrets!")
                else:
                    client = Groq(api_key=groq_key)
                    
                    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages]
                    candidate_models = [
                        "openai/gpt-oss-20b",
                        "openai/gpt-oss-120b",
                        "qwen/qwen3.8-27b",
                        "minimaxai/minimax-m2.7"
                    ]
                    
                    ai_reply = None
                    last_error = ""
                    
                    for model_name in candidate_models:
                        try:
                            response = client.chat.completions.create(
                                model=model_name,
                                messages=messages,
                                temperature=0.7,
                                max_tokens=1000,
                            )
                            ai_reply = response.choices[0].message.content
                            if ai_reply:
                                break
                        except Exception as ex:
                            last_error = str(ex)
                            continue

                    if ai_reply:
                        st.write(ai_reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
                    else:
                        st.error(f"Groq API chyba: {last_error}")


# ---------------- ADMIN ----------------

with st.sidebar:

    st.divider()

    st.subheader("🔐 Admin")

    password = st.text_input(
        "Heslo",
        type="password"
    )

    if password == "admin530":

        st.success("Admin režim aktivní")

        if st.button("💰 Přidat mince"):

            st.session_state.coins += 100000

            save_game()

            st.rerun()

        if st.button("💎 Přidat gemy"):

            st.session_state.gems += 1000

            save_game()

            st.rerun()

        if st.button("🎁 Odemknout všechny postavy"):

            for name in BRAWLER_STATS.keys():
                st.session_state.inventory[name] = {"level": 1, "duplicates": 0}

            save_game()

            st.success("Všechny postavy odemčeny.")

        if st.button("🎃 Odemknout všechny Halloweenské postavy"):
            st.session_state.owned_characters = [c["id"] for c in HALLOWEEN_CHARACTERS]
            save_game()
            st.success("Všechny Halloweenské postavy odemčeny.")

        if st.button("♻️ Vymazat uloženou hru"):

            st.session_state.clear()
            js_reset = """
            <script>
                localStorage.removeItem('ultrado_user_save');
                window.location.href = window.location.pathname;
            </script>
            """
            components.html(js_reset, height=0, width=0)

            st.rerun()

save_game()
                                    
