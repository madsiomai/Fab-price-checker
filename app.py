import streamlit as st
import requests
import time

st.set_page_config(page_title="FaB Checker 2026", page_icon="🛡️", layout="wide")

@st.cache_data
def load_fab_data():
    url = "https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/master/json/english/card.json"
    return requests.get(url).json()

def get_live_price(card_name):
    base_name = card_name.split('(')[0].strip()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36'}
    try:
        search_url = f"https://tcgcsv.com/tcgplayer/62/search?q={base_name.replace(' ', '%20')}"
        res = requests.get(search_url, headers=headers, timeout=10).json()
        if res.get('results'):
            pid = res['results'][0].get('productId')
            time.sleep(0.5)
            p_res = requests.get(f"https://tcgcsv.com/tcgplayer/62/product/{pid}/prices", headers=headers).json()
            if p_res.get('results'):
                val = p_res['results'][0].get('marketPrice')
                return f"${val:.2f}" if val else "No Data"
        return "Market N/A"
    except:
        return "Server Busy"

st.title("🛡️ FaB Price & Card Checker")
user_input = st.text_input("Search Card Name:").strip()

if user_input:
    all_cards = load_fab_data()
    matches = [c for c in all_cards if user_input.lower() in c['name'].lower()]
    
    if matches:
        card = next((c for c in matches if c['name'].lower() == user_input.lower()), matches[0])
        col1, col2 = st.columns([1, 1.2])
        
        # --- THE IMAGE FIX RE-CRACKED ---
        printings = card.get('printings', [])
        
        with col1:
            if printings:
                # We try two different ID types just in case
                first_print = printings[0]
                img_id = first_print.get('unique_id') or first_print.get('id')
                
                # If the Fabrary API changed, we use the image_url field directly as a backup
                img_url = first_print.get('image_url') or f"https://api.fabrary.net/v1/cards/image/{img_id}.png"
                
                st.image(img_url, use_container_width=True)
                
                # DEBUGGER: Only shows if you click it
                with st.expander("🛠️ Debug Image Data"):
                    st.write(f"Attempting ID: {img_id}")
                    st.write(f"Attempting URL: {img_url}")
                    st.json(first_print)
            else:
                st.error("No printings found for this card.")
            
        with col2:
            st.header(card['name'])
            price = get_live_price(card['name'])
            st.metric(label="TCGplayer Market Price", value=price)
            st.divider()
            txt = card.get('text') or (printings[0].get('text') if printings else "") or "No text."
            st.write(f"**Card Text:** {txt}")
