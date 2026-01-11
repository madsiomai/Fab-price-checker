import streamlit as st
import requests

# --- APP CONFIG ---
st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️", layout="wide")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    # Primary card database
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_live_price(card_name):
    """Fetches real-time market price from TCGCSV (Public TCGplayer Mirror)"""
    try:
        # Clean name: TCGplayer likes 'Snatch' better than 'Snatch (Red)'
        clean_name = card_name.split('(')[0].strip()
        
        # Step A: Search for Product ID (Category 62 = Flesh and Blood)
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={clean_name.replace(' ', '%20')}"
        search_data = requests.get(search_url, timeout=5).json()
        results = search_data.get('results', [])
        
        if results:
            product_id = results[0].get('productId')
            # Step B: Get Market Price using that ID
            price_url = f"https://tcgcsv.com/tcgplayer/62/product/{product_id}/prices"
            price_data = requests.get(price_url, timeout=5).json().get('results', [])
            
            if price_data:
                mkt_price = price_data[0].get('marketPrice')
                return f"${mkt_price:.2f}" if mkt_price else "Check Site"
    except:
        return "N/A"
    return "N/A"

# --- 2. USER INTERFACE ---
st.title("🛡️ FaB Price & Card Checker")
st.write("Live data for Flesh and Blood TCG (2026 Edition)")

# .strip() handles the extra space bar press automatically
raw_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo")
user_query = raw_input.strip().lower()

if user_query:
    all_cards = load_fab_data()
    # Find partial matches
    matches = [c for c in all_cards if user_query in c['name'].lower()]
    
    if matches:
        # Dropdown for multiple versions
        if len(matches) > 1:
            choice = st.selectbox("Multiple versions found. Please select one:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)
        else:
            card = matches[0]

        # Layout: Image on Left, Info on Right
        col1, col2 = st.columns([1, 1.2])
        
        # Access nested printing data
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            # Use image_url directly from the data
            img_url = first_print.get('image_url')
            if img_url:
                st.image(img_url, width="stretch", caption=card['name'])
            else:
                st.error("No image available.")
            
        with col2:
            st.header(card['name'])
            
            # --- LIVE PRICE SECTION ---
            st.subheader("💰 Market Price")
            with st.spinner('Fetching live price...'):
                current_val = get_live_price(card['name'])
            st.metric(label="TCGplayer Market", value=current_val)
            
            # Direct link for buying/verifying
            tcg_search = card['name'].replace(" ", "+")
            st.link_button("View on TCGplayer", f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={tcg_search}")
            
            # --- CARD TEXT SECTION ---
            st.divider()
            # Checks for text in multiple possible locations
            ability_text = card.get('text') or first_print.get('text') or card.get('description') or "No text available."
            st.markdown(f"**Card Text:**\n{ability_text}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
    else:
        st.warning("No card found. Try a different search term!")
