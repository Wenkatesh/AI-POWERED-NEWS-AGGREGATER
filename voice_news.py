import streamlit as st
import requests
import spacy
import google.generativeai as genai
from textblob import TextBlob
from datetime import datetime, timedelta
from gtts import gTTS
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyCn5TSbk7SYU1b1ADykXYvI02xzdVZyd48")

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def process_news_content(text):
    """Perform NLP processing: sentiment analysis, NER, and keyword extraction."""
    if not text:
        return {"sentiment": "Neutral", "entities": [], "keywords": []}
    
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    keywords = [chunk.text for chunk in doc.noun_chunks]
    sentiment_score = TextBlob(text).sentiment.polarity
    sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
    
    return {"sentiment": sentiment, "entities": entities, "keywords": keywords}

def summarize_with_gemini(text):
    """Summarize news using Gemini API."""
    if not text:
        return "No content available to summarize."
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Summarize in 8-10 lines: {text[:3000]}")
        return response.text.strip() if response and response.text else "Failed to summarize."
    except Exception as e:
        return f"Summarization failed: {str(e)}"

def generate_speech(text, filename="news_audio.mp3"):
    """Convert text to speech and save as an audio file."""
    tts = gTTS(text=text, lang="en")
    tts.save(filename)
    return filename

def ask_news_ai(query, news_context):
    """Uses Gemini API to answer questions based on the latest news."""
    if not news_context:
        return "No news available for context."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Based on the latest news:\n\nContext: {news_context}\n\nQuestion: {query}\n\nAnswer concisely.")
        return response.text.strip() if response and response.text else "AI could not generate a response."
    except Exception as e:
        return f"AI failed to generate a response: {str(e)}"

def get_news_by_country_category_date(country, category, keyword, date):
    """Fetch news based on country, category, keyword, and date using Mediastack API."""
    MEDIASTACK_API_KEY = "46dbbb88980aabc6699a72e1be8c6ffb"
    url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&countries={country}&categories={category}&keywords={keyword}&date={date}&limit=15"
    response = requests.get(url)
    news_data = response.json()
    return news_data.get("data", [])

# List of major countries
countries = {"United States": "us", "India": "in", "United Kingdom": "gb", "Canada": "ca", "Australia": "au", "None": ""}

# News categories
categories = ["general", "business", "entertainment", "health", "science", "sports", "technology", "politics", "world", "environment", "None"]

# Streamlit UI
st.title("🤖 AI-Powered News Aggregator with Voice 🗣️")
st.sidebar.header("Select News Preferences")

selected_country = st.sidebar.selectbox("Select a country for top news:", list(countries.keys()))
selected_category = st.sidebar.selectbox("Select news category:", categories)
selected_date = st.sidebar.date_input("Select a date for news:", datetime.today() - timedelta(days=1), min_value=datetime(2000, 1, 1), max_value=datetime.today() - timedelta(days=1))
selected_date = selected_date.strftime("%Y-%m-%d")

if st.sidebar.button("Get News"):
    country_code = countries[selected_country]
    category_code = selected_category if selected_category != "None" else ""
    articles = get_news_by_country_category_date(country_code, category_code, "", selected_date)

    if not articles:
        st.warning("No news found. Try a different country, category, or date!")
    else:
        for index, article in enumerate(articles):
            st.subheader(article["title"])
            st.write(f"**Source:** {article['source']}")
            st.write(f"**Published At:** {article['published_at']}")

            # NLP Processing
            nlp_results = process_news_content(article.get("content", "") or article.get("description", ""))
            st.write(f"**Sentiment:** {nlp_results['sentiment']}")
            st.write(f"**Entities:** {nlp_results['entities']}")
            st.write(f"**Keywords:** {', '.join(nlp_results['keywords'])}")

            # Summarization using Gemini API
            st.write("### 📌 Summarized News")
            summary_text = summarize_with_gemini(article.get("content", "") or article.get("description", ""))
            st.success(summary_text)

            # Generate and play speech
            audio_file = generate_speech(summary_text, f"news_audio_{index}.mp3")
            st.audio(audio_file, format="audio/mp3")

            st.markdown(f"[Read Full News]({article['url']})")

# AI Chatbot for News Queries
st.sidebar.subheader("Ask AI about News")
user_query = st.sidebar.text_area("Ask a question about recent news:")

if st.sidebar.button("Ask AI"):
    articles = get_news_by_country_category_date(countries[selected_country], selected_category, "", selected_date)
    
    if not articles:
        st.sidebar.warning("No news available. Fetch news first!")
    else:
        news_context = " ".join([article["title"] + ". " + article.get("description", "") for article in articles[:10]])  # Limit context size
        response = ask_news_ai(user_query, news_context)
        st.sidebar.write("AI Response:", response)
