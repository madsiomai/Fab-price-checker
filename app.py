import streamlit as st
import requests

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️")

# --- 1. DATA LOADING & PRICE FUNCTIONS ---
@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_price(card_name):
    try:
        # TCGCSV Search
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={card_name.replace(' ', '%20')}"
        results = requests.get(search_url).json().get('results', [])
        if results:
            product_id = results[0].get('productId')
            # Fetch Market Price
            price_url = f"https://tcgcsv.com/tcgplayer/62/product/{product_id}/prices"
            price_data = requests.get(price_url).json().get('results', [])
            if price_data:
                market_val = price_data[0].get('marketPrice')
                return f"${market_val:.2f}" if market_val else "N/A"
    except:
        return "N/A"
    return "N/A"

# --- 2. MAIN APP ---
st.title("🛡️ FaB Price & Card Checker")

# Added .strip() here to fix that extra space bar issue!
user_input = st.text_input("Search Card Name:", placeholder="e.g. Valiant Dynamo").strip()

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        card = matches[0]
        if len(matches) > 1:
            choice = st.selectbox("Multiple found:", [c['name'] for c in matches])
            card = next(c for c in matches if c['name'] == choice)

        # NOW col1 and col2 are defined safely inside the 'if' block
        col1, col2 = st.columns([1, 1])
        
        printings = card.get('printings', [])
        first_print = printings[0] if printings else {}
        
        with col1:
            img_url = first_print.get('image_url')
            if img_url:
                st.image(img_url, width="stretch", caption=card['name'])
            
        with col2:
            st.header(card['name'])
            
            # LIVE PRICE METRIC
            st.subheader("💰 Market Price")
            price_val = get_price(card['name'])
            st.metric(label="TCGplayer Market", value=price_val)
            
            # TCGPLAYER LINK
            clean_name = card['name'].replace(" ", "+")
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={clean_name}"
            st.link_button("View on TCGplayer", tcg_url)
            
            # TEXT & STATS
            st.divider()
            display_text = card.get('text') or first_print.get('text') or card.get('description') or "Rules on card art."
            st.write(f"**Card Text:** {display_text}")
            st.write(f"**Type:** {card.get('type_text', 'N/A')}")
            
    else:
        st.error("No card found. Try a different name!")
