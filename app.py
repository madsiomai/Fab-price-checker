import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️", layout="wide")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_live_price(card_name):
    """Fetches real-time market price with 2026 search cleaning"""
    try:
        # TCGplayer search is very picky. We strip out (Red), (Yellow), etc.
        # This leaves just the base name like 'Snatch' or 'Enlightened Strike'
        base_name = card_name.split('(')[0].strip()
        
        # We need a 'User-Agent' in 2026 so the server doesn't block us
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # Step A: Search for Product ID (Category 62 = FaB)
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={base_name.replace(' ', '%20')}"
        search_res = requests.get(search_url, headers=headers, timeout=10).json()
        results = search_res.get('results', [])
        
        if results:
            # We grab the ID of the first result found
            pid = results[0].get('productId')
            
            # Step B: Get the Market Price
            price_url = f"https://tcgcsv.com/tcgplayer/62/product/{pid}/prices"
            price_res = requests.get(price_url, headers=headers, timeout=10).json()
            prices = price_res.get('results', [])
            
            if prices:
                # We pull the marketPrice field
                val = prices[0].get('marketPrice')
                return f"${val:.2f}" if val else "Market N/A"
                
        return "Not Found"
    except Exception as e:
        return "Error"

# --- 2. USER INTERFACE ---
st.title("🛡️ FaB Price & Card Checker")

# The .strip() here fixes the extra space bar issue automatically
raw_input = st.text_input("Search Card Name:", placeholder="e.g. Command and Conquer")
user_query = raw_input.strip().lower()

if user_query:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_query in c['name'].lower()]
    
    if matches:
        # Exact match priority
        exact = next((c for c in matches if c['name'].lower() == user_query), None)
        card = exact if exact else matches[0]
        
        if len(matches) > 1 and not exact:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        col1, col2 = st.columns([1, 1.2])
        
        # Drill into printings for the image and extra text
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            img_url = first_print.get('image_url')
            if img_url:
                st.image(img_url, width="stretch", caption=card['name'])
            
        with col2:
            st.header(card['name'])
            
            # THE LIVE PRICE
            st.subheader("💰 Market Price")
            with st.spinner('Checking TCGplayer...'):
                price = get_live_price(card['name'])
            st.metric(label="TCGplayer Market Price", value=price)
            
            # TCGplayer Button
            tcg_search = card['name'].replace(" ", "+")
            st.link_button("View on TCGplayer", f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={tcg_search}")
            
            # CARD TEXT
            st.divider()
            txt = card.get('text') or first_print.get('text') or card.get('description') or "See card image for text."
            st.markdown(f"**Card Text:**\n{txt}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
    else:
        st.warning("No card found.")
