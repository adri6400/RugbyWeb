# app.py
import streamlit as st
from pages import page1, page2, page3, page4, page5, page6, page7 # Import the page1 function from pages.py

st.set_page_config(layout="wide")


# Initialise the variable of session page if it doesn't exist
if 'page' not in st.session_state:
    st.session_state.page = 1

if st.session_state.page == 1:
    page1() 

elif st.session_state.page == 2:
    # each player of home team details
    page2()

elif st.session_state.page == 3:
    # each player of away team details
    page3()

elif st.session_state.page == 4:
    page4()

elif st.session_state.page == 5:
    page5()

elif st.session_state.page == 6:
    page6()

elif st.session_state.page == 7:
    page7()

