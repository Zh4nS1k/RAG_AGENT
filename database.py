from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql://user:password@localhost:5432/rag_db"

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    source_url = Column(String)
    article_id = Column(String) # ID from the site (e.g. 'z18')
    meta_info = Column(JSON) # To store additional metadata
    
    chunks = relationship("Chunk", back_populates="article", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    chunk_index = Column(Integer)
    chroma_id = Column(String) # UUID used in ChromaDB
    
    article = relationship("Article", back_populates="chunks")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
