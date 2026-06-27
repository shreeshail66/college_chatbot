"""
chatbot.py
----------
This is the "brain" of the chatbot.

It works in 2 layers:

LAYER 1 (always works, 100% free, no internet needed):
    "Retrieval based" matching - it compares the student's question
    with every question stored in the knowledge_base table and
    returns the answer of the closest match, using TF-IDF + cosine
    similarity (a standard, beginner-friendly NLP technique).

LAYER 2 (optional, needs free API key):
    If LAYER 1 doesn't find a good enough match (similarity score is
    low), it can optionally call a FREE LLM API (Groq) to generate a
    more natural answer. This is OFF by default. To turn it on, see
    the README.md ("Optional AI / Free LLM API" section).
"""

import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import get_connection

# ---------------------------------------------------------------
# Set this to True and add your free Groq API key (see README) to
# enable smarter AI fallback answers. Leave False for a 100% free,
# offline-capable retrieval-only chatbot.
# ---------------------------------------------------------------
USE_LLM_FALLBACK = False
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")   # never hardcode your key here
GROQ_MODEL = "llama-3.1-8b-instant"
SIMILARITY_THRESHOLD = 0.25   # below this score -> fallback / "I don't know"


def get_knowledge_base():
    conn = get_connection()
    rows = conn.execute("SELECT question, answer FROM knowledge_base").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def retrieve_answer(user_question: str):
    """
    Compares user_question against every question in the knowledge base
    using TF-IDF + cosine similarity, and returns the best matching
    answer along with a similarity score (0 to 1).
    """
    kb = get_knowledge_base()
    if not kb:
        return None, 0.0

    questions = [item["question"] for item in kb]
    questions.append(user_question)  # add user question at the end

    vectorizer = TfidfVectorizer().fit_transform(questions)
    vectors = vectorizer.toarray()

    user_vector = vectors[-1]
    kb_vectors = vectors[:-1]

    scores = cosine_similarity([user_vector], kb_vectors)[0]
    best_index = scores.argmax()
    best_score = scores[best_index]

    return kb[best_index]["answer"], best_score


def call_groq_llm(user_question: str):
    """
    Optional fallback: calls the free Groq API (OpenAI-compatible)
    so the bot can still respond helpfully when nothing matches
    the knowledge base well. Returns None if not configured or
    if the request fails, so the app can fall back gracefully.
    """
    if not GROQ_API_KEY:
        return None

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": (
                        "You are a helpful assistant for a college chatbot. "
                        "Answer briefly and politely. If you are not sure, "
                        "tell the student to contact the college office."
                    )},
                    {"role": "user", "content": user_question},
                ],
                "temperature": 0.4,
                "max_tokens": 200,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Groq API error:", e)
        return None


def get_chatbot_response(user_question: str) -> str:
    """
    Main function called by app.py.
    1. Try retrieval from knowledge_base.
    2. If confidence is low and LLM fallback is enabled -> call Groq.
    3. Otherwise return a friendly "I don't know" message.
    """
    answer, score = retrieve_answer(user_question)

    if answer and score >= SIMILARITY_THRESHOLD:
        return answer

    if USE_LLM_FALLBACK:
        llm_answer = call_groq_llm(user_question)
        if llm_answer:
            return llm_answer

    return ("I'm not fully sure about that. Please rephrase your question, "
            "or contact the college office for more details.")
