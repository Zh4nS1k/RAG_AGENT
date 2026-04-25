from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    source_url = Column(String)
    article_id = Column(String) # ID from the site or file (e.g. 'Статья 1')
    meta_info = Column(JSON) # To store additional metadata
    
    chunks = relationship("Chunk", back_populates="article", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    chunk_index = Column(Integer)
    chroma_id = Column(String) # UUID used in ChromaDB
    
    article = relationship("Article", back_populates="chunks")
