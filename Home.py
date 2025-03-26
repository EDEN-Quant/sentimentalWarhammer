import streamlit as st


st.set_page_config(page_title="Sentiment Analysis Tool", page_icon="📊")

# """
# Home.py

# This module serves as the main entry point for a sentiment analysis tool built using Streamlit. 
# The tool is designed to analyze and visualize sentiment data for two distinct models:

# 1. Macro Team Model: Focused on analyzing macroeconomic sentiment trends.
# 2. Stocks Team Model: Tailored for sentiment analysis related to stock market data.

# Users can interact with the application to explore sentiment insights and trends for their respective teams.
# """



st.title("Sentiment Analysis Tool")
st.write(
    """
    Welcome to the Sentiment Analysis Tool! This application allows you to analyze and visualize sentiment data 
    for two distinct models:
    
    1. **Macro Team Model**: Focused on analyzing macroeconomic sentiment trends.
    2. **Stocks Team Model**: Tailored for sentiment analysis related to stock market data.
    
    Use the navigation options on the sidebar to explore sentiment insights and trends for your team.
    """
)


