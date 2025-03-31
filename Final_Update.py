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
genai.configure(api_key="AIzaSyA_4osQoZxBdNdDrZ4RXPkhmoVGr4kB8ic")

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")
translator = Translator()

# Mediastack API Key
MEDIASTACK_API_KEY = "9f9d26568717f598067ae30d5a2e0d60"

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

def chat_with_gemini(query):
    """Generates a response using Gemini 1.5 Flash API as a general chatbot."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(query)
        return response.text.strip() if response and response.text else "Failed to generate a response."
    except Exception as e:
        return f"Error: {str(e)}"

def translate_text(text, target_lang):
    """Translate text to the selected language."""
    if not text:
        return ""
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        return f"Translation failed: {str(e)}"

def generate_speech(text, filename="news_audio.mp3", lang="en"):
    """Convert text to speech and save as an audio file."""
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename

def get_news_by_country_category_date(country, category, keyword, date):
    """Fetch news based on country, category, keyword, and date using Mediastack API."""
    url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&countries={country}&categories={category}&keywords={keyword}&date={date}&limit=15"
    response = requests.get(url)
    news_data = response.json()
    return news_data.get("data", [])

# Language Mapping
languages = {"English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "French": "fr", "Spanish": "es", "Chinese": "zh-cn", "German": "de", "Japanese": "ja", "Russian": "ru"}

# Streamlit UI
st.title("🤖 AI-Powered News Aggregator with Voice 🌍🗣️")
st.subheader("Stay updated with the latest news & chat with AI about current events")

# Sidebar - News Selection
st.sidebar.header("Select News Preferences")
countries = {"United States": "us", "India": "in", "United Kingdom": "gb", "Canada": "ca", "Australia": "au", "None": ""}
categories = ["general", "business", "entertainment", "health", "science", "sports", "technology", "politics", "world", "environment", "None"]

selected_country = st.sidebar.selectbox("Select a country for top news:", list(countries.keys()))
selected_category = st.sidebar.selectbox("Select news category:", categories)
selected_date = st.sidebar.date_input("Select a date for news:", datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
selected_language = st.sidebar.selectbox("Select Language:", list(languages.keys()))

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

            nlp_results = process_news_content(article.get("content", "") or article.get("description", ""))
            st.write(f"**Sentiment:** {nlp_results['sentiment']}")
            st.write(f"**Entities:** {nlp_results['entities']}")
            st.write(f"**Keywords:** {', '.join(nlp_results['keywords'])}")

            st.write("### 📌 Summarized News")
            summary_text = summarize_with_gemini(article.get("content", "") or article.get("description", ""))
            translated_summary = translate_text(summary_text, languages[selected_language])
            st.success(translated_summary)
            
            audio_file = generate_speech(translated_summary, f"news_audio_{index}.mp3", languages[selected_language])
            st.audio(audio_file, format="audio/mp3")

            st.markdown(f"[Read Full News]({article['url']})")

# Sidebar - Chatbot (Moved to Bottom)
st.sidebar.header("AI Chatbot")
user_query = st.sidebar.text_area("Ask AI about any topic:")
if st.sidebar.button("Ask AI"):
    if user_query.strip():
        ai_response = chat_with_gemini(user_query)
        st.sidebar.write("### 🤖 AI Response")
        st.sidebar.success(ai_response)
    else:
        st.sidebar.warning("Please enter a question.")

