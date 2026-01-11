import streamlit as st
import requests

st.set_page_config(page_title="FaB Tracker", page_icon="🛡️")

# --- INITIALIZE COLLECTION ---
# This creates a "hidden list" that stays active while you use the app
if 'my_collection' not in st.session_state:
    st.session_state.my_collection = []

# --- SIDEBAR COLLECTION VIEW ---
with st.sidebar:
    st.header("🎴 My Collection")
    if not st.session_state.my_collection:
        st.write("Your list is empty!")
    for item in st.session_state.my_collection:
        st.write(f"- {item}")
    
    if st.button("Clear Collection"):
        st.session_state.my_collection = []
        st.rerun()

# --- MAIN APP ---
st.title("🛡️ Flesh and Blood Price Checker")
query = st.text_input("Search for a card:", placeholder="e.g. Art of War")

@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

if query:
    all_cards = load_fab_data()
    results = [c for c in all_cards if query.lower() in c['name'].lower()]
    
    if results:
        card = results[0]
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Using Fabrary as a more reliable image source
            img_id = card.get('printings', [{}])[0].get('unique_id', card.get('unique_id'))
            st.image(f"https://api.fabrary.net/v1/cards/image/{img_id}.png", use_container_width=True)
            
        with col2:
            st.header(card['name'])
            
            # THE ADD BUTTON
            if st.button(f"➕ Add {card['name']} to Collection"):
                if card['name'] not in st.session_state.my_collection:
                    st.session_state.my_collection.append(card['name'])
                    st.toast(f"Added {card['name']}!")
                    st.rerun()

            st.divider()
            tcg_url = f"https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q={card['name'].replace(' ', '+')}"
            st.link_button("🎯 View Live Prices on TCGplayer", tcg_url)
