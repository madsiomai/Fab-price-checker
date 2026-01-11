import streamlit as st
import requests

st.set_page_config(page_title="FaB Tracker 2026", page_icon="🛡️")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    # Primary community-driven card data
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

# --- 2. MAIN APP ---
st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo")

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # If multiple matches, pick the best one
        card = matches[0]
        if len(matches) > 1:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        col1, col2 = st.columns([1, 1])
        
        # --- THE FIX: DRILLING INTO PRINTINGS ---
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            # Use the printing's unique_id instead of the card's 0 ID
            img_id = first_print.get('unique_id', 'unknown')
            img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
            st.image(img_url, width="stretch", caption=card['name'])
            
        with col2:
            st.header(card['name'])
            
            # PRICE LINK
            st.subheader("💰 TCGplayer Prices")
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("View Real-Time Prices", tcg_url)
            
            # TEXT & STATS FIX
            st.divider()
            # Some cards put text on the main entry, others inside printings
            card_text = card.get('text') or first_print.get('text') or "No card text found."
            st.write(f"**Card Text:** {card_text}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
            # Helpful Debug (Hidden by default)
            with st.expander("🛠️ View Raw Card Data"):
                st.json(card)
    else:
        st.error("No card found. Try a different name!")
