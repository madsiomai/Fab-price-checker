import streamlit as st
import requests
import time

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️", layout="wide")

@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_live_price(card_name):
    """Refined 2026 Price Fetcher with Backup Logic"""
    # 1. Clean the name for the search engine
    base_name = card_name.split('(')[0].strip()
    
    # 2. Mimic a real web browser to avoid 403 Forbidden errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        # Step A: Find the Product
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={base_name.replace(' ', '%20')}"
        search_response = requests.get(search_url, headers=headers, timeout=10)
        
        if search_response.status_code == 200:
            results = search_response.json().get('results', [])
            if results:
                product_id = results[0].get('productId')
                
                # Step B: Get the Price
                time.sleep(0.5) # Polite delay
                price_url = f"https://tcgcsv.com/tcgplayer/62/product/{product_id}/prices"
                price_response = requests.get(price_url, headers=headers, timeout=10)
                
                if price_response.status_code == 200:
                    prices = price_response.json().get('results', [])
                    if prices:
                        mkt_price = prices[0].get('marketPrice')
                        return f"${mkt_price:.2f}" if mkt_price else "No Market Data"
        
        return "Market N/A"
    except Exception as e:
        # This catch keeps the app from crashing if the server times out
        return "Server Busy"

# --- MAIN APP INTERFACE ---
st.title("🛡️ FaB Price & Card Checker")

user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo").strip()

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # Logic to pick the best match
        exact = next((c for c in matches if c['name'].lower() == user_input.lower()), None)
        card = exact if exact else matches[0]
        
        if len(matches) > 1 and not exact:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        col1, col2 = st.columns([1, 1.2])
        
        # --- THE IMAGE FIX REVISITED ---
        # We look inside 'printings' for the unique STRING ID
        printings = card.get('printings', [])
        if printings:
            first_print = printings[0]
            # Use the string-based ID for the Fabrary API
            img_id = first_print.get('unique_id')
            img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
            
            with col1:
                st.image(img_url, width="stretch")
            
            with col2:
                st.header(card['name'])
                
                # --- LIVE PRICE ---
                st.subheader("💰 TCGplayer Market Price")
                with st.spinner('Checking Market...'):
                    price = get_live_price(card['name'])
                st.metric(label="Market Value", value=price)
                
                st.divider()
                # Text fallback logic
                txt = card.get('text') or first_print.get('text') or card.get('description') or "Check card image."
                st.write(f"**Card Text:** {txt}")
                st.write(f"**Type:** {card.get('type_text', 'N/A')}")
    else:
        st.warning("Card not found.")
