# 🎓 AI Chatbot for College — Final Year Project

A complete, working web app built with **Python (Flask)** + **HTML/CSS/JS** + **SQLite**.

Features included:
- ✅ Student login
- ✅ Ask questions about the college (retrieval-based chatbot)
- ✅ Timetable
- ✅ Faculty information
- ✅ Attendance information
- ✅ FAQs
- ✅ Admin panel to update chatbot knowledge
- ✅ Optional: free LLM API fallback (Groq) for smarter answers

No payment needed anywhere. Everything here is free.

---

## 1. What you need to install

You only need **Python 3.9+** installed on your laptop.
Check: open Command Prompt / Terminal and type:
```
python --version
```
If it's not installed, download from https://www.python.org/downloads/ (tick
"Add Python to PATH" during install on Windows).

---

## 2. Step-by-step setup

### Step 1 — Open the project folder
Unzip the project, then open a terminal inside the `college_chatbot` folder.

### Step 2 — (Recommended) Create a virtual environment
```
python -m venv venv
```
Activate it:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

### Step 3 — Install the required packages
```
pip install -r requirements.txt
```
This installs:
- **Flask** – the web framework that runs your app and pages
- **scikit-learn** – does the TF-IDF text-matching for the chatbot
- **requests** – only needed if you turn on the optional LLM API

### Step 4 — Create the database
```
python database.py
```
This creates `college.db` (SQLite file) and fills it with demo data:
- Demo student login → roll no `101`, password `1234`
- Demo admin login → username `admin`, password `admin123`

### Step 5 — Run the app
```
python app.py
```
You'll see something like:
```
* Running on http://127.0.0.1:5000
```
Open that link in your browser. Login as the demo student and start chatting!

To access the admin panel, go to: `http://127.0.0.1:5000/admin/login`

---

## 3. How the chatbot works (no API needed)

The chatbot is **retrieval-based**:
1. All Q&A pairs live in the `knowledge_base` table (FAQs, fees, admission, etc.)
2. When a student types a question, the app converts every stored question
   AND the new question into TF-IDF vectors (a way of turning text into
   numbers based on word importance).
3. It compares the new question to every stored one using **cosine
   similarity** and picks the closest match.
4. If nothing matches well, it shows a polite "I'm not sure" message
   (or calls a free LLM, see below).

This is explained in `chatbot.py` with comments — read through it, it's
good to understand for your project viva/demo.

The **admin** can add, view or delete knowledge base entries at
`/admin` — anything added there is immediately searchable by the chatbot.

---

## 4. Optional AI — adding a free LLM API (for smarter answers)

By default `USE_LLM_FALLBACK = False` in `chatbot.py`, so the project works
100% offline with no API key. If you want it to also answer questions that
AREN'T in the knowledge base (using a real LLM), follow these steps:

### Option A: Groq (recommended — fast & free)
1. Go to https://console.groq.com/ and sign up (free, no credit card).
2. Go to **API Keys** → **Create API Key** → copy it.
3. In your terminal (inside the project folder), set the key as an
   environment variable:
   - Windows (Command Prompt): `set GROQ_API_KEY=your_key_here`
   - Windows (PowerShell): `$env:GROQ_API_KEY="your_key_here"`
   - Mac/Linux: `export GROQ_API_KEY=your_key_here`
4. Open `chatbot.py` and change:
   ```python
   USE_LLM_FALLBACK = True
   ```
5. Run `python app.py` again. Now, if the chatbot can't find a good match
   in the knowledge base, it will ask Groq's LLM (`llama-3.1-8b-instant`,
   free tier) for an answer.

### Option B: Google Gemini API (also free tier)
1. Go to https://aistudio.google.com/apikey and generate a free API key.
2. The request format is slightly different from Groq's. If you'd like,
   I can give you a ready-made `call_gemini_llm()` function to drop into
   `chatbot.py` instead of `call_groq_llm()` — just ask.

> Note: Free tiers have rate limits (e.g. a certain number of requests per
> minute/day). That's normal and fine for a college project demo.

---

## 5. Project structure
```
college_chatbot/
│
├── app.py              -> Flask routes (all pages/logic)
├── chatbot.py           -> Chatbot matching logic (TF-IDF + optional LLM)
├── database.py          -> Creates & seeds the SQLite database
├── requirements.txt      -> Python packages needed
├── college.db            -> SQLite database (created after step 4)
│
├── templates/            -> HTML pages (Jinja2 templates)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html (chat page)
│   ├── timetable.html
│   ├── faculty.html
│   ├── attendance.html
│   ├── faqs.html
│   ├── admin_login.html
│   └── admin_dashboard.html
│
└── static/
    ├── style.css
    └── chat.js
```

---

## 6. How to customize for YOUR college

- **Add real students** → edit the `seed_data()` function in `database.py`,
  or build a simple `/register` form (ask me if you want this added).
- **Add real faculty/timetable/attendance** → same idea, edit `seed_data()`,
  or add them through a future admin form (currently admin can only manage
  the chatbot's knowledge base — ask me if you want full CRUD for faculty/
  timetable/attendance too, it's a small addition).
- **Change colors/branding** → edit `static/style.css`.
- **Deploy online** (so it's not just on your laptop) → can be deployed for
  free on Render.com or PythonAnywhere. Ask me and I'll give you those steps.

---

## 7. For your project report / viva

Good points to mention:
- Retrieval-based chatbot using **TF-IDF vectorization** and **cosine
  similarity** (classic NLP technique, explainable, no black-box risk).
- Optional integration point for a **generative LLM (Groq/Gemini)** shows
  awareness of modern AI architecture (hybrid retrieval + generation).
- Clean separation of concerns: `database.py` (data), `chatbot.py` (AI
  logic), `app.py` (web routes/controller), `templates/` (views) — this is
  the MVC pattern.
- Admin panel demonstrates a real-world **CMS-style knowledge update
  system**, so the bot can be kept up to date without redeploying code.

Good luck with your project! 🎉
