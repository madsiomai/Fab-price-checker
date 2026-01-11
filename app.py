import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

# --- 2. MAIN SEARCH ---
st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo")

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # If multiple cards match (like 'Strike'), pick the first or use a selectbox
        card = matches[0]
        if len(matches) > 1:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        col1, col2 = st.columns([1, 1])
        
        with col1:
            # IMAGE LOGIC: Dive into the first printing
            printings = card.get('printings', [])
            if printings:
                # We use the 'unique_id' from the first printing for the image
                img_id = printings[0].get('unique_id', 'unknown')
                img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
                st.image(img_url, width="stretch", caption=card['name'])
            else:
                st.warning("No printing data found for this card.")
            
        with col2:
            st.header(card['name'])
            
            # PRICE LINK (TCGplayer)
            st.subheader("💰 TCGplayer Prices")
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("View Real-Time Prices", tcg_url)
            
            # DESCRIPTION & STATS
            st.divider()
            # Most cards have 'text', but heroes might use 'description'
            desc = card.get('text', card.get('description', 'No text available.'))
            st.write(f"**Card Text:** {desc}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
            # Debugging Tool (Hidden by default)
            with st.expander("🛠️ Debug Raw Data"):
                st.write(card)
    else:
        st.error("No card found. Try a different name!")
