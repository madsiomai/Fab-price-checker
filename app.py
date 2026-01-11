import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="FaB Tracker 2026", page_icon="🛡️")

# --- 1. INITIALIZE COLLECTION ---
if 'my_collection' not in st.session_state:
    st.session_state.my_collection = []

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🎴 My Collection")
    for item in st.session_state.my_collection:
        st.write(f"✅ {item}")
    if st.button("Clear All"):
        st.session_state.my_collection = []
        st.rerun()

# --- 3. PRICE DATA (TCGCSV) ---
@st.cache_data(ttl=3600)
def load_prices():
    # Category 62 is Flesh and Blood
    url = "https://tcgcsv.com/categories/62/prices"
    try:
        return pd.read_csv(url)
    except:
        return None

# --- 4. MAIN SEARCH ---
st.title("🛡️ FaB Price Checker")
# We MUST define 'query' before we use 'if query:'
query = st.text_input("Search for a card:", placeholder="e.g. Command and Conquer")

@st.cache_data
def load_card_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

if query:
    cards = load_card_data()
    prices = load_prices()
    matches = [c for c in cards if query.lower() in c['name'].lower()]
    
    if matches:
        card = matches[0]
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # FIXED: Updated for 2026 Streamlit standards
            img_id = card.get('unique_id', 'unknown')
            img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
            st.image(img_url, width="stretch")
            
        with col2:
            st.header(card['name'])
            
            # AUTOMATIC PRICE (TCGCSV)
            st.subheader("💰 Live Market Price")
            product_id = card.get('tcgplayer_id')
            
            if prices is not None and product_id:
                row = prices[prices['productId'] == product_id]
                if not row.empty:
                    mkt = row.iloc[0]['marketPrice']
                    st.metric("TCGplayer Market", f"${mkt:.2f}")
                else:
                    st.write("Price data not found for this specific printing.")
            else:
                st.write("Fetching live prices...")
            
            if st.button(f"➕ Add to Collection"):
                if card['name'] not in st.session_state.my_collection:
                    st.session_state.my_collection.append(card['name'])
                    st.rerun()
            
            st.divider()
            st.write(f"**Text:** {card.get('text', 'N/A')}")
    else:
        st.warning("Card not found!")
