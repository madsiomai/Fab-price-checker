import streamlit as st
import requests

st.set_page_config(page_title="FaB Price Checker", layout="wide")

st.title("🛡️ Flesh and Blood Price Checker")
st.write("Enter a card name to see current TCGplayer market prices.")

# 1. Search Bar
card_query = st.text_input("Card Name", placeholder="e.g. Command and Conquer")

if card_query:
    # 2. Get Card Data (using The FAB Cube/Open Source data)
    # For this hack, we'll use a direct search link to fetch the card details
    search_url = f"https://api.scryfall.com/cards/search?q={card_query}" # Placeholder logic
    
    # NOTE: In a full app, we would use the FAB Cube JSON. 
    # For now, let's simulate the display layout:
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Displaying a sample card image from FABDB logic
        st.image("https://storage.googleapis.com/fabmaster/media/images/WTR156.width-450.png", caption="Card Art")
        
    with col2:
        st.subheader(f"Results for: {card_query}")
        st.info("**TCGplayer Market Price:** $85.50")
        
        # Create a simple table for variations
        price_data = {
            "Finish": ["Non-Foil", "Rainbow Foil", "Cold Foil"],
            "Market Price": ["$85.50", "$120.00", "$450.00"],
            "Low": ["$80.00", "$110.00", "$425.00"]
        }
        st.table(price_data)
        
        st.button("View on TCGplayer")
