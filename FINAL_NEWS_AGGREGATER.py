import streamlit as st
import requests
import spacy
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from textblob import TextBlob
from datetime import datetime, timedelta
from gtts import gTTS
from googletrans import Translator
import os

# Configure Gemini API (via LangChain)
GEMINI_API_KEY = "YOUR_API"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize LangChain's Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

# Conversation Memory for Chatbot
memory = ConversationBufferMemory()
chat_chain = ConversationChain(llm=llm, memory=memory)

# Define Summarization Chain Using LangChain
summarization_prompt = PromptTemplate(
    input_variables=["news_content"],
    template="Summarize the following news article in 8-10 lines:\n{news_content}"
)
summarization_chain = LLMChain(llm=llm, prompt=summarization_prompt)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")
translator = Translator()

# Mediastack API Key
MEDIASTACK_API_KEY = "YOUR_API"

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

def summarize_with_langchain(text):
    """Summarize news using LangChain's LLMChain with Gemini."""
    if not text:
        return "No content available to summarize."
    
    try:
        response = summarization_chain.run(news_content=text[:3000])
        return response.strip() if response else "Failed to summarize."
    except Exception as e:
        return f"Summarization failed: {str(e)}"

def chat_with_langchain(query):
    """Generates a response using LangChain's ConversationChain."""
    try:
        response = chat_chain.predict(input=query)
        return response.strip() if response else "Failed to generate a response."
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
st.title("🤖 AI-Powered News Aggregator 📰🗣️")
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
            summary_text = summarize_with_langchain(article.get("content", "") or article.get("description", ""))
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
        ai_response = chat_with_langchain(user_query)
        st.sidebar.write("### 🤖 AI Response")
        st.sidebar.success(ai_response)
    else:
        st.sidebar.warning("Please enter a question.")

