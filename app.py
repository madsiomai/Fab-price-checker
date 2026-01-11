import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️")

# --- 1. SEARCH LOGIC ---
st.title("🛡️ FaB Price Checker")
user_input = st.text_input("Enter Card Name:", placeholder="e.g. Enlightened Strike")

@st.cache_data
def load_all_cards():
    # This is the gold standard for FaB card data
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

if user_input:
    all_cards = load_all_cards()
    
    # "Fuzzy" search: finds the card even if you only type part of the name
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        # If multiple cards match, let the user pick from a dropdown
        if len(matches) > 1:
            st.write(f"Found {len(matches)} matches. Please select one:")
            card_names = [c['name'] for c in matches]
            selected_name = st.selectbox("Select Card:", card_names)
            card = next(c for c in matches if c['name'] == selected_name)
        else:
            card = matches[0]

        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Try to show the image using the most common URL format
            img_id = card.get('unique_id', '0')
            img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
            st.image(img_url, width="stretch", caption=card['name'])
            
        with col2:
            st.header(card['name'])
            
            # --- 2. THE PRICE SOLUTION ---
            st.subheader("💰 Price Check")
            st.write("Live prices from TCGplayer (Open in new tab):")
            
            # Create a clean search link
            search_query = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={search_query}"
            
            st.link_button("🚀 View TCGplayer Prices", tcg_url)
            
            # Add a manual price tracker for your collection
            price_guess = st.number_input("Found a price? Track it here:", value=0.0)
            if st.button("Add to Collection"):
                st.success(f"Saved {card['name']} at ${price_guess}!")
                
            st.divider()
            st.write(f"**Description:** {card.get('text', 'N/A')}")
    else:
        st.error(f"Could not find '{user_input}'. Try a shorter part of the name!")
