import streamlit as st
import requests
import spacy
import google.generativeai as genai
from textblob import TextBlob
from datetime import datetime, timedelta
from gtts import gTTS
from googletrans import Translator
import os

# Configure Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")
translator = Translator()

# Mediastack API Key
MEDIASTACK_API_KEY = "YOUR_MEDIASTACK_API_KEY"

def get_news_by_country_category_date(country, category, date):
    """Fetch news based on country, category, and date using Mediastack API."""
    url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&countries={country}&categories={category}&date={date}&limit=15"
    response = requests.get(url)
    news_data = response.json()
    return news_data.get("data", [])

# Custom CSS for Colorful Futuristic UI with Dark/Light Mode
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .title-text {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(255,255,255,0.9);
    }
    .news-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255,255,255,0.5);
    }
    .news-card:hover {
        transform: scale(1.05);
        transition: 0.3s;
    }
    .button {
        display: inline-block;
        padding: 10px 20px;
        color: white;
        background: #ff6a00;
        border-radius: 5px;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main UI
# Main UI
st.markdown("<div class='title-text'>🤖 AI-Powered News Aggregator with Voice 🗣️</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Stay updated with the latest news across the globe in multiple languages</div>", unsafe_allow_html=True)

st.sidebar.header("🌍 News Preferences")
selected_country = st.sidebar.selectbox("Select Country", ["us", "in", "gb", "ca", "au", "None"])
selected_category = st.sidebar.selectbox("Select Category", ["general", "business", "entertainment", "health", "science", "sports", "technology", "politics", "world", "environment"])
selected_language = st.sidebar.selectbox("Select Language", ["English", "Hindi", "French", "Spanish", "German", "Japanese", "Russian"])
selected_date = st.sidebar.date_input("Select Date", datetime.today() - timedelta(days=1))

if st.sidebar.button("Get News", key="news_button"):
    articles = get_news_by_country_category_date(selected_country, selected_category, selected_date.strftime("%Y-%m-%d"))
    
    if not articles:
        st.warning("No news found. Try different filters!")
    else:
        for index, article in enumerate(articles):
            st.markdown(f"<div class='news-card'><h2>{article['title']}</h2><h4>Source: {article['source']}</h4><h4>Published: {article['published_at']}</h4>", unsafe_allow_html=True)
            translated_text = translator.translate(article["description"], dest=selected_language.lower()).text
            st.write(f"**Summary in {selected_language}:** {translated_text}")
            
            # AI-Powered Sentiment Analysis
            sentiment = TextBlob(article["description"]).sentiment.polarity
            sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
            st.write(f"**Sentiment:** {sentiment_label}")
            
            # Text to Speech
            tts = gTTS(text=translated_text, lang=selected_language[:2].lower())
            audio_file = f"news_audio_{index}.mp3"
            tts.save(audio_file)
            st.audio(audio_file, format="audio/mp3")
            
            st.markdown(f"<a href='{article['url']}' target='_blank' class='button'>Read More</a></div>", unsafe_allow_html=True)
