# FinNews AI – Financial News Simplifier

A full-stack educational project that retrieves recent financial news with NewsAPI and simplifies it with Groq's LLM through a FastAPI backend. The browser UI is plain HTML/CSS/JavaScript.

## Architecture
Browser -> FastAPI -> NewsAPI -> financial articles -> Groq LLM -> simplified summaries -> Browser

## Features
- Search/fetch current financial, market, economic, and business news
- Multi-article processing
- LLM-generated jargon-free summaries
- Source metadata and original article links
- `/health`, `/api/news`, `/api/simplified` REST endpoints
- CORS, environment-variable API keys, validation and error handling
- Responsive frontend
- Prompt explicitly avoids invented facts and personalized investment advice

## Setup
1. Install Python 3.8+ and open the project in VS Code.
2. In a terminal:

```bash
cd backend
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and add your own NewsAPI and Groq API keys. Never put real API keys in GitHub.

5. Start backend:
```bash
uvicorn main:app --reload
```
Expected backend: `http://127.0.0.1:8000`; API docs: `/docs`; health check: `/health`.

6. In another terminal serve the frontend:
```bash
cd frontend
python -m http.server 5500
```
Then open `http://127.0.0.1:5500`.

## API flow
When the user clicks **Fetch & Simplify**, JavaScript calls `/api/simplified`. FastAPI calls NewsAPI, converts results into structured Article objects, then sends each article's title/description/content to Groq. The prompt asks the model for `What happened`, `Why it matters`, and `Key takeaway`. The backend returns JSON and JavaScript renders cards.

## Important limitation
NewsAPI often provides only a description/truncated content depending on plan/source. Therefore this version summarizes only the text legally returned by the API; it does not scrape paywalled/full articles. LLM output should be treated as a simplification aid, not as financial advice.

## Suggested testing
- Open `/health`: status should be `ok` and both API configured fields should be true.
- Open `/docs` and test `/api/news` first.
- Test `/api/simplified` with `inflation`, `stock market`, or `interest rates`.
- Remove one key temporarily to verify error handling.
- Test UI on narrow/mobile browser width.

## Hinglish Summary
FinNews AI ka main kaam complex financial news ko simple language me convert karna hai. User **Fetch & Simplify** button click karta hai. Frontend request FastAPI backend ko bhejta hai. Backend NewsAPI se latest articles fetch karta hai. Uske baad article ka title, description aur available content Groq ke LLM ko diya jata hai. LLM us news ko teen simple parts me explain karta hai: **What happened**, **Why it matters**, aur **Key takeaway**. Final summary browser me card ke form me show hoti hai.

`NEWS_API_KEY` aur `GROQ_API_KEY` `.env` file me rakhe jate hain, isliye keys frontend me expose nahi hoti. CORS frontend aur backend ko communicate karne deta hai. Error handling API failure ya missing key ko clear error me convert karti hai. `/health` endpoint se backend aur configuration check ki ja sakti hai.

Viva ke liye flow yaad rakho: **User -> HTML/JS -> FastAPI -> NewsAPI -> Article -> Groq LLM -> Simplified Summary -> FastAPI JSON -> Browser UI**.
