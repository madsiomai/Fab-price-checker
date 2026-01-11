import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker", page_icon="🛡️")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    # Using the most reliable open-source card database
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

# --- 2. MAIN APP ---
st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:", placeholder="e.g. Command and Conquer")

if user_input:
    all_cards = load_fab_data()
    # Find all cards that contain the user's text
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # If many cards match, let the user choose
        if len(matches) > 1:
            choice = st.selectbox("Multiple found, please select:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)
        else:
            card = matches[0]

        col1, col2 = st.columns([1, 1])
        
        with col1:
            # IMAGE FIX: Use the first printing's ID for the image
            # This is the most reliable way to hit the Fabrary image server
            printings = card.get('printings', [{}])
            img_id = printings[0].get('id', 'unknown') if printings else 'unknown'
            img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
            
            st.image(img_url, width="stretch", caption=card['name'])
            
        with col2:
            st.header(card['name'])
            
            # PRICE FIX: Clean search link
            st.subheader("💰 Price Check")
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("View Prices on TCGplayer", tcg_url)
            
            # DESCRIPTION FIX: Pulling from the correct data field
            st.divider()
            card_text = card.get('text', card.get('description', 'No text available.'))
            st.write(f"**Card Text:** {card_text}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
    else:
        st.error("No card found. Try a shorter search term!")
