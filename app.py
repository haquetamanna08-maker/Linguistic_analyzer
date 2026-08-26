from flask import Flask, render_template, request
from textblob import TextBlob
import textstat
import nltk

# Ensure NLTK packages are available in production environments
try:
    nltk.download('punkt', quiet=True)
except Exception:
    pass

app = Flask(__name__)

def analyze_marketing_copy(text, polarity, readability_score):
    words = text.strip().split()
    word_count = len(words)
    text_lower = text.lower()
    
    # 1. Edge-case detection: Low context or personal statements (e.g., "I am healthy")
    vague_starts = ["i am ", "you are ", "this is ", "it is ", "i feel "]
    is_vague = any(text_lower.startswith(phrase) for phrase in vague_starts) and word_count < 6

    if word_count < 4 or is_vague:
        return {
            'audience': "Low Context / Non-Marketing Copy ⚠️",
            'channel_tip': "This text is too short or personal to evaluate as commercial copy.",
            'tone': "Generic / Personal Statement 😐",
            'tone_tip': "Personal claims describe a state rather than a customer value proposition.",
            'cta_feedback': "Missing CTA. Convert personal claims into benefits (e.g., 'Discover 5 Secrets to Staying Healthy').",
            'word_count': word_count,
            'reading_time': "< 1 min"
        }

    # 2. Target Audience & Channel Recommendations
    if readability_score >= 80:
        audience = "General Public & Social Media (Instagram, TikTok, B2C Ads)"
        channel_tip = "Highly accessible copy with low cognitive friction. Perfect for quick scrolling."
    elif readability_score >= 60:
        audience = "Mainstream Web Readers (Blogs, Email Newsletters, Landing Pages)"
        channel_tip = "Balanced readability ideal for standard web campaigns and brand messaging."
    elif readability_score >= 40:
        audience = "Professional & Technical (B2B SaaS, In-depth Guides, Product Documentation)"
        channel_tip = "Suited for informed decision-makers, but simplify if targeting broad consumers."
    else:
        audience = "Niche Experts & Legal/Academic (Whitepapers, Compliance Docs)"
        channel_tip = "Dense structure. Consider shortening sentences for commercial audience engagement."

    # 3. Emotional Tone & Strategic Angle
    if polarity > 0.4:
        tone = "High Energy & Enthusiastic 🚀"
        tone_tip = "Great for product launches, special offers, and inspirational brand stories."
    elif polarity > 0.05:
        tone = "Warm & Encouraging 🙂"
        tone_tip = "Excellent for customer onboarding, service descriptions, and building trust."
    elif polarity >= -0.05:
        tone = "Objective & Informative 🎯"
        tone_tip = "Best for feature updates, case studies, and transparent pricing pages."
    else:
        tone = "Problem-Focused / Urgent ⚠️"
        tone_tip = "Effective for highlighting customer pain points, but follow up quickly with a solution."

    # 4. Actionability & CTA Detection
    action_words = ['get', 'start', 'buy', 'try', 'join', 'discover', 'learn', 'save', 'claim', 'download', 'subscribe', 'book']
    has_cta = any(word in text_lower for word in action_words)
    cta_feedback = "Strong call-to-action detected! 💪" if has_cta else "Consider adding an active CTA verb (e.g., 'Get', 'Start', 'Discover')."

    return {
        'audience': audience,
        'channel_tip': channel_tip,
        'tone': tone,
        'tone_tip': tone_tip,
        'cta_feedback': cta_feedback,
        'word_count': word_count,
        'reading_time': max(1, round(word_count / 200, 1))
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    original_text = ""

    if request.method == 'POST':
        original_text = request.form.get('content', '')
        if original_text.strip():
            blob = TextBlob(original_text)
            polarity = blob.sentiment.polarity
            readability_score = textstat.flesch_reading_ease(original_text)

            results = analyze_marketing_copy(original_text, polarity, readability_score)

    return render_template('index.html', original_text=original_text, results=results)

if __name__ == '__main__':
    app.run(debug=True)
