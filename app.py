import streamlit as st
import pandas as pd
import requests

# 1. Load the Price Data from TCGCSV
@st.cache_data(ttl=3600) # Refreshes once per hour
def get_tcg_prices():
    # Category 62 is usually Flesh and Blood on TCGplayer
    url = "https://tcgcsv.com/categories/62/prices" 
    # This reads the live price list into a table
    df = pd.read_csv(url)
    return df

# 2. Update your search logic
if query:
    all_cards = load_data() # Your existing function
    price_df = get_tcg_prices()
    
    matches = [c for c in all_cards if query.lower() in c['name'].lower()]
    
    if matches:
        card = matches[0]
        # Match the card to its price using the TCGplayer ID
        # Many FaB datasets store this under 'tcgplayer_id' or 'product_id'
        tcg_id = card.get('tcgplayer_id') 
        
        if tcg_id:
            # Find the row in the price table that matches our card
            card_price_row = price_df[price_df['productId'] == tcg_id]
            
            if not card_price_row.empty:
                market_price = card_price_row.iloc[0]['marketPrice']
                st.metric(label="Market Price", value=f"${market_price:.2f}")
            else:
                st.write("Price not found in today's CSV update.")
