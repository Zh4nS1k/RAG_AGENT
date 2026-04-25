from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Добавляем путь к корню бэкенда, чтобы импорты работали
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.infrastructure.llm import get_embeddings, get_llm
from src.infrastructure.vector_store import VectorStoreManager
from src.application.rag_service import RAGService
from src.infrastructure.database import SessionLocal, get_db
from src.domain.models import Article, Chunk

app = FastAPI(title="RAG Agent API 🚀")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные сервисы
embeddings = get_embeddings()
vector_store = VectorStoreManager(
    embeddings, 
    collection_name="kazakhstan_codes_v4", 
    persist_directory="./chroma_db_v4"
)
llm = get_llm()
rag_service = RAGService(vector_store, llm)

# Модели Pydantic
class Query(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    source_url: str
    article_id: Optional[str]

class ChromaResponse(BaseModel):
    ids: List[str]
    metadatas: List[dict]
    documents: List[str]

@app.post("/chat", response_model=Answer)
async def chat(query: Query):
    try:
        answer = rag_service.answer_question(query.question)
        return Answer(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/articles", response_model=List[ArticleResponse])
async def get_articles(db=Depends(get_db)):
    articles = db.query(Article).limit(100).all()
    return [
        ArticleResponse(
            id=a.id,
            title=a.title,
            content=a.content,
            source_url=a.source_url,
            article_id=a.article_id
        ) for a in articles
    ]

@app.get("/db/vector", response_model=ChromaResponse)
async def get_vector_db():
    try:
        results = vector_store.vector_store.get(limit=50)
        return ChromaResponse(
            ids=results['ids'],
            metadatas=results['metadatas'],
            documents=results['documents']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
