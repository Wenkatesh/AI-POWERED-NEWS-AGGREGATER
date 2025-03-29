import streamlit as st
import requests
import spacy
from textblob import TextBlob
from datetime import datetime, timedelta

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def analyze_sentiment(text):
    """Perform sentiment analysis using TextBlob for long articles."""
    if not text:
        return "Neutral"
    
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.1:
        return "Positive"
    elif sentiment_score < -0.1:
        return "Negative"
    else:
        return "Neutral"

def get_news(date):
    """Fetch news using Mediastack API."""
    MEDIASTACK_API_KEY = "OUR_API_KEY"
    url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&date={date}&limit=10"
    response = requests.get(url)
    return response.json().get("data", [])

# Streamlit UI
st.title("📰 Sentiment Analysis of News Articles")

selected_date = st.sidebar.date_input("Select a date:", datetime.today() - timedelta(days=1))
selected_date = selected_date.strftime("%Y-%m-%d")

if st.sidebar.button("Get News Sentiments"):
    articles = get_news(selected_date)
    
    if not articles:
        st.warning("No news found. Try a different date!")
    else:
        for article in articles:
            st.subheader(article["title"])
            sentiment = analyze_sentiment(article.get("content", "") or article.get("description", ""))
            st.write(f"**Sentiment:** {sentiment}")
