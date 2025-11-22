import streamlit as st
from main import compose_response

st.title("🌍 Multi-Agent Tourism System")
query = st.text_input("Enter your trip query:")

if st.button("Submit"):
    result = compose_response(query)
    st.write(result)
