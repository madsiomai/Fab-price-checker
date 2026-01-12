import streamlit as st
import requests
import time

# --- 1. SETTINGS & GAMING THEME ---
st.set_page_config(page_title="FaB NEXUS 2026", page_icon="⚔️", layout="wide")

# Custom CSS for a sleek, dark, modern gaming vibe
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #4a9eff; }
    .stButton>button { background-color: #4a9eff; color: white; border-radius: 5px; width: 100%; }
    .stTextInput>div>div>input { background-color: #1e2130; color: #4a9eff; border: 1px solid #4a9eff; }
    h1 { text-shadow: 2px 2px #4a9eff; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINES ---
@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_live_price(card_name):
    """The 'Hardened' 2026 Price Engine"""
    base_name = card_name.split('(')[0].strip()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        # Step A: Search via TCGCSV (The 2026 gold standard mirror)
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={base_name.replace(' ', '%20')}"
        res = requests.get(search_url, headers=headers, timeout=8).json()
        if res.get('results'):
            pid = res['results'][0].get('productId')
            time.sleep(0.3)
            # Step B: Fetch Market Price
            price_res = requests.get(f"https://tcgcsv.com/tcgplayer/62/product/{pid}/prices", headers=headers).json()
            if price_res.get('results'):
                val = price_res['results'][0].get('marketPrice')
                return f"${val:.2f}" if val else "Listing N/A"
        return "Market N/A"
    except:
        return "Server Lag"

# --- 3. STATE MANAGEMENT (RECENT SEARCHES) ---
if 'history' not in st.session_state:
    st.session_state.history = []

def add_to_history(name):
    if name not in st.session_state.history:
        st.session_state.history.insert(0, name)
        st.session_state.history = st.session_state.history[:5] # Keep last 5

# --- 4. SIDEBAR (GAMING HUB) ---
with st.sidebar:
    st.title("🛡️ NEXUS HUB")
    st.subheader("🔥 Trending 2026")
    # Instant search buttons for popular 2026 cards
    for trend in ["Rosetta Thorn", "Command and Conquer", "Taylor"]:
        if st.button(trend):
            st.session_state.search_trigger = trend
            
    st.divider()
    st.subheader("🕒 Recent")
    for item in st.session_state.history:
        st.caption(f"• {item}")

# --- 5. MAIN UI ---
st.title("⚔️ FaB NEXUS CARD ENGINE")

# Logic to handle clicks from Trending buttons
default_search = st.session_state.get('search_trigger', "")
user_input = st.text_input("READY SEARCH ENGINE:", value=default_search, placeholder="Enter Card Name...").strip()

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        card = next((c for c in matches if c['name'].lower() == user_input.lower()), matches[0])
        add_to_history(card['name'])
        
        col1, col2 = st.columns([1, 1.2])
        
        # Image Display logic
        printings = card.get('printings', [])
        with col1:
            if printings:
                first = printings[0]
                # Direct URL is often safer than building it
                img_url = first.get('image_url') or f"https://api.fabrary.net/v1/cards/image/{first.get('unique_id')}.png"
                st.image(img_url, use_container_width=True)
            else:
                st.warning("NO VISUAL DATA")
        
        with col2:
            st.header(card['name'])
            
            # MODERN PRICE DISPLAY
            with st.container():
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    with st.spinner('SYNCING...'):
                        price = get_live_price(card['name'])
                    st.metric("MARKET PRICE", price)
                with p_col2:
                    st.write("") # Spacer
                    st.write("")
                    st.link_button("🛒 BUY ON TCG", f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={card['name'].replace(' ', '+')}")
            
            st.divider()
            txt = card.get('text') or (printings[0].get('text') if printings else "No Text")
            st.info(f"**DATA LOG:**\n\n{txt}")
            st.write(f"**CLASS/TYPE:** {card.get('type_text', 'N/A')}")
    else:
        st.error("CARD NOT FOUND IN ARCHIVES")
