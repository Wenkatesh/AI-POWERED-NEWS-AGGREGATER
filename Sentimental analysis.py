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
    
    return {"sentiment": sentiment, "entities": entities, "keywords": keywords}