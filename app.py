import streamlit as st
import time
import random
import json
import os
from datetime import datetime, timedelta

# --- OPRAVA IMPORTŮ ---
# Pokud knihovny nejsou nainstalovány, aplikace se aspoň spustí s varováním
try:
    import wikipediaapi
    from deep_translator import GoogleTranslator
    IMPORT_ERR = False
except ImportError:
    IMPORT_ERR = True

# --- NASTAVENÍ STRÁNKY ---
import streamlit.components.v1 as components
# --- POJISTKA PROTI ERRORŮM (Dej to úplně nahoru) ---
if 'mince' not in st.session_state:
    st.session_state.mince = 49
if 'seminka' not in st.session_state:
    st.session_state.seminka = 0
if 'inventar_seedy' not in st.session_state:
    st.session_state.inventar_seedy = []
if 'zasazeno' not in st.session_state:
    st.session_state.zasazeno = []
if 'zasazeno' not in st.session_state:
    # Tady budou rostliny, co už jsou v zemi
    st.session_state.zasazeno = []
    def zobraz_3d_zahradu():
       st.markdown("### 🎮 3D Zahrada Ultrado")
    zasazene_rostliny = st.session_state.get('zasazeno', [])
    js_plants = ""
st.divider()
    st.subheader("🛒 Obchod Ultrado")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("💰 Mince", st.session_state.mince)
    with c2:
        st.metric("🎒 Batoh", len(st.session_state.inventar_seedy))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Koupit Bílý Seed (10 m)"):
            if st.session_state.mince >= 10:
                st.session_state.mince -= 10
                st.session_state.inventar_seedy.append("Bílý Seed")
                st.rerun()
    with col_b:
        if st.button("Koupit Modrý Seed (50 m)"):
            if st.session_state.mince >= 50:
                st.session_state.mince -= 50
                st.session_state.inventar_seedy.append("Modrý Seed")
                st.rerun()

st.divider()

# 2. SÁZENÍ (Tady to dáváš do 3D)
st.subheader("🌱 Zasadit semínko")
if st.session_state.inventar_seedy:
    # Uděláme seznam unikátních věcí v batohu
    moznosti = list(set(st.session_state.inventar_seedy))
    vyber = st.selectbox("Vyber z batohu:", moznosti)
    
    if st.button(f"Zasadit {vyber}", use_container_width=True):
        st.session_state.inventar_seedy.remove(vyber)
        # Uložíme informaci o typu pro 3D okno
        st.session_state.zasazeno.append({"typ": vyber})
        st.success("Zasazeno do 3D zahrady!")
        st.rerun()
else:
    st.info("Batoh je prázdný. Kup si něco v obchodě!")

# --- KONEC BLOKU ---     
    st.markdown("### 🎮 Ultrado Garden 3D")
    
    # Načteme data ze systému do formátu pro JavaScript
    zasazene_rostliny = st.session_state.get('zasazeno', [])
    
    # Příprava rostlin pro JS (předáme barvu podle typu)
    js_plants = ""
    for i, rostlina in enumerate(zasazene_rostliny):
        barva = "0xffffff" if "Bílý" in rostlina['typ'] else "0x0000ff"
        # Každou kytku dáme na trochu jiné místo (náhodně dokola)
        pos_x = (i % 3) * 2 - 2
        pos_z = (i // 3) * 2 - 2
        js_plants += f"""
        const plant{i} = new THREE.Mesh(
            new THREE.BoxGeometry(0.5, 0.5, 0.5),
            new THREE.MeshPhongMaterial({{ color: {barva} }})
        );
        plant{i}.position.set({pos_x}, 0.5, {pos_z});
        scene.add(plant{i});
        """

    html_kod = f"""
    <div id="container" style="width: 100%; height: 400px; background: #0e1117; border-radius: 20px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 400, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, 400);
        document.getElementById('container').appendChild(renderer.domElement);

        scene.add(new THREE.AmbientLight(0x404040));
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(5, 10, 5);
        scene.add(light);

        const ground = new THREE.Mesh(
            new THREE.CylinderGeometry(10, 10, 0.5, 32),
            new THREE.MeshPhongMaterial({{ color: 0x2ecc71 }})
        );
        scene.add(ground);

        // --- TADY SE VYKRESLÍ TVOJE KYTKY ---
        {js_plants}

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        camera.position.set(0, 8, 12);
        controls.update();

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    import streamlit.components.v1 as components
    components.html(html_kod, height=420)
st.divider() # Udělá dělicí čáru
st.subheader("🛒 Obchod se semínky")

# Definice nabídky
nabidka = {
    "Bílý Seed (Základní)": {"cena": 10},
    "Modrý Seed (Vzácný)": {"cena": 50}
}

# Zobrazení tvých peněz a batohu hezky vedle sebe
c1, c2 = st.columns(2)
with c1:
    st.metric("💰 Mince", st.session_state.mince)
with c2:
    # Spočítáme, kolik věcí máš v seznamu inventar_seedy
    pocet_v_batohu = len(st.session_state.get('inventar_seedy', []))
    st.metric("🎒 Semínka v batohu", pocet_v_batohu)

# Tlačítka pro nákup (uděláme dva sloupce)
cols = st.columns(2)
for i, (jmeno, data) in enumerate(nabidka.items()):
    with cols[i]:
        st.write(f"**{jmeno}**")
        if st.button(f"Koupit za {data['cena']}", key=f"buy_{jmeno}"):
            if st.session_state.mince >= data['cena']:
                st.session_state.mince -= data['cena']
                # Přidáme jméno seedu do seznamu v batohu
                st.session_state.inventar_seedy.append(jmeno)
                st.success(f"Koupeno!")
                st.rerun()
            else:
                st.error("Nemáš dost mincí!")
                st.divider()
st.subheader("🌱 Zasadit na zahradu")

# Pokud máš něco v batohu, ukaž výběr
if st.session_state.inventar_seedy:
    # Vybereš si, co chceš zasadit
    vyber = st.selectbox("Co zasadíme?", options=list(set(st.session_state.inventar_seedy)))
    
    if st.button(f"Zasadit {vyber}", use_container_width=True):
        # 1. Odebereme to z batohu
        st.session_state.inventar_seedy.remove(vyber)
        # 2. Přidáme to do seznamu zasazených věcí
        st.session_state.zasazeno.append({"typ": vyber, "cas": "teď"})
        st.success(f"Zasazeno! {vyber} se už připravuje.")
        st.rerun()
else:
    st.info("Tvůj batoh je prázdný. Kup si něco v obchodu nahoře!")

# Výpis toho, co už je v zemi
if st.session_state.zasazeno:
    st.write("---")
    st.write("🌍 **Na tvojí zahradě už roste:**")
    for kytka in st.session_state.zasazeno:
        st.write(f"🌵 {kytka['typ']}")               
# --- DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #FF8C00; font-family: 'Orbitron', sans-serif; }
    .stButton>button { background-color: #FF8C00; color: black; border-radius: 10px; font-weight: bold; border: none; }
    
    /* Herní karty */
    .brawler-card {
        padding: 15px; border-radius: 12px; background: #1c1f26;
        border-top: 4px solid #FF8C00; text-align: center; margin-bottom: 10px;
    }
    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
    }
    .box-shake { animation: shake 0.5s infinite; border: 2px solid red; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA A RARITY ---
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

SAVE_FILE = "ultrido_data.json"

# --- SYSTÉM UKLÁDÁNÍ ---
def save_game():
    data = {
        "coins": st.session_state.coins,
        "gems": st.session_state.gems,
        "inventory": st.session_state.inventory,
        "last_claim": st.session_state.last_claim,
        "last_wheel": st.session_state.last_wheel,
        "subs": st.session_state.subs
    }
    with open(SAVE_FILE, "w") as f: json.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                d = json.load(f)
                st.session_state.coins = d.get("coins", 200)
                st.session_state.gems = d.get("gems", 0)
                st.session_state.inventory = d.get("inventory", {})
                st.session_state.last_claim = d.get("last_claim", time.time())
                st.session_state.last_wheel = d.get("last_wheel", 0)
                st.session_state.subs = d.get("subs", 0)
        except: pass

# --- INICIALIZACE STAVU ---
if 'coins' not in st.session_state:
    st.session_state.coins, st.session_state.gems, st.session_state.inventory = 200, 0, {}
    st.session_state.last_claim, st.session_state.last_wheel = time.time(), 0
    st.session_state.subs = 0
    st.session_state.last_drop = None
    load_game()
zobraz_3d_zahradu()
# Kontrola, jestli máme v paměti semínka, pokud ne, vytvoříme je
if 'seminka' not in st.session_state:
   if 'mince' not in st.session_state:
    st.session_state.mince = 49  # Tvoje startovní hodnota
st.write(f"🎒 V inventáři máš: {st.session_state.seminka} semínek")
# Vytvoření dvou sloupců pro přehlednost
col1, col2 = st.columns(2)

with col1:
    # Zobrazení mincí s ikonou
    st.metric(label="💰 Moje Mince", value=f"{st.session_state.get('mince', 0)}")

with col2:
    # Zobrazení semínek s ikonou
    st.metric(label="🎒 Semínka", value=f"{st.session_state.get('seminka', 0)}")
# --- POMOCNÉ FUNKCE ---
def get_income():
    c_h, g_h = 0, 0
    for name, count in st.session_state.inventory.items():
        if name in BRAWLER_STATS:
            c_h += BRAWLER_STATS[name][1] * count
            g_h += BRAWLER_STATS[name][2] * count
    return c_h, g_h

def open_box(b_type):
    if b_type == "Brawl Box": w = {"Common": 85, "Rare": 14, "Epic": 1, "Legendary": 0}
    elif b_type == "Big Box": w = {"Common": 50, "Rare": 35, "Epic": 10, "Legendary": 5}
    else: w = {"Common": 15, "Rare": 25, "Epic": 35, "Legendary": 23, "Zakladatel": 2}
    
    placeholder = st.empty()
    placeholder.markdown(f'<div class="box-shake" style="padding:20px; text-align:center;"><h2>📦 OTEVÍRÁM {b_type.upper()}...</h2></div>', unsafe_allow_html=True)
    time.sleep(1.5)
    placeholder.empty()

    rarity = random.choices(list(w.keys()), weights=list(w.values()))[0]
    res = random.choice([n for n, d in BRAWLER_STATS.items() if d[0] == rarity])
    
    if res not in st.session_state.inventory: st.session_state.inventory[res] = 1
    else: st.session_state.coins += (BRAWLER_STATS[res][1] * 10)
    
    st.session_state.last_drop = {"name": res, "rarity": rarity}
    save_game()

# --- BOČNÍ PANEL (PRODUKCE) ---
with st.sidebar:
    st.title("⚡ ULTRADO 3.0")
    
    # CESTA KE SLÁVĚ
    st.subheader("📊 CESTA KE SLÁVĚ")
    st.session_state.subs = st.number_input("Odběratelů:", value=st.session_state.subs)
    cil = st.number_input("Cíl (subs):", value=100)
    if cil > 0:
        proc = min(100, int((st.session_state.subs / cil) * 100))
        st.progress(proc / 100)
        st.write(f"{proc}% cesty k {cil} subs!")
        if st.session_state.subs >= cil: st.success("HOTOVO! 🏆"); st.balloons()

    st.divider()

    # ÚKOLY
    with st.expander("✅ MOJE ÚKOLY"):
        st.checkbox("Vymyslet téma", key="t1")
        st.checkbox("Natočit video", key="t2")
        st.checkbox("Sestříhat (YouCut)", key="t3")
        st.checkbox("Vydat na YouTube", key="t4")

    # TRENDY
    with st.expander("🔍 TRENDY"):
        q = st.text_input("Hledat téma:", key="search_sidebar")
        if q:
            st.markdown(f"👉 [YouTube](https://www.youtube.com/results?search_query={q})")
            st.markdown(f"👉 [TikTok](https://www.tiktok.com/search?q={q})")

    # PŘEKLADAČ
    with st.expander("🌍 PŘEKLADAČ"):
        txt = st.text_area("Česky:", key="trans_sidebar")
        if st.button("Přeložit") and not IMPORT_ERR:
            st.success(GoogleTranslator(source='cs', target='en').translate(txt))
        elif IMPORT_ERR: st.error("Knihovna nenalezena.")

    # RESET
    if st.button("🔄 ÚPLNÝ RESET HRY"):
        st.session_state.clear()
        st.rerun()

# --- HLAVNÍ PLOCHA (TABS) ---
tab_game, tab_studio = st.tabs(["🎮 TYCOON HRA", "🎬 PRODUKČNÍ PANEL"])

with tab_game:
    # Horní lišta
    c_h, g_h = get_income()
    col1, col2, col3 = st.columns(3)
    col1.metric("Mince", f"{int(st.session_state.coins)} 🪙", f"+{c_h}/h")
    col2.metric("Gemy", f"{int(st.session_state.gems)} 💎", f"+{g_h}/h")
    col3.metric("Odběratelé", st.session_state.subs)

    # Kolo štěstí
    st.subheader("🎡 Kolo štěstí")
    t_pass = time.time() - st.session_state.last_wheel
    is_free = t_pass >= 86400
    if is_free:
        if st.button("🎰 ZDARMA (Daily)"):
            st.session_state.last_wheel = time.time()
            st.session_state.coins += random.randint(100, 500)
            st.toast("Získáno pár mincí!"); save_game(); st.rerun()
    else:
        st.info(f"Další free spin za {str(timedelta(seconds=int(86400-t_pass)))}")

    st.divider()

    # Shop a Sklad
    c_s1, c_s2 = st.columns([2, 1])
    with c_s1:
        st.subheader("🛒 Shop s Boxy")
        b1, b2, b3 = st.columns(3)
        if b1.button("Brawl Box (100 🪙)"):
            if st.session_state.coins >= 100: st.session_state.coins -= 100; open_box("Brawl Box"); st.rerun()
        if b2.button("Big Box (500 🪙)"):
            if st.session_state.coins >= 500: st.session_state.coins -= 500; open_box("Big Box"); st.rerun()
        if b3.button("Mega Box (50 💎)"):
            if st.session_state.gems >= 50: st.session_state.gems -= 50; open_box("Mega Box"); st.rerun()
    
    with c_s2:
        st.subheader("⛏️ Sklad")
        diff = min(time.time() - st.session_state.last_claim, 43200)
        m_c, m_g = (c_h/3600)*diff, (g_h/3600)*diff
        st.write(f"Vytěženo: {round(m_c,1)} 🪙")
        if st.button("💰 VYZVEDNOUT"):
            st.session_state.coins += m_c; st.session_state.gems += m_g
            st.session_state.last_claim = time.time(); save_game(); st.rerun()

    # Inventář
    st.subheader("🎒 Tvůj Tým (seřazeno)")
    if st.session_state.inventory:
        sorted_inv = sorted(st.session_state.inventory.items(), key=lambda x: RARITY_ORDER[BRAWLER_STATS[x[0]][0]])
        i_cols = st.columns(5)
        for i, (name, count) in enumerate(sorted_inv):
            rar = BRAWLER_STATS[name][0]
            clr = {"Common": "#FFF", "Rare": "#0F0", "Epic": "#F0F", "Legendary": "#FF0", "Zakladatel": "#F40"}[rar]
            with i_cols[i % 5]:
                st.markdown(f'<div class="brawler-card" style="border-top-color:{clr}"><b style="color:{clr}">{name}</b><br><small>{rar}</small></div>', unsafe_allow_html=True)

with tab_studio:
    st.title("🎬 HLAVNÍ PANEL ULTRADO")
    vstup = st.text_input("💡 Co dnes tvoříme?", placeholder="Zadej téma videa...", key="main_input")

    col_p, col_r = st.columns(2)
    with col_p:
        st.subheader("🎥 Produkce")
        if st.button("✂️ YouCut Tipy"): st.info("Zkus 'Keyframes' pro plynulý zoom!")
        if st.button("📺 Návrhy názvů"):
            if vstup: st.success(random.choice([f"Šílený {vstup}!", f"Jak na {vstup}", f"Tajemství {vstup}"]))
        if st.button("🔥 Brutální Hook"):
            if vstup: st.warning(f"Vsadím se, že o {vstup} jsi tohle nevěděl!")

    with col_r:
        st.subheader("📚 Rešerše")
        if st.button("📖 Wikipedie"):
            if vstup and not IMPORT_ERR:
                try:
                    wiki = wikipediaapi.Wikipedia(language='cs', user_agent='Ultrado/1.0')
                    st.write(wiki.page(vstup).summary[:300] + "...")
                except: st.error("Nepodařilo se načíst.")
            elif IMPORT_ERR: st.error("Chybí knihovna wikipedia-api.")
        if st.button("🏷️ Hashtagy"):
            st.code(f"#{vstup if vstup else 'video'} #youcut #viral")

    st.divider()
    if st.button("📝 GENERUJ KOMPLETNÍ PLÁN"):
        if vstup:
            st.balloons()
            st.subheader(f"📋 Plán pro: {vstup}")
            st.write("1. Úvod: Hook (Zaujmout hned)\n2. Střed: Gameplay/Informace\n3. Outro: Výzva k odběru!")

    # Kalkulačka dole
    with st.expander("🔢 RYCHLÁ KALKULAČKA"):
        kn1 = st.number_input("Číslo 1", value=0.0)
        kn2 = st.number_input("Číslo 2", value=0.0)
        kop = st.selectbox("Operace", ["+", "-", "*", "/"])
        if st.button("Vypočítej"):
            if kop == "+": r = kn1+kn2
            elif kop == "-": r = kn1-kn2
            elif kop == "*": r = kn1*kn2
            elif kop == "/": r = kn1/kn2 if kn2 != 0 else "Chyba"
            st.code(f"Výsledek: {r}")

# Admin Mod
with st.sidebar:
    st.divider()
    secret = st.text_input("Admin", type="password")
    if secret == "admin530" and st.button("AKTIVOVAT CHEATY"):
        st.session_state.coins, st.session_state.gems = 99999, 999
        for n in BRAWLER_STATS: st.session_state.inventory[n] = 1
        save_game(); st.rerun()
