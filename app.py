from flask import Flask, render_template, request
from textblob import TextBlob
import textstat
import nltk

# Ensure NLTK packages are available
nltk.download('punkt')

app = Flask(__name__)

def get_sentiment_label(polarity):
    if polarity > 0.5:
        return "Very Positive 😄", "Great energy! Your copy feels optimistic and upbeat."
    elif polarity > 0.1:
        return "Slightly Positive 🙂", "Friendly tone, encouraging for readers."
    elif polarity >= -0.1:
        return "Neutral 😐", "Clear and direct tone, perfect for informative or formal copy."
    elif polarity >= -0.5:
        return "Slightly Negative 🙁", "A bit cautious or problem-focused."
    else:
        return "Very Negative 😟", "Strongly negative tone. Good for highlighting problems, but ensure it balances out."

def get_readability_label(score):
    if score >= 90:
        return "Very Easy 🟢", "5th Grade Level — Effortless to read for anyone."
    elif score >= 70:
        return "Easy 🟢", "7th Grade Level — Clear and conversational for general audiences."
    elif score >= 60:
        return "Standard / Balanced 🟡", "8th–9th Grade Level — Ideal for most web content and marketing copy."
    elif score >= 50:
        return "Fairly Difficult 🟧", "High School Level — Concise, but contains longer words or sentences."
    else:
        return "Complex / Technical 🔴", "College Level — Might feel dense or hard for quick reading."

@app.route('/', methods=['GET', 'POST'])
def index():
    sentiment_label = None
    sentiment_tip = None
    readability_label = None
    readability_tip = None
    original_text = ""

    if request.method == 'POST':
        original_text = request.form.get('content', '')
        if original_text.strip():
            blob = TextBlob(original_text)
            polarity = blob.sentiment.polarity
            readability_score = textstat.flesch_reading_ease(original_text)

            sentiment_label, sentiment_tip = get_sentiment_label(polarity)
            readability_label, readability_tip = get_readability_label(readability_score)

    return render_template(
        'index.html',
        original_text=original_text,
        sentiment_label=sentiment_label,
        sentiment_tip=sentiment_tip,
        readability_label=readability_label,
        readability_tip=readability_tip
    )

if __name__ == '__main__':
    app.run(debug=True)
