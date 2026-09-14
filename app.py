import streamlit as st
import streamlit.components.v1 as components
import time
import random
import json
import os
from datetime import timedelta

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

# ---------------- LOKÁLNÍ UKLÁDÁNÍ (LOCALSTORAGE) ----------------

# Načtení uložení z URL/prohlížeče při spuštění
query_params = st.query_params

if "loaded_from_client" not in st.session_state:
    if "save_data" in query_params:
        try:
            data = json.loads(query_params["save_data"])
            st.session_state.coins = data.get("coins", 200)
            st.session_state.gems = data.get("gems", 0)
            st.session_state.inventory = data.get("inventory", {})
            st.session_state.last_claim = data.get("last_claim", time.time())
            st.session_state.last_wheel = data.get("last_wheel", 0)
            st.session_state.subs = data.get("subs", 0)
        except Exception:
            pass
    st.session_state.loaded_from_client = True

# Standardní nastavení proměnných
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


def save_game():
    """Uloží data přímo do prohlížeče daného uživatele (localStorage)."""
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel,
        "subs": st.session_state.subs,
    }
    json_str = json.dumps(data)
    
    # JavaScript pro uložení do localStorage daného zařízení
    js_code = f"""
    <script>
        localStorage.setItem('ultrado_user_save', '{json_str}');
    </script>
    """
    components.html(js_code, height=0, width=0)

# Synchronizace uložení do localStorage při zapnutí stránky
js_load_code = """
<script>
    const savedData = localStorage.getItem('ultrado_user_save');
    const urlParams = new URLSearchParams(window.location.search);
    if (savedData && !urlParams.has('save_data')) {
        urlParams.set('save_data', savedData);
        window.location.search = urlParams.toString();
    }
</script>
"""
components.html(js_load_code, height=0, width=0)


# ---------------- DATA ----------------

RARITY_ORDER = {
    "Zakladatel": 0,
    "Legendary": 1,
    "Epic": 2,
    "Rare": 3,
    "Common": 4
}

BRAWLER_STATS = {
    "YouCut Bot": ["Common", 20, 0, 100],
    "Sběrač Pixelů": ["Common", 25, 0, 80],
    "Kluk Střihač": ["Common", 30, 0, 60],
    "Boxík": ["Common", 15, 0, 120],
    "Filtrová Víla": ["Rare", 60, 0, 100],
    "Brawl Expert": ["Rare", 80, 0, 70],
    "Ultrido Velitel": ["Epic", 150, 0.5, 100],
    "Zlatý Střihač": ["Epic", 200, 0.8, 65],
    "Data-Drak": ["Epic", 250, 1.0, 40],
    "Drahokamový Titán": ["Legendary", 800, 3.5, 100],
    "Brawl Král": ["Legendary", 1200, 5.0, 50],
    "Zakladatel (TY)": ["Zakladatel", 5000, 7.0, 100]
}

# ---------------- POMOCNÉ FUNKCE ----------------

def get_income():
    coins_h = 0
    gems_h = 0

    for name, count in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            coins_h += BRAWLER_STATS[name][1] * count
            gems_h += BRAWLER_STATS[name][2] * count

    return coins_h, gems_h


def open_box(box_type):

    if box_type == "Brawl Box":
        chances = {
            "Common": 85,
            "Rare": 14,
            "Epic": 1,
            "Legendary": 0,
        }

    elif box_type == "Big Box":
        chances = {
            "Common": 50,
            "Rare": 35,
            "Epic": 10,
            "Legendary": 5,
        }

    else:
        chances = {
            "Common": 15,
            "Rare": 25,
            "Epic": 35,
            "Legendary": 23,
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
        st.session_state.inventory[reward] = 1
    else:
        st.session_state.coins += (
            BRAWLER_STATS[reward][1] * 10
        )

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

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("⚡ ULTRADO 3.0")

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

tab_game, tab_studio = st.tabs([
    "🎮 TYCOON",
    "🎬 PRODUKČNÍ PANEL"
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

    st.write(f"Vytěženo: {round(mined_coins,1)} 🪙")

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
            key=lambda x: RARITY_ORDER[
                BRAWLER_STATS[x[0]][0]
            ]
        )

        cols = st.columns(5)

        colors = {
            "Common": "#ffffff",
            "Rare": "#00ff66",
            "Epic": "#ff00ff",
            "Legendary": "#ffff00",
            "Zakladatel": "#ff5500"
        }

        for i, (name, count) in enumerate(inventory):

            rarity = BRAWLER_STATS[name][0]

            with cols[i % 5]:

                st.markdown(
                    f"""
                    <div class="brawler-card"
                    style="border-top-color:{colors[rarity]}">
                        <b style="color:{colors[rarity]}">
                        {name}
                        </b><br>
                        <small>{rarity}</small><br>
                        ×{count}
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
                        st.write(page.summary[:500] + "...")
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
                st.session_state.inventory[name] = 1

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
    
