import streamlit as st
import requests
import spacy
from textblob import TextBlob
from datetime import datetime, timedelta
from gtts import gTTS
import os

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

def extract_entities_and_keywords(text):
    """Extract named entities and keywords from the text."""
    if not text:
        return [], []
    
    doc = nlp(text)
    entities = [f"{ent.text} ({ent.label_})" for ent in doc.ents]
    keywords = [chunk.text for chunk in doc.noun_chunks]
    return entities, keywords

def summarize_text(text):
    """Summarize long news articles."""
    if not text:
        return "No content available to summarize."
    
    sentences = text.split('.')
    summary = '. '.join(sentences[:5]) + ('.' if len(sentences) > 5 else '')
    return summary

def text_to_speech(text, filename="news_audio.mp3"):
    """Convert summarized text to speech and save as an audio file."""
    tts = gTTS(text=text, lang="en")
    tts.save(filename)
    return filename

def get_news(country, category, date):
    """Fetch news using Mediastack API."""
    MEDIASTACK_API_KEY = "9f9d26568717f598067ae30d5a2e0d60"
    url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&countries={country}&categories={category}&date={date}&limit=10"
    response = requests.get(url)
    return response.json().get("data", [])

# Streamlit UI
st.title("📰 Sentiment Analysis & Summarized News with Speech")

# Sidebar options
st.sidebar.header("Select News Preferences")
countries = {"United States": "us", "India": "in", "United Kingdom": "gb", "Canada": "ca", "Australia": "au"}
categories = ["general", "business", "entertainment", "health", "science", "sports", "technology"]

selected_country = st.sidebar.selectbox("Select a country:", list(countries.keys()))
selected_category = st.sidebar.selectbox("Select news category:", categories)
selected_date = st.sidebar.date_input("Select a date:", datetime.today() - timedelta(days=1))
selected_date = selected_date.strftime("%Y-%m-%d")

if st.sidebar.button("Get News Sentiments & Summaries"):
    articles = get_news(countries[selected_country], selected_category, selected_date)
    
    if not articles:
        st.warning("No news found. Try a different selection!")
    else:
        for index, article in enumerate(articles):
            st.subheader(article["title"])
            content = article.get("content", "") or article.get("description", "")
            
            # Sentiment Analysis
            sentiment = analyze_sentiment(content)
            st.write(f"**Sentiment:** {sentiment}")
            
            # Named Entity Recognition & Keywords Extraction
            entities, keywords = extract_entities_and_keywords(content)
            st.write("**Entities:**", ', '.join(entities))
            st.write("**Keywords:**", ', '.join(keywords))
            
            # Summarization
            st.write("### 📌 Summarized News")
            summary = summarize_text(content)
            st.success(summary)
            
            # Text-to-Speech
            audio_file = text_to_speech(summary, f"news_audio_{index}.mp3")
            st.audio(audio_file, format="audio/mp3")
            
            # Read Full News Link
            st.markdown(f"[Read Full News]({article['url']})")
