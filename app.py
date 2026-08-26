import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from flask import Flask, render_template, request
from textblob import TextBlob
import textstat

app = Flask(__name__)

def get_sentiment_comment(polarity):
    if polarity > 0.1:
        return "Positive Tone"
    elif polarity < -0.1:
        return "Negative Tone"
    else:
        return "Neutral / Objective Tone"

def get_subjectivity_comment(subj):
    if subj > 0.5:
        return "Opinion-Based / Subjective"
    else:
        return "Fact-Based / Objective"

def get_readability_comment(score):
    if score >= 70:
        return "Easy to Read (General Public)"
    elif score >= 50:
        return "Fairly Readable (Standard)"
    elif score >= 30:
        return "Difficult (Academic / Technical)"
    else:
        return "Very Hard / Complex Structure"

@app.route('/', methods=['GET', 'POST'])
def home():
    analysis = None
    if request.method == 'POST':
        text = request.form['marketing_text']
        blob = TextBlob(text)
        
        polarity_val = round(blob.sentiment.polarity, 2)
        subjectivity_val = round(blob.sentiment.subjectivity, 2)
        readability_val = textstat.flesch_reading_ease(text)
        word_count = len(blob.words)
        
        analysis = {
            'text': text,
            'word_count': word_count,
            'polarity': f"{polarity_val} ({get_sentiment_comment(polarity_val)})",
            'subjectivity': f"{subjectivity_val} ({get_subjectivity_comment(subjectivity_val)})",
            'readability': f"{round(readability_val, 2)} - {get_readability_comment(readability_val)}"
        }
    return render_template('index.html', result=analysis)

if __name__ == '__main__':
    app.run(debug=True)
