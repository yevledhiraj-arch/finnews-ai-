import os
from typing import List, Optional
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

app = FastAPI(title='FinNews AI', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=False, allow_methods=['*'], allow_headers=['*'])

class Article(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    publishedAt: Optional[str] = None

class SimplifiedArticle(Article):
    summary: str


def fetch_news(query: str = 'finance OR stock market OR economy', page_size: int = 6) -> List[Article]:
    if not NEWS_API_KEY:
        raise HTTPException(500, 'NEWS_API_KEY is not configured')
    params = {
        'q': query,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': page_size,
        'apiKey': NEWS_API_KEY,
    }
    try:
        r = requests.get('https://newsapi.org/v2/everything', params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(502, f'NewsAPI request failed: {e}')
    if data.get('status') != 'ok':
        raise HTTPException(502, data.get('message', 'NewsAPI returned an error'))
    out = []
    for a in data.get('articles', []):
        if not a.get('title') or a.get('title') == '[Removed]':
            continue
        out.append(Article(title=a['title'], description=a.get('description'), content=a.get('content'), url=a.get('url'), source=(a.get('source') or {}).get('name'), publishedAt=a.get('publishedAt')))
    return out


def simplify(article: Article) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(500, 'GROQ_API_KEY is not configured')
    client = Groq(api_key=GROQ_API_KEY)
    text = f"Title: {article.title}\nDescription: {article.description or ''}\nContent: {article.content or ''}"
    prompt = f'''You are FinNews AI. Simplify the financial news below for a non-expert reader.
Rules:
- Preserve factual meaning; never invent facts.
- Explain financial jargon in simple language.
- Give 3 short sections: What happened, Why it matters, Key takeaway.
- Do not give personalized investment advice.
- Keep it concise (120-180 words).

NEWS:\n{text}'''
    try:
        result = client.chat.completions.create(model=GROQ_MODEL, messages=[{'role':'user','content':prompt}], temperature=0.2, max_tokens=350)
        return result.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(502, f'Groq processing failed: {e}')

@app.get('/health')
def health():
    return {'status': 'ok', 'news_api_configured': bool(NEWS_API_KEY), 'groq_configured': bool(GROQ_API_KEY), 'model': GROQ_MODEL}

@app.get('/api/news', response_model=List[Article])
def news(q: str = Query('finance OR stock market OR economy', min_length=2), limit: int = Query(6, ge=1, le=20)):
    return fetch_news(q, limit)

@app.get('/api/simplified', response_model=List[SimplifiedArticle])
def simplified(q: str = Query('finance OR stock market OR economy', min_length=2), limit: int = Query(5, ge=1, le=10)):
    articles = fetch_news(q, limit)
    return [SimplifiedArticle(**a.model_dump(), summary=simplify(a)) for a in articles]
