import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️")

# --- 1. DATA LOADING ---
@st.cache_data
def load_fab_data():
    # This is the exact source your app is currently using
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

# --- 2. MAIN APP ---
st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo")

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # Select the card
        card = matches[0]
        if len(matches) > 1:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        col1, col2 = st.columns([1, 1])
        
        # --- THE DATA DRILL ---
        # Your screenshot shows info is inside 'printings' -> 0
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            # IMAGE FIX: Use the 'image_url' directly from your screenshot!
            img_url = first_print.get('image_url')
            if img_url:
                st.image(img_url, width="stretch", caption=card['name'])
            else:
                st.warning("No image URL found in the database.")
            
        with col2:
            st.header(card['name'])
            
            # PRICE LINK
            st.subheader("💰 TCGplayer Prices")
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("View Live Prices", tcg_url)
            
            # TEXT FIX: Pulling 'text' or 'flavor_text'
            st.divider()
            # We look at 'text' first, then 'description'
            display_text = card.get('text') or first_print.get('text') or "No ability text found."
            st.write(f"**Card Text:** {display_text}")
            
            # Show Type
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
            if st.button("Add to Collection"):
                st.success(f"Added {card['name']}!")
    else:
        st.error("No card found. Try a shorter name!")
