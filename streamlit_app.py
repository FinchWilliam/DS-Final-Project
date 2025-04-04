import streamlit as st
import pandas as pd
import notebooks.model_functions as mf

st.set_page_config(
    page_title="My Flavour pair recommender",
    page_icon=":smile:",
    layout="wide"
)

st.write('''
            # Input a flavour and see what it recommends to pair with it
        ''')

cols = st.columns([4,4,2])
with cols[0]:
    liked_ingredients = st.text_input("Enter your flavours here, seperated by a comma:", "raspberry")

with cols[1]:
    disliked_ingredients = st.text_input("tell me flavours you don't like, seperated by a comma:")

with cols[2]:
    n_items = st.number_input("How many flavours shall we return?", min_value=0, max_value = 20,value=5)





similarity_matrix = pd.read_csv("data/similarity_matrix.csv", index_col=0)
closest_items, error_codes = mf.recommend_items(sim_matrix=similarity_matrix, near_items=liked_ingredients, far_items=disliked_ingredients, top_n = n_items)
closest_items = list(closest_items.index)

if len(error_codes) != 0:
    for error in error_codes:
        st.write(f"Error {error}")
st.write(f"### The best {n_items} flavors we have to pair:")
for item in closest_items:
    st.write(item.title())