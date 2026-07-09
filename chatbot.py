"""
chatbot.py
----------
This is the "brain" of the chatbot.
"""

import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import get_connection

USE_LLM_FALLBACK = False
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"
SIMILARITY_THRESHOLD = 0.25


def get_knowledge_base():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM knowledge_base")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def retrieve_answer(user_question: str):
    kb = get_knowledge_base()
    if not kb:
        return None, 0.0

    questions = [item["question"] for item in kb]
    questions.append(user_question)

    vectorizer = TfidfVectorizer().fit_transform(questions)
    vectors = vectorizer.toarray()

    user_vector = vectors[-1]
    kb_vectors = vectors[:-1]

    scores = cosine_similarity([user_vector], kb_vectors)[0]
    best_index = scores.argmax()
    best_score = scores[best_index]

    return kb[best_index]["answer"], best_score


def call_groq_llm(user_question: str):
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
    answer, score = retrieve_answer(user_question)

    if answer and score >= SIMILARITY_THRESHOLD:
        return answer

    if USE_LLM_FALLBACK:
        llm_answer = call_groq_llm(user_question)
        if llm_answer:
            return llm_answer

    return ("I'm not fully sure about that. Please rephrase your question, "
            "or contact the college office for more details.")