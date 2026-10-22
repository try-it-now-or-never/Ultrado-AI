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

# ---------------- GLOBÁLNÍ ČASOVÉ PROMĚNNÉ ----------------
event_end_date = datetime(2026, 11, 8, 23, 59, 59)
now = datetime.now()

# ---------------- DATABÁZE 25 HALLOWEENSKÝCH POSTAV (VYVÁŽENÉ) ----------------

HALLOWEEN_CHARACTERS = [
    # Common (🟢)
    {"id": "h1", "name": "Zombie Střihač", "rarity": "🟢 Common", "type": "coins", "price": 150, "cph": 6, "gph": 0, "desc": "Nespí, nejí, jen stříhá... i když mu odpadávají prsty."},
    {"id": "h2", "name": "Kameraman Kostlivec", "rarity": "🟢 Common", "type": "coins", "price": 300, "cph": 12, "gph": 0, "desc": "Jeho záběry jsou celkem chrastivé, ale drží kameru pevně."},
    {"id": "h3", "name": "Pavučinový Zvukař", "rarity": "🟢 Common", "type": "coins", "price": 500, "cph": 20, "gph": 0, "desc": "Mikrofon má obmotaný pavučinami pro extra temný efekt."},
    {"id": "h4", "name": "Thumbnail Mumie", "rarity": "🟢 Common", "type": "coins", "price": 700, "cph": 30, "gph": 0, "desc": "Kreslí náhledovky z obvazů. Vypadají překvapivě dobře."},
    {"id": "h5", "name": "Netopýří Scenárista", "rarity": "🟢 Common", "type": "coins", "price": 900, "cph": 40, "gph": 0, "desc": "Píše příběhy pouze za úplňku a při svíčkách."},
    
    # Rare (🔵)
    {"id": "h6", "name": "Frankensteinův Střihač", "rarity": "🔵 Rare", "type": "coins", "price": 1500, "cph": 60, "gph": 0, "desc": "Sešívá jednotlivé klipy dohromady bleskovou rychlostí."},
    {"id": "h7", "name": "Duch Animátor 👻", "rarity": "🔵 Rare", "type": "coins", "price": 2200, "cph": 85, "gph": 0, "desc": "Animuje bez doteku klávesnice. Klávesy se mačkají samy!"},
    {"id": "h8", "name": "Vampire Dron 🦇", "rarity": "🔵 Rare", "type": "coins", "price": 3000, "cph": 110, "gph": 0, "desc": "Létá nad studiem a natáčí záběry, ze kterých mrazí v zádech."},
    {"id": "h9", "name": "Čarodějnice Social Media", "rarity": "🔵 Rare", "type": "coins", "price": 4000, "cph": 140, "gph": 0, "desc": "Míchá v kotli tajemné lektvary pro virální dosah."},
    {"id": "h10", "name": "Kat Režisér", "rarity": "🔵 Rare", "type": "coins", "price": 5500, "cph": 180, "gph": 0, "desc": "Když se záběr nepovede, nekompromisně ho okamžitě utne."},
    
    # Epic (🟣)
    {"id": "h11", "name": "Streamer Vlkodlak", "rarity": "🟣 Epic", "type": "coins", "price": 9000, "cph": 250, "gph": 0, "desc": "Při nočních streamech pořádně vyje na své diváky."},
    {"id": "h12", "name": "VFX Demon", "rarity": "🟣 Epic", "type": "coins", "price": 13000, "cph": 320, "gph": 0, "desc": "Jeho efekty jsou doslova pekelně dobré."},
    {"id": "h13", "name": "Krvavý Producer", "rarity": "🟣 Epic", "type": "coins", "price": 19000, "cph": 400, "gph": 0, "desc": "Investuje do videí s chladnou hlavou a elegancí."},
    {"id": "h14", "name": "Clickbait Smrťák", "rarity": "🟣 Epic", "type": "coins", "price": 27000, "cph": 500, "gph": 0, "desc": "Na jeho vykřičníky v náhledovkách klikne úplně každý."},
    {"id": "h15", "name": "Hrobník Manažer", "rarity": "🟣 Epic", "type": "coins", "price": 38000, "cph": 650, "gph": 0, "desc": "Dokáže pohřbít jakoukoliv konkurenci."},
    
    # Legendary (🟡)
    {"id": "h16", "name": "AI Dýňový Bot", "rarity": "🟡 Legendary", "type": "gems", "price": 20, "cph": 800, "gph": 0.1, "desc": "Generuje strašidelně dobrý obsah 24/7."},
    {"id": "h17", "name": "Viral Duch", "rarity": "🟡 Legendary", "type": "gems", "price": 30, "cph": 1000, "gph": 0.2, "desc": "Prochází algoritmy jako zdí a přináší lavinu sledovanosti."},
    {"id": "h18", "name": "Algoritmus z Pekla", "rarity": "🟡 Legendary", "type": "gems", "price": 50, "cph": 1300, "gph": 0.3, "desc": "Tento kód drží tvoje videa na hlavní stránce YouTube."},
    {"id": "h19", "name": "Hrad Drákuly Studio", "rarity": "🟡 Legendary", "type": "gems", "price": 75, "cph": 1600, "gph": 0.5, "desc": "Nejluxusnější temné studio s neomezeným rozpočtem."},
    
    # Event Exclusive (🎃)
    {"id": "h20", "name": "Bezhlavý Editor", "rarity": "🎃 Event", "type": "coins", "price": 2000, "cph": 75, "gph": 0, "desc": "Ztratil hlavu, ale na střih má pořád skvělý cit."},
    {"id": "h21", "name": "Zombie Kameraman", "rarity": "🎃 Event", "type": "coins", "price": 6500, "cph": 200, "gph": 0, "desc": "Udrží kameru stabilní i během apokalypsy."},
    {"id": "h22", "name": "Pumpkin King 🎃", "rarity": "🎃 Event", "type": "gems", "price": 25, "cph": 900, "gph": 0.1, "desc": "Vládce Halloweenu přináší královské zisky."},
    {"id": "h23", "name": "Zombie Scriptwriter", "rarity": "🎃 Event", "type": "gems", "price": 12, "cph": 500, "gph": 0, "desc": "Píše scénáře bez přestávky celou věčnost."},
    {"id": "h24", "name": "Duch Creator 👻🛠️", "rarity": "🎃 Event", "type": "gems", "price": 120, "cph": 2000, "gph": 0.8, "desc": "Legenda tvorby obsahu, která tvoří i ze záhrobí."},
    {"id": "h25", "name": "Zlatá Halloweenská Trofej 🏆", "rarity": "🎃 Event", "type": "gems", "price": 90, "cph": 1700, "gph": 0.6, "desc": "Exkluzivní trofej garantující trvalý přísun statistik."}
]

HW_CHAR_MAP = {c["id"]: c for c in HALLOWEEN_CHARACTERS}

# ---------------- DATABÁZE VÁNOČNÍCH POSTAV ----------------

CHRISTMAS_CHARACTERS = [
    {"id": "x1", "name": "Zmrzlý rampouch", "rarity": "🟢 Common", "cph": 35, "gph": 0, "desc": "Chladný střihač s rychlými reflexy."},
    {"id": "x2", "name": "Vánoční strom", "rarity": "🟣 Epic", "cph": 250, "gph": 0, "desc": "Září sváteční atmosférou a mincemi."},
    {"id": "x3", "name": "Sněhová bouře", "rarity": "🔴 Mythic", "cph": 750, "gph": 1.0, "desc": "Přináší opravdovou lavinu zisků."},
    {"id": "x4", "name": "Ultrado dárek (Zlatý)", "rarity": "🟡 Legendary", "cph": 850, "gph": 3.0, "desc": "Zlaté překvapení pro skvělé tvůrce."},
    {"id": "x5", "name": "Vánoční Překvapení", "rarity": "🔮 Secret", "cph": 1000, "gph": 5.0, "desc": "Tajemná legenda vzešlá z Mystery Packu!"}
]

XMAS_CHAR_MAP = {c["id"]: c for c in CHRISTMAS_CHARACTERS}

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

if "snowflakes" not in st.session_state:
    st.session_state.snowflakes = 0

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

# Vánoční proměnné v session state
if "last_xmas_claim" not in st.session_state:
    st.session_state.last_xmas_claim = ""

if "owned_xmas_characters" not in st.session_state:
    st.session_state.owned_xmas_characters = []

if "xmas_xp" not in st.session_state:
    st.session_state.xmas_xp = 0

if "has_premium_pass" not in st.session_state:
    st.session_state.has_premium_pass = False

if "last_gift_time" not in st.session_state:
    st.session_state.last_gift_time = 0

if "christmas_admin_debug" not in st.session_state:
    st.session_state.christmas_admin_debug = False

if "simulated_phase" not in st.session_state:
    st.session_state.simulated_phase = "Real time"


def save_game():
    """Uloží data do Supabase (pokud je hráč přihlášen) i do localStorage."""
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "snowflakes": st.session_state.snowflakes,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel,
        "subs": st.session_state.subs,
        "last_daily_claim": st.session_state.last_daily_claim,
        "last_xmas_claim": st.session_state.last_xmas_claim,
        "owned_characters": st.session_state.owned_characters,
        "owned_xmas_characters": st.session_state.owned_xmas_characters,
        "gems_per_hour": st.session_state.gems_per_hour,
        "xmas_xp": st.session_state.xmas_xp,
        "has_premium_pass": st.session_state.has_premium_pass
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
    js_code = """
    <script>
        localStorage.setItem('ultrado_user_save', '""" + json_str + """');
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
                    st.session_state.snowflakes = user_data.get("snowflakes", 0)
                    st.session_state.inventory = user_data.get("inventory", {})
                    st.session_state.last_claim = user_data.get("last_claim", time.time())
                    st.session_state.last_wheel = user_data.get("last_wheel", 0)
                    st.session_state.subs = user_data.get("subs", 0)
                    st.session_state.last_daily_claim = user_data.get("last_daily_claim", res.data[0].get("last_daily_claim", ""))
                    st.session_state.last_xmas_claim = user_data.get("last_xmas_claim", "")
                    st.session_state.owned_characters = user_data.get("owned_characters", res.data[0].get("owned_characters", []))
                    st.session_state.owned_xmas_characters = user_data.get("owned_xmas_characters", [])
                    st.session_state.gems_per_hour = user_data.get("gems_per_hour", res.data[0].get("gems_per_hour", 0.0))
                    st.session_state.xmas_xp = user_data.get("xmas_xp", 0)
                    st.session_state.has_premium_pass = user_data.get("has_premium_pass", False)
                    
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
                        "snowflakes": 0,
                        "inventory": {},
                        "last_claim": time.time(),
                        "last_wheel": 0,
                        "subs": 0,
                        "last_daily_claim": "",
                        "last_xmas_claim": "",
                        "owned_characters": [],
                        "owned_xmas_characters": [],
                        "gems_per_hour": 0.0,
                        "xmas_xp": 0,
                        "has_premium_pass": False
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

def get_current_time():
    if st.session_state.christmas_admin_debug:
        if st.session_state.simulated_phase == "Pre-Event (14. - 17. 12.)":
            return datetime(2026, 12, 15, 12, 0)
        elif st.session_state.simulated_phase == "Full Event & Pass (18. 12. - 3. 1.)":
            return datetime(2026, 12, 20, 12, 0)
        elif st.session_state.simulated_phase == "Po Eventu (Po 3. 1.)":
            return datetime(2027, 1, 5, 12, 0)
    return datetime.now()

now_time = get_current_time()

# Časové milníky Vánočního Eventu
XMAS_EVENT_START = datetime(2026, 12, 14)
XMAS_PASS_START = datetime(2026, 12, 18)
XMAS_EVENT_END = datetime(2027, 1, 3, 23, 59, 59)

is_xmas_event_active = XMAS_EVENT_START <= now_time <= XMAS_EVENT_END
is_xmas_pass_active = now_time >= XMAS_PASS_START and is_xmas_event_active


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

    # Přičtení příjmu z vánočních postav
    for char_id in st.session_state.owned_xmas_characters:
        if char_id in XMAS_CHAR_MAP:
            coins_h += XMAS_CHAR_MAP[char_id]["cph"]
            gems_h += XMAS_CHAR_MAP[char_id]["gph"]

    return round(coins_h, 1), round(gems_h, 1)


def open_box(box_type):

    if box_type == "Malý box":
        chances = {
            "Common": 80,
            "Rare": 18,
            "Epic": 2,
            "Mythic": 0,
            "Legendary": 0,
        }

    elif box_type == "Velký box":
        chances = {
            "Common": 45,
            "Rare": 35,
            "Epic": 14,
            "Mythic": 5,
            "Legendary": 1,
        }

    else:  # Ultrado box
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


def open_xmas_box(box_type):
    """Otevírání vánočních krabiček za vločky."""
    if box_type == "Sněhová krabička":
        if "x1" not in st.session_state.owned_xmas_characters:
            st.session_state.owned_xmas_characters.append("x1")
            st.success("Získal jsi vánoční postavu: Zmrzlý rampouch!")
        else:
            st.session_state.coins += 5000
            st.success("Získal jsi 5 000 🪙!")
            
    elif box_type == "Mystery Pack":
        if random.random() <= 0.003 and "x5" not in st.session_state.owned_xmas_characters:
            st.session_state.owned_xmas_characters.append("x5")
            st.balloons()
            st.success("🎉 Neskutečné štěstí! Získal jsi Secret Legendary: Vánoční Překvapení!")
        else:
            rew = random.choice(["coins", "gems", "snowflakes"])
            if rew == "coins":
                st.session_state.coins += 15000
                st.success("Získal jsi 15 000 🪙!")
            elif rew == "gems":
                st.session_state.gems += 50
                st.success("Získal jsi 50 💎!")
            else:
                st.session_state.snowflakes += 100
                st.success("Získal jsi 100 ❄️!")

    elif box_type == "Vánoční Ultrado Box":
        if "x2" not in st.session_state.owned_xmas_characters:
            st.session_state.owned_xmas_characters.append("x2")
            st.success("Získal jsi vánoční postavu: Vánoční strom!")
        else:
            st.session_state.gems += 150
            st.success("Získal jsi 150 💎!")
            
    save_game()

# ---------------- CSS ----------------

st.markdown("""
<style>
.main {
    background: #0e1117;
}
h1, h2, h3 {
    color: #ff8c00;
}
.stButton>button {
    background: #ff8c00;
    color: black;
    border-radius: 12px;
    border: none;
    font-weight: bold;
}
.brawler-card {
    background: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 10px;
    border-top: 4px solid #ff8c00;
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


# ---------------- CSS SNÍH NA POZADÍ (BĚHEM EVENTU) ----------------

if is_xmas_event_active:
    st.markdown(
        """
        <style>
        .snowflake {
          color: #fff;
          font-size: 1.2em;
          font-family: Arial;
          text-shadow: 0 0 2px #000;
        }
        @keyframes snowflakes-fall { 0% { top: -10%; } 100% { top: 100%; } }
        @keyframes snowflakes-shake { 0% { transform: translateX(0px); } 50% { transform: translateX(80px); } 100% { transform: translateX(0px); } }
        
        .snowflake {
          position: fixed;
          top: -10%;
          z-index: 0;
          user-select: none;
          cursor: default;
          animation-name: snowflakes-fall, snowflakes-shake;
          animation-duration: 10s, 3s;
          animation-timing-function: linear, ease-in-out;
          animation-iteration-count: infinite, infinite;
          animation-play-state: running, running;
        }
        .snowflake:nth-of-type(0){left:1%;animation-delay:0s,0s}
        .snowflake:nth-of-type(1){left:10%;animation-delay:1s,1s}
        .snowflake:nth-of-type(2){left:20%;animation-delay:6s,.5s}
        .snowflake:nth-of-type(3){left:30%;animation-delay:4s,2s}
        .snowflake:nth-of-type(4){left:40%;animation-delay:2s,2s}
        .snowflake:nth-of-type(5){left:50%;animation-delay:8s,3s}
        .snowflake:nth-of-type(6){left:60%;animation-delay:6s,2s}
        .snowflake:nth-of-type(7){left:70%;animation-delay:2.5s,1s}
        .snowflake:nth-of-type(8){left:80%;animation-delay:1s,0s}
        .snowflake:nth-of-type(9){left:90%;animation-delay:3s,1.5s}
        </style>
        
        <div class="snowflakes" aria-hidden="true">
          <div class="snowflake">❄</div><div class="snowflake">❅</div>
          <div class="snowflake">❆</div><div class="snowflake">❄</div>
          <div class="snowflake">❅</div><div class="snowflake">❆</div>
          <div class="snowflake">❄</div><div class="snowflake">❅</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("⚡ ULTRADO 3.0")
    st.write(f"👤 Přihlášen: **{st.session_state.username}**")
    
    if is_xmas_event_active:
        st.info(f"❄️ Sněhové vločky: **{st.session_state.snowflakes}**")
    
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
                
    with st.expander("⚖️ Podmínky & Ochrana soukromí"):
        st.markdown("""
        **Zásady ochrany soukromí a pravidla hry**
        
        * **Osobní údaje:** Hra ukládá pouze zvolenou přezdívku a herní postup. Nepožadujeme e-mail ani reálné jméno.
        * **Bez mikrotransakcí:** Všechny měny (mince, gemy) jsou pouze virtuální a nelze je nakupovat ani směňovat za reálné peníze.
        * **Pravidla obchodování (Trading):** Výměna herních předmětů nebo postav za reálné peníze mimo hru je přísně zakázána.
        * **Ukládání dat:** Data jsou bezpečně uložena v databázi pro zachování tvého herního postupu.
        * **Férová hra:** Používáním aplikace souhlasíš s dodržováním pravidel a férovým hraním bez zneužívání chyb.
        """)
        

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

tab_game, tab_studio, tab_ai, tab_market = st.tabs([
    "🎮 TYCOON",
    "🎬 PRODUKČNÍ PANEL",
    "💬 AI CHAT",
    "🤝 TRŽIŠTĚ"
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
    # 🎁 RANDOM EVENT: PADAJÍCÍ VÁNOČNÍ DÁREK (KAŽDÝCH 15 MINUT)
    # ==========================================================================
    if is_xmas_event_active:
        current_ts = time.time()
        if current_ts - st.session_state.last_gift_time >= 900:  # 15 minut
            if "gift_spawn_time" not in st.session_state:
                st.session_state.gift_spawn_time = current_ts

            time_left_gift = 5 - int(current_ts - st.session_state.gift_spawn_time)
            if time_left_gift > 0:
                st.warning(f"🎁 PADAJÍCÍ VÁNOČNÍ DÁREK! Zmizí za {time_left_gift} s!")
                if st.button("🎁 CHYTIT DÁREK (+15 ❄️)", key="catch_gift_btn"):
                    st.session_state.snowflakes += 15
                    st.session_state.last_gift_time = current_ts
                    del st.session_state.gift_spawn_time
                    st.balloons()
                    st.success("Chytil jsi dárek a získal 15 ❄️!")
                    save_game()
                    st.rerun()
            else:
                st.session_state.last_gift_time = current_ts
                del st.session_state.gift_spawn_time

    # ==========================================================================
    # 🎄 VÁNOČNÍ EVENT SEKCE (14. 12. 2026 – 3. 1. 2027)
    # ==========================================================================
    if is_xmas_event_active:
        st.subheader("🎄 VÁNOČNÍ EVENT")

        # 🛒 DENNÍ OBCHOD & VÁNOČNÍ NABÍDKA
        with st.expander("🛒 DENNÍ OBCHOD & VÁNOČNÍ NABÍDKA ❄️", expanded=False):
            st.subheader("🎁 Denní dárek zdarma")
            today_str_xmas = now_time.strftime("%Y-%m-%d")
            
            if st.session_state.last_xmas_claim == today_str_xmas:
                st.info("✅ Dnešní dárek zdarma už máš vyzvednutý! Přijď zase zítra.")
            else:
                if st.button("Vyzvednout 50 ❄️ Sněhových vloček zdarma", key="claim_daily_xmas", type="primary", use_container_width=True):
                    st.session_state.snowflakes += 50
                    st.session_state.last_xmas_claim = today_str_xmas
                    st.success("Získal jsi 50 ❄️!")
                    save_game()
                    st.rerun()

            st.divider()
            st.subheader("🎄 Exkluzivní vánoční nabídka")
            
            col_x1, col_x2, col_x3 = st.columns(3)
            with col_x1:
                st.markdown("### Vánoční strom")
                st.caption("Vzácnost: 🟣 Epic")
                st.write("Příjem: 🪙 +250/s")
                if "x2" not in st.session_state.owned_xmas_characters:
                    if st.button("Koupit za 750 ❄️", key="buy_x2", use_container_width=True):
                        if st.session_state.snowflakes >= 750:
                            st.session_state.snowflakes -= 750
                            st.session_state.owned_xmas_characters.append("x2")
                            st.success("Koupil jsi Vánoční strom!")
                            save_game()
                            st.rerun()
                        else:
                            st.error("Nemáš dostatek vloček!")
                else:
                    st.info("Vlastněno")

            with col_x2:
                st.markdown("### Sněhová bouře")
                st.caption("Vzácnost: 🔴 Mythic")
                st.write("Příjem: 🪙 +750/s | 💎 +1/h")
                if "x3" not in st.session_state.owned_xmas_characters:
                    if st.button("Koupit za 1 500 ❄️", key="buy_x3", use_container_width=True):
                        if st.session_state.snowflakes >= 1500:
                            st.session_state.snowflakes -= 1500
                            st.session_state.owned_xmas_characters.append("x3")
                            st.success("Koupil jsi Sněhovou bouři!")
                            save_game()
                            st.rerun()
                        else:
                            st.error("Nemáš dostatek vloček!")
                else:
                    st.info("Vlastněno")

            with col_x3:
                st.markdown("### Ultrado dárek (Zlatý)")
                st.caption("Vzácnost: 🟡 Legendary")
                st.write("Příjem: 🪙 +850/s | 💎 +3/h")
                if "x4" not in st.session_state.owned_xmas_characters:
                    if st.button("Koupit za 2 500 ❄️", key="buy_x4", use_container_width=True):
                        if st.session_state.snowflakes >= 2500:
                            st.session_state.snowflakes -= 2500
                            st.session_state.owned_xmas_characters.append("x4")
                            st.success("Koupil jsi Ultrado dárek (Zlatý)!")
                            save_game()
                            st.rerun()
                        else:
                            st.error("Nemáš dostatek vloček!")
                else:
                    st.info("Vlastněno")

        # 📦 VÁNOČNÍ BOXY
        with st.expander("📦 VÁNOČNÍ KRABIČKY A PACKY", expanded=False):
            c_b1, c_b2, c_b3 = st.columns(3)
            with c_b1:
                if st.button("❄️ Sněhová krabička\n80 ❄️", use_container_width=True):
                    if st.session_state.snowflakes >= 80:
                        st.session_state.snowflakes -= 80
                        open_xmas_box("Sněhová krabička")
                    else:
                        st.error("Chybí ti vločky!")
            with c_b2:
                if st.button("🎁 Mystery Pack\n250 ❄️", use_container_width=True):
                    if st.session_state.snowflakes >= 250:
                        st.session_state.snowflakes -= 250
                        open_xmas_box("Mystery Pack")
                    else:
                        st.error("Chybí ti vločky!")
            with c_b3:
                if st.button("🎄 Vánoční Ultrado Box\n350 ❄️", use_container_width=True):
                    if st.session_state.snowflakes >= 350:
                        st.session_state.snowflakes -= 350
                        open_xmas_box("Vánoční Ultrado Box")
                    else:
                        st.error("Chybí ti vločky!")

        # 📜 VÁNOČNÍ ÚKOLY
        with st.expander("📜 VÁNOČNÍ ÚKOLY (DAILY & EVENT)", expanded=False):
            st.write("#### ⏱️ Denní úkoly (+30 ❄️)")
            st.checkbox("Vánoční maraton (Hraj 20 minut)")
            st.checkbox("Sváteční nakupování (Otevři 1 box)")
            st.checkbox("Cesta za Passem (Získej 150 XP)")

        # 🎅 VÁNOČNÍ PASS
        with st.expander("🎅 VÁNOČNÍ PASS (20 TIERŮ + BONUS)", expanded=False):
            if is_xmas_pass_active:
                st.progress(min(st.session_state.xmas_xp / 10000, 1.0), text=f"Tvoje XP: {st.session_state.xmas_xp} XP")
                if not st.session_state.has_premium_pass:
                    if st.button("💎 Koupit Premium Pass za 25 000 🪙"):
                        if st.session_state.coins >= 25000:
                            st.session_state.coins -= 25000
                            st.session_state.has_premium_pass = True
                            st.success("Koupil jsi Premium Vánoční Pass!")
                            save_game()
                            st.rerun()
                        else:
                            st.error("Nemáš dostatek mincí!")
                else:
                    st.success("⭐ Premium Pass AKTIVNÍ!")
            else:
                st.info("🎅 Vánoční Pass startuje 18. prosince! Sbírej zatím vločky z dárků a úkolů.")

        st.divider()

    # =====# --- ZÁLOŽKA 2: TRŽIŠTĚ (NOVÁ MULTIPLAYER LOGIKA) --
with tab_market:
    st.title("🤝 Hráčské Tržiště")
    st.write("Nakupuj postavy a elixíry od ostatních hráčů nebo vystav vlastní přebytky!")

    # --- A. AUTOMATICKÁ VÝPLATA TRŽEB PRODEJCI ---
    if supabase and st.session_state.get("username"):
        try:
            sold_res = supabase.table("marketplace").select("*").eq("seller", st.session_state.username).eq("status", "sold").execute()
            sold_items = sold_res.data if sold_res.data else []

            if sold_items:
                total_coins_earned = 0
                total_gems_earned = 0

                for sold in sold_items:
                    if sold["currency"] == "coins":
                        total_coins_earned += sold["price"]
                    else:
                        total_gems_earned += sold["price"]

                    supabase.table("marketplace").update({"status": "claimed"}).eq("id", sold["id"]).execute()

                st.session_state.coins += total_coins_earned
                st.session_state.gems += total_gems_earned
                save_game()

                earned_msg = []
                if total_coins_earned > 0:
                    earned_msg.append(f"{total_coins_earned} 🪙")
                if total_gems_earned > 0:
                    earned_msg.append(f"{total_gems_earned} 💎")

                st.toast(f"🎉 Tvoje zboží bylo prodáno! Získal jsi: {', '.join(earned_msg)}", icon="💰")
        except Exception:
            pass

    if "hidden_trades" not in st.session_state:
        st.session_state.hidden_trades = []

    market_view_tab, market_create_tab = st.tabs(["🌐 Veřejný trh", "📦 Vystavit předmět"])

    # --- B. PROHLÍŽENÍ A NÁKUP (VEŘEJNÝ TRH) ---
    with market_view_tab:
        if supabase:
            try:
                res = supabase.table("marketplace").select("*").eq("status", "active").execute()
                offers = res.data if res.data else []

                active_offers = [
                    o for o in offers 
                    if o["seller"] != st.session_state.username and o["id"] not in st.session_state.hidden_trades
                ]

                if not active_offers:
                    st.info("Na trhu nejsou žádné aktivní nabídky od ostatních hráčů.")
                else:
                    for offer in active_offers:
                        col_info, col_btn1, col_btn2 = st.columns([3, 1, 1])
                        currency_icon = "🪙" if offer["currency"] == "coins" else "💎"

                        with col_info:
                            st.write(f"**Prodejce:** {offer['seller']} | **Předmět:** `{offer['item_name']}` | **Cena:** {offer['price']} {currency_icon}")

                        # 🟢 ZELENÁ FAJFKA (KOUPIT)
                        with col_btn1:
                            if st.button("✅ Koupit", key=f"buy_trade_{offer['id']}", use_container_width=True):
                                has_funds = (st.session_state.coins >= offer['price']) if offer['currency'] == "coins" else (st.session_state.gems >= offer['price'])

                                if not has_funds:
                                    st.error("Nemáš dostatek financí!")
                                else:
                                    # 1. Stržení financí kupujícímu
                                    if offer['currency'] == "coins":
                                        st.session_state.coins -= offer['price']
                                    else:
                                        st.session_state.gems -= offer['price']

                                    raw_name = offer['item_name']

                                    # 2. Připsání předmětu kupujícímu
                                    if raw_name.startswith("Standard: "):
                                        clean_name = raw_name.replace("Standard: ", "")
                                        if clean_name not in st.session_state.inventory:
                                            st.session_state.inventory[clean_name] = {"level": 1, "duplicates": 0}
                                        else:
                                            if isinstance(st.session_state.inventory[clean_name], int):
                                                st.session_state.inventory[clean_name] = {"level": st.session_state.inventory[clean_name], "duplicates": 0}
                                            st.session_state.inventory[clean_name]["duplicates"] += 1

                                    elif raw_name.startswith("Halloween: "):
                                        clean_name = raw_name.replace("Halloween: ", "")
                                        for h_id, h_data in HW_CHAR_MAP.items():
                                            if h_data["name"] == clean_name:
                                                if h_id not in st.session_state.owned_characters:
                                                    st.session_state.owned_characters.append(h_id)
                                                break

                                    elif raw_name.startswith("Vánoce: "):
                                        clean_name = raw_name.replace("Vánoce: ", "")
                                        for x_id, x_data in XMAS_CHAR_MAP.items():
                                            if x_data["name"] == clean_name:
                                                if x_id not in st.session_state.owned_xmas_characters:
                                                    st.session_state.owned_xmas_characters.append(x_id)
                                                break

                                    elif raw_name.startswith("Elixír: "):
                                        clean_name = raw_name.replace("Elixír: ", "")
                                        if "potions" not in st.session_state:
                                            st.session_state.potions = {}
                                        st.session_state.potions[clean_name] = st.session_state.potions.get(clean_name, 0) + 1

                                    # 3. Označení v Supabase jako prodané
                                    supabase.table("marketplace").update({"status": "sold"}).eq("id", offer["id"]).execute()

                                    save_game()
                                    st.success(f"Úspěšně jsi zakoupil {raw_name}!")
                                    st.rerun()

                        # 🔴 ČERVENÝ KŘÍŽEK (SKRÝT NABÍDKU)
                        with col_btn2:
                            if st.button("❌ Skrýt", key=f"hide_trade_{offer['id']}", use_container_width=True):
                                st.session_state.hidden_trades.append(offer['id'])
                                st.rerun()

            except Exception as e:
                st.error(f"Nepodařilo se načíst tržiště: {e}")
        else:
            st.warning("Tržiště vyžaduje aktivní připojení k Supabase databázi.")

    # --- C. VYSTAVENÍ PŘEDMĚTU NA TRH ---
    with market_create_tab:
        sellable_items = []

        # Standardní
        for name in st.session_state.inventory.keys():
            sellable_items.append(f"Standard: {name}")

        # Halloween
        for char_id in st.session_state.get("owned_characters", []):
            if char_id in HW_CHAR_MAP:
                sellable_items.append(f"Halloween: {HW_CHAR_MAP[char_id]['name']}")

        # Vánoce
        for char_id in st.session_state.get("owned_xmas_characters", []):
            if char_id in XMAS_CHAR_MAP:
                sellable_items.append(f"Vánoce: {XMAS_CHAR_MAP[char_id]['name']}")

        # Elixíry
        if "potions" in st.session_state:
            for p_name, p_count in st.session_state.potions.items():
                if p_count > 0:
                    sellable_items.append(f"Elixír: {p_name}")

        if not sellable_items:
            st.info("Nemáš v inventáři žádné postavy ani elixíry k prodeji.")
        else:
            selected_item = st.selectbox("Vyber předmět/postavu k prodeji", sellable_items)
            price_currency = st.selectbox("Měna", ["Mince (🪙)", "Gemy (💎)"])
            item_price = st.number_input("Cena", min_value=1, value=100, step=10)

            if st.button("🚀 Vystavit na trh", use_container_width=True):
                curr_code = "coins" if "Mince" in price_currency else "gems"

                # Odebrání prodávaného předmětu prodejci z inventáře
                if selected_item.startswith("Standard: "):
                    clean_name = selected_item.replace("Standard: ", "")
                    del st.session_state.inventory[clean_name]

                elif selected_item.startswith("Halloween: "):
                    clean_name = selected_item.replace("Halloween: ", "")
                    for h_id, h_data in HW_CHAR_MAP.items():
                        if h_data["name"] == clean_name:
                            st.session_state.owned_characters.remove(h_id)
                            break

                elif selected_item.startswith("Vánoce: "):
                    clean_name = selected_item.replace("Vánoce: ", "")
                    for x_id, x_data in XMAS_CHAR_MAP.items():
                        if x_data["name"] == clean_name:
                            st.session_state.owned_xmas_characters.remove(x_id)
                            break

                elif selected_item.startswith("Elixír: "):
                    clean_name = selected_item.replace("Elixír: ", "")
                    st.session_state.potions[clean_name] -= 1

                if supabase:
                    try:
                        supabase.table("marketplace").insert({
                            "seller": st.session_state.username,
                            "item_name": selected_item,
                            "price": int(item_price),
                            "currency": curr_code,
                            "status": "active"
                        }).execute()

                        save_game()
                        st.success(f"Předmět '{selected_item}' byl nabídnut na trhu!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Chyba při vystavování: {e}")
            

    
                
                        
                        
                        
        

    # ---------------- SHOP ----------------

    st.subheader("🛒 Obchod s boxy")

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("📦 Malý box\n100 🪙", use_container_width=True):
            if st.session_state.coins >= 100:
                st.session_state.coins -= 100
                open_box("Malý box")
                st.rerun()
            else:
                st.error("Nemáš dost mincí.")

    with b2:
        if st.button("📦 Velký box\n500 🪙", use_container_width=True):
            if st.session_state.coins >= 500:
                st.session_state.coins -= 500
                open_box("Velký box")
                st.rerun()
            else:
                st.error("Nemáš dost mincí.")

    with b3:
        if st.button("🎁 Ultrado box\n50 💎", use_container_width=True):
            if st.session_state.gems >= 50:
                st.session_state.gems -= 50
                open_box("Ultrado box")
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

    
         # ---------------- INVENTÁŘ (ROZDĚLENÝ NA ZÁLOŽKY) ----------------

        # ---------------- INVENTÁŘ (ROZDĚLENÝ NA ZÁLOŽKY) ----------------

    st.subheader("🎒 Inventář & Tým")

    inv_tab_chars, inv_tab_potions = st.tabs(["🦸 Postavy a Tým", "🧪 Elixíry a Předměty"])

    # --- ZÁLOŽKA 1: POSTAVY ---
    with inv_tab_chars:
        if st.session_state.inventory or st.session_state.owned_characters or st.session_state.owned_xmas_characters:

            cols = st.columns(5)
            col_idx = 0

            colors = {
                "Common": "#ffffff",
                "Rare": "#00ff66",
                "Epic": "#ff00ff",
                "Mythic": "#ff0000",
                "Legendary": "#ffff00",
                "Zakladatel": "#ff5500",
                "🟢 Common": "#4CAF50",
                "🔵 Rare": "#2196F3",
                "🟣 Epic": "#9C27B0",
                "🟡 Legendary": "#FFEB3B",
                "🔴 Mythic": "#F44336",
                "🔮 Secret": "#E91E63",
                "🎃 Event": "#ff6600"
            }

            # 1. Vánoční postavy
            for char_id in st.session_state.owned_xmas_characters:
                if char_id in XMAS_CHAR_MAP:
                    char = XMAS_CHAR_MAP[char_id]
                    rarity = char["rarity"]

                    with cols[col_idx % 5]:
                        st.markdown(
                            f"""
                            <div class="brawler-card" style="border-top-color:{colors.get(rarity.split()[-1], '#ff8c00')}; border: 2px solid {colors.get(rarity.split()[-1], '#ff8c00')};">
                                <b style="color:{colors.get(rarity.split()[-1], '#ff8c00')}">{char['name']}</b><br>
                                <small>{rarity}</small><br>
                                <span style="color:#ff8c00; font-weight:bold;">🎄 VÁNOCE</span><br>
                                <small>🪙 +{char['cph']}/h | 💎 +{char['gph']}/h</small>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    col_idx += 1

            # 2. Halloweenské postavy
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

            # 3. Standardní Brawleři
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
                        <div class="brawler-card" style="border-top-color:{colors.get(rarity, '#ffffff')}">
                            <b style="color:{colors.get(rarity, '#ffffff')}">{name}</b><br>
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

    # --- ZÁLOŽKA 2: ELIXÍRY A PŘEDMĚTY ---
    with inv_tab_potions:
        if "potions" not in st.session_state:
            st.session_state.potions = {}

        if not st.session_state.potions:
            st.info("Zatím nemáš žádné elixíry ani speciální předměty.")
        else:
            for p_name, p_count in st.session_state.potions.items():
                st.write(f"🧪 **{p_name}** — Počet: {p_count} ks")

            
                

        
    
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

        if st.button("❄️ Přidat 1 000 vloček"):
            st.session_state.snowflakes += 1000
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

        if st.button("🎄 Odemknout Vánoční postavy"):
            st.session_state.owned_xmas_characters = [c["id"] for c in CHRISTMAS_CHARACTERS]
            save_game()
            st.success("Všechny Vánoční postavy odemčeny.")

            st.divider()
        st.write("### 🎄 Testování Vánočního Eventu")
        st.session_state.christmas_admin_debug = st.checkbox("Aktivovat Debug Mode pro Vánoce", value=st.session_state.christmas_admin_debug)
        
        if st.session_state.christmas_admin_debug:
            st.session_state.simulated_phase = st.radio(
                "Simulovat fázi eventu:",
                ["Real time", "Pre-Event (14. - 17. 12.)", "Full Event & Pass (18. 12. - 3. 1.)", "Po Eventu (Po 3. 1.)"]
            )
            st.info(f"Aktuálně simulovaný čas: {now_time.strftime('%d. %m. %Y %H:%M')}")
            # TADY BYL ST.RERUN() - KDYŽ HO SMAŽEŠ, Bude to fungovat normálně!
        

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

    
