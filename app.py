def get_price(card_name):
    try:
        # Step 1: Search TCGplayer (Category 62 is Flesh and Blood)
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={card_name.replace(' ', '%20')}"
        search_results = requests.get(search_url).json().get('results', [])
        
        if search_results:
            # We take the first product ID that matches
            product_id = search_results[0].get('productId')
            
            # Step 2: Get the Market Price for that ID
            price_url = f"https://tcgcsv.com/tcgplayer/62/product/{product_id}/prices"
            price_data = requests.get(price_url).json().get('results', [])
            
            if price_data:
                # 'marketPrice' is the standard value used for trade/sale
                market_val = price_data[0].get('marketPrice')
                return f"${market_val:.2f}" if market_val else "N/A"
    except Exception:
        return "Price Error"
    return "N/A"

# --- In your main display block ---
with col2:
    st.header(card['name'])
    
    # NEW PRICE DISPLAY
    st.subheader("💰 Market Price")
    price = get_price(card['name'])
    
    # This creates a big, professional price bubble
    st.metric(label="TCGplayer Market", value=price)
    
    # Keep the button for manual verification
    st.link_button("View on TCGplayer", tcg_url)
