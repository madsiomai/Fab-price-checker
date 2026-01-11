import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker", page_icon="🛡️")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

# --- 2. MAIN APP ---
st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo")

if user_input:
    all_cards = load_fab_data()
    # Find matching cards
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # If many cards match, let the user pick
        if len(matches) > 1:
            choice = st.selectbox("Multiple found, please select:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)
        else:
            card = matches[0]

        col1, col2 = st.columns([1, 1])
        
        # --- THE FIX: DRILLING INTO PRINTINGS ---
        # We look inside the 'printings' list to find the actual ID and Text
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            # Use the unique_id from the first printing
            img_id = first_print.get('unique_id')
            if img_id and img_id != 0:
                img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
                st.image(img_url, width="stretch", caption=card['name'])
            else:
                st.error("⚠️ Image ID is missing in this database entry.")
            
        with col2:
            st.header(card['name'])
            
            # PRICE LINK (TCGplayer)
            st.subheader("💰 Price Check")
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("View Live Prices on TCGplayer", tcg_url)
            
            # TEXT & STATS FIX
            st.divider()
            # We check the printing level first, then the card level
            card_text = first_print.get('text') or card.get('text') or "No card text available."
            st.write(f"**Card Text:** {card_text}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
            # Debugger - Use this if it STILL doesn't work!
            with st.expander("🛠️ View Raw Card Data"):
                st.json(card)
    else:
        st.error("No card found. Try a shorter search term!")
