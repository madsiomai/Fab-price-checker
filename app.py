import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_price(card_name):
    try:
        # TCGCSV is a community tool that pulls real TCGplayer prices
        # We search category 62 (Flesh and Blood) for your card name
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={card_name.replace(' ', '%20')}"
        results = requests.get(search_url).json().get('results', [])
        if results:
            product_id = results[0].get('productId')
            # Now we get the specific price for that product ID
            price_url = f"https://tcgcsv.com/tcgplayer/62/product/{product_id}/prices"
            price_data = requests.get(price_url).json().get('results', [])
            if price_data:
                # Returns the Market Price
                return f"${price_data[0].get('marketPrice', 'N/A')}"
    except:
        return "Price Unavailable"
    return "N/A"

# --- 2. MAIN APP ---
st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo")

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        card = matches[0]
        if len(matches) > 1:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        col1, col2 = st.columns([1, 1])
        
        # Pulling printing info for the image
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            # We use the 'image_url' that we know works from your screenshot
            img_url = first_print.get('image_url')
            if img_url:
                st.image(img_url, width="stretch", caption=card['name'])
            
        with col2:
            st.header(card['name'])
            
            # --- THE PRICE FIX ---
            st.subheader("💰 Market Price")
            current_price = get_price(card['name'])
            st.metric(label="TCGplayer Market", value=current_price)
            
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("Buy on TCGplayer", tcg_url)
            
            # --- THE TEXT FIX ---
            st.divider()
            # FAB Cube data sometimes uses 'description' for the actual card rules
            display_text = card.get('text') or first_print.get('text') or card.get('description') or "Check card image for rules."
            st.write(f"**Card Text:** {display_text}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
    else:
        st.error("No card found. Try a shorter name!")
