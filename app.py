import streamlit as st
import streamlit.components.v1 as components
import time
import random
import json
import os
import hashlib
from datetime import timedelta
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


def save_game():
    """Uloží data do Supabase (pokud je hráč přihlášen) i do localStorage."""
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel,
        "subs": st.session_state.subs,
    }
    
    # 1. Uložení do Supabase Cloud Databáze
    if st.session_state.logged_in and supabase:
        try:
            supabase.table("players").update({
                "save_data": data
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
                        "subs": 0
                    }
                    supabase.table("players").insert({
                        "username": r_user,
                        "password_hash": hashed,
                        "save_data": default_save
                    }).execute()
                    
                    st.success("Účet vytvořen! Nyní se můžeš přihlásit.")
            else:
                st.warning("Vyplň všechna pole.")

        # Upozornění pro hráče o uložení dat
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
    gems_h = 0

    for name, item_data in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            if isinstance(item_data, dict):
                level = item_data.get("level", 1)
            else:
                level = item_data

            multiplier = 1 + (level - 1) * 0.20
            
            coins_h += BRAWLER_STATS[name][1] * multiplier
            gems_h += BRAWLER_STATS[name][2] * multiplier

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

    if st.session_state.inventory:

        inventory = sorted(
            st.session_state.inventory.items(),
            key=lambda x: RARITY_ORDER.get(
                BRAWLER_STATS[x[0]][0], 99
            )
        )

        cols = st.columns(5)

        colors = {
            "Common": "#ffffff",
            "Rare": "#00ff66",
            "Epic": "#ff00ff",
            "Mythic": "#ff0000",
            "Legendary": "#ffff00",
            "Zakladatel": "#ff5500"
        }

        for i, (name, item_data) in enumerate(inventory):

            rarity = BRAWLER_STATS[name][0]

            if isinstance(item_data, dict):
                lvl = item_data.get("level", 1)
                dups = item_data.get("duplicates", 0)
            else:
                lvl = item_data
                dups = 0

            needed = lvl * 2

            with cols[i % 5]:

                st.markdown(
                    f"""
                    <div class="brawler-card"
                    style="border-top-color:{colors[rarity]}">
                        <b style="color:{colors[rarity]}">
                        {name}
                        </b><br>
                        <small>{rarity}</small><br>
                        <span style="color:#ff8c00; font-weight:bold;">Lv. {lvl}</span><br>
                        <small>Karty: {dups}/{needed}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

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

        if st.button("Vypočítat"):

            if op == "+":
                result = n1 + n2

            elif op == "-":
                result = n1 - n2

            elif op == "*":
                result = n1 * n2

            else:
                if n2 == 0:
                    result = "Chyba (dělení nulou)"
                else:
                    result = n1 / n2

            st.code(f"Výsledek: {result}")


with tab_ai:
    st.title("🤖 ULTRADO AI ASISTENT")
    st.caption("Ptej se na cokoliv — od školních dotazů a programování až po herní strategie a nápady na videa!")

    groq_key = st.secrets.get("GROQ_API_KEY")

    if not GROQ_AVAILABLE:
        st.error("Knihovna 'groq' není nainstalována. Přidej 'groq' do souboru requirements.txt.")
    elif not groq_key:
        st.warning("V 'Secrets' chybí klíč GROQ_API_KEY. Vlož ho v nastavení aplikace ve Streamlit Cloud.")
    else:
        client = Groq(api_key=groq_key)

        # Zobrazení předchozích zpráv
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Vstup pro novou zprávu
        user_prompt = st.chat_input("Napiš dotaz nebo se zeptej na hru...")

        if user_prompt:
            # Uložení a zobrazení dotazu uživatele
            st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.write(user_prompt)

            # Příprava kontextu pro AI
            system_prompt = f"""
            Jsi inteligentní a přátelský AI asistent integrovaný přímo v herním webu 'Ultrado'.
            Tvé znalosti jsou neomezené – dokážeš odpovídat na jakékoliv otázky (škola, věda, kód, YouTube tvorba, každodenní témata).
            Zároveň znáš aktuální stav přihlášeného hráče:
            - Uživatelské jméno: {st.session_state.username}
            - Mince: {int(st.session_state.coins)} 🪙
            - Gemy: {int(st.session_state.gems)} 💎
            - Odběratelé: {st.session_state.subs} 👥
            - Počet postav v týmu: {len(st.session_state.inventory)}

            Odpovídej vtipně, věcně a v češtině. Pokud se hráč ptá na hru, využij tyto jeho údaje. Pokud se ptá na cokoliv jiného, odpověz mu plnohodnotně jako vševědoucí AI.
            """

            messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.chat_messages:
                messages.append({"role": m["role"], "content": m["content"]})

            with st.chat_message("assistant"):
                with st.spinner("AI přemýšlí..."):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=1000,
                        )
                        ai_reply = response.choices[0].message.content
                        st.write(ai_reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
                    except Exception as ex:
                        st.error(f"Chyba při komunikaci s AI: {ex}")


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

# Uložení při každé změně stavu
save_game()
    
