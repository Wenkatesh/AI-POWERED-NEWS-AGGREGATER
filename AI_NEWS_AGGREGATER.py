import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime, timedelta

# ---- Configure Gemini API ----
genai.configure(api_key="AIzaSyApoU6lhmnb1TBsIc_TUtMC-AXtbBPB2_k")

def summarize_text(text):
    """Summarizes the given text into 8-10 lines using Gemini API."""
    if not text:
        return "Summary not available."

    prompt = f"Summarize the following news article in 8 to 10 lines:\n\n{text}"
    
    response = genai.GenerativeModel("gemini-pro").generate_content(prompt)

    return response.text if hasattr(response, "text") else "Summary not available."

# ---- NewsAPI Key ----
NEWS_API_KEY = "de64cd6721a74ad3bb779ace2512533d"

# ---- Function to Fetch News ----
def get_news(category, from_date, to_date):
    """Fetches news articles from NewsAPI based on category and date range."""
    url = f"https://newsapi.org/v2/everything?q={category}&from={from_date}&to={to_date}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    return news_data.get("articles", [])

# ---- Streamlit UI ----
st.title(" AI-Powered News Aggregator")

# ---- User Inputs ----
category = st.selectbox("📌 Select a news category:", 
                        ["business", "entertainment", "general", "health", "science", "sports", "technology"])

# ---- Date Selection ----
today = datetime.today().date()
col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input(" From Date", today - timedelta(days=7), max_value=today)
with col2:
    to_date = st.date_input(" To Date", today, min_value=from_date, max_value=today)

# ---- Fetch and Display News ----
if st.button(" Get News"):
    articles = get_news(category, from_date, to_date)

    if not articles:
        st.warning("No news found for the selected date range. Try different dates or category!")
    else:
        for index, article in enumerate(articles):
            st.subheader(f" {article['title']}")
            st.write(f"**Source:** {article['source']['name']} | **Published At:** {article['publishedAt']}")

            # Expandable section to show full news description
            with st.expander("View News"):
                st.write(article["description"] or "No description available.")

            # Summarization Button - Ensures summary only appears after clicking
            if st.button(f" Summarize: {article['title']}", key=f"summary_btn_{index}"):
                st.session_state[f"summary_{index}"] = summarize_text(article["content"] or article["description"])
            
            # Display summary only if it was generated
            if f"summary_{index}" in st.session_state:
                st.success(st.session_state[f"summary_{index}"])

            st.markdown(f"[🔗 Read Full News]({article['url']})")
