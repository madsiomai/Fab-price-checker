import streamlit as st
import requests

st.set_page_config(page_title="FaB Tracker", page_icon="🛡️")

# --- INITIALIZE COLLECTION ---
if 'my_collection' not in st.session_state:
    st.session_state.my_collection = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎴 My Collection")
    for item in st.session_state.my_collection:
        st.write(f"✅ {item}")
    if st.button("Clear All"):
        st.session_state.my_collection = []
        st.rerun()

# --- MAIN APP ---
st.title("🛡️ FaB Price Checker")
query = st.text_input("Search for a card:", placeholder="e.g. Valiant Dynamo")

@st.cache_data
def load_data():
    # Fetching the most reliable community card data
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

if query:
    cards = load_data()
    # Find matches
    matches = [c for c in cards if query.lower() in c['name'].lower()]
    
    if matches:
        card = matches[0]
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # TRY MULTIPLE IMAGE SOURCES
            # Source A: Fabrary
            img_id = card.get('unique_id', 'unknown')
            img_url = f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
            st.image(img_url, use_container_width=True)
            
        with col2:
            st.header(card['name'])
            
            # PRICE SECTION
            st.subheader("💰 Price Check")
            tcg_search = card['name'].replace(" ", "+")
            st.info("Market prices change fast! Check TCGplayer below:")
            st.link_button(f"Verify Price for {card['name']}", f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={tcg_search}")
            
            # COLLECTION BUTTON
            if st.button(f"➕ Save to Collection"):
                if card['name'] not in st.session_state.my_collection:
                    st.session_state.my_collection.append(card['name'])
                    st.rerun()
            
            st.divider()
            st.write(f"**Text:** {card.get('text', 'N/A')}")
    else:
        st.warning("Card not found. Try a different name!")
