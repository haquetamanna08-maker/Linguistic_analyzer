import re
from flask import Flask, render_template, request
from textblob import TextBlob
import textstat
from langdetect import detect, DetectorFactory
from spellchecker import SpellChecker

DetectorFactory.seed = 0

app = Flask(__name__)

def analyze_marketing_copy(text, polarity, readability_score):
    words = text.strip().split()
    word_count = len(words)
    text_lower = text.lower()
    spell = SpellChecker()

    # 1. Language Detection Check
    try:
        lang = detect(text)
        if lang != 'en':
            return {
                'audience': "Unsupported Language 🌐",
                'channel_tip': "This analyzer currently supports English text only.",
                'tone': "Language Not Recognized ⚠️",
                'tone_tip': f"Detected non-English script/language code ('{lang}').",
                'cta_feedback': "Please input your marketing copy in English.",
                'word_count': word_count,
                'reading_time': "< 1 min",
                'spelling_feedback': "N/A",
                'sentence_length_feedback': "N/A"
            }
    except Exception:
        pass

    # 2. Edge-case detection: Short/vague personal statements
    vague_starts = ["i am ", "you are ", "this is ", "it is ", "i feel "]
    is_vague = any(text_lower.startswith(phrase) for phrase in vague_starts) and word_count < 6

    if word_count < 4 or is_vague:
        return {
            'audience': "Low Context / Non-Marketing Copy ⚠️",
            'channel_tip': "This text is too short or personal to evaluate as commercial copy.",
            'tone': "Generic / Personal Statement 😐",
            'tone_tip': "Personal claims describe a state rather than a customer value proposition.",
            'cta_feedback': "Missing CTA. Convert personal claims into benefits.",
            'word_count': word_count,
            'reading_time': "< 1 min",
            'spelling_feedback': "Text too short to check.",
            'sentence_length_feedback': "Text too short to evaluate sentence length."
        }

    # 3. Target Audience & Channel Recommendations
    if readability_score >= 80:
        audience = "General Public & Social Media (Instagram, TikTok, B2C Ads)"
        channel_tip = "Highly accessible copy with low cognitive friction."
    elif readability_score >= 60:
        audience = "Mainstream Web Readers (Blogs, Email Newsletters, Landing Pages)"
        channel_tip = "Balanced readability ideal for standard web campaigns."
    elif readability_score >= 40:
        audience = "Professional & Technical (B2B SaaS, In-depth Guides)"
        channel_tip = "Suited for informed decision-makers."
    else:
        audience = "Niche Experts & Legal/Academic (Whitepapers, Compliance Docs)"
        channel_tip = "Dense structure. Simplify for commercial engagement."

    # 4. Tone Analysis
    if polarity > 0.4:
        tone = "High Energy & Enthusiastic 🚀"
        tone_tip = "Great for product launches and promotional sales."
    elif polarity > 0.05:
        tone = "Warm & Encouraging 🙂"
        tone_tip = "Excellent for customer onboarding and trust building."
    elif polarity >= -0.05:
        tone = "Objective & Informative 🎯"
        tone_tip = "Best for feature updates and pricing pages."
    else:
        tone = "Problem-Focused / Urgent ⚠️"
        tone_tip = "Effective for highlighting customer pain points."

    # 5. CTA Verification
    action_words = ['get', 'start', 'buy', 'try', 'join', 'discover', 'learn', 'save', 'claim', 'download']
    has_cta = any(word in text_lower for word in action_words)
    cta_feedback = "Strong call-to-action detected! 💪" if has_cta else "Consider adding an active CTA verb."

    # 6. Detailed Spelling & Typo Check
    clean_words = [word.strip(".,!?\"'()[]") for word in words]
    misspelled = list(spell.unknown([w for w in clean_words if w.isalpha()]))
    
    if len(misspelled) == 0:
        spelling_feedback = "No spelling errors detected! ✨"
    else:
        details = []
        for word in misspelled:
            correction = spell.correction(word)
            if correction and correction != word:
                details.append(f"<span style='color: #dc2626; font-weight: 700;'>{word}</span> → <i style='color: #16a34a;'>{correction}</i>")
            else:
                details.append(f"<span style='color: #dc2626; font-weight: 700;'>{word}</span>")
        
        spelling_feedback = f"Found {len(misspelled)} typo(s):<br>" + "<br>".join(details)

    # 7. Sentence Length Verification (Target: 10 - 20 words per sentence)
    clean_text = text.strip()
    sentences = [s.strip() for s in re.split(r'[.!?]+(?=\s|$)', clean_text) if s.strip()]
    sentence_count = max(len(sentences), 1)
    avg_words_per_sent = round(word_count / sentence_count, 1)

    if 10 <= avg_words_per_sent <= 20:
        sentence_length_feedback = f"Optimal length ({avg_words_per_sent} words/sentence). Fits the target 10–20 range! ✅"
    elif avg_words_per_sent < 10:
        sentence_length_feedback = f"Sentences are too short (avg {avg_words_per_sent} words). Aim for 10–20 words per sentence for ideal pacing."
    else:
        sentence_length_feedback = f"Sentences are too long (avg {avg_words_per_sent} words). Breakdown sentences to fit the target 10–20 range."

    return {
        'audience': audience,
        'channel_tip': channel_tip,
        'tone': tone,
        'tone_tip': tone_tip,
        'cta_feedback': cta_feedback,
        'word_count': word_count,
        'reading_time': max(1, round(word_count / 200, 1)),
        'spelling_feedback': spelling_feedback,
        'sentence_length_feedback': sentence_length_feedback
    }

@app.route('/', methods=['GET', 'POST'])
def home():
    analysis = None
    text_input = ""
    
    if request.method == 'POST':
        text_input = request.form.get('marketing_text', '')
        if text_input.strip():
            blob = TextBlob(text_input)
            polarity = blob.sentiment.polarity
            readability_score = textstat.flesch_reading_ease(text_input)
            analysis = analyze_marketing_copy(text_input, polarity, readability_score)
            
    return render_template('index.html', analysis=analysis, text_input=text_input)

if __name__ == '__main__':
    app.run(debug=True)
