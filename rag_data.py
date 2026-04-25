from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import bs4
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import urllib3
import uuid
from database import init_db, SessionLocal, Article, Chunk

import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("indexing.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Postgres Database
init_db()

# 1. Custom Parser for Adilet
def parse_adilet_html(html_content, url):
    soup = bs4.BeautifulSoup(html_content, "html.parser")
    article_tag = soup.find("article")
    if not article_tag:
        return [Document(page_content=soup.get_text(), metadata={"source": url})]

    documents = []
    current_title = "Преамбула"
    current_id = ""
    current_content = []

    # Iterate through elements in article
    for element in article_tag.find_all(['h3', 'p']):
        if element.name == 'h3':
            # If we have content from previous section, save it
            if current_content:
                text = "\n".join(current_content)
                documents.append(Document(
                    page_content=f"{current_title}\n{text}",
                    metadata={
                        "source": url,
                        "title": current_title,
                        "article_id": current_id,
                        "link": f"{url}#{current_id}" if current_id else url
                    }
                ))
                current_content = []

            current_title = element.get_text().strip()
            current_id = element.get('id', '')
        elif element.name == 'p':
            # Handle notes and subpoints
            p_text = element.get_text().strip()
            if p_text:
                current_content.append(p_text)

    # Save the last section
    if current_content:
        text = "\n".join(current_content)
        documents.append(Document(
            page_content=f"{current_title}\n{text}",
            metadata={
                "source": url,
                "title": current_title,
                "article_id": current_id,
                "link": f"{url}#{current_id}" if current_id else url
            }
        ))

    return documents

# 2. Loading and Processing
web_paths = (
    "https://adilet.zan.kz/rus/docs/K2600000000",
    "https://adilet.zan.kz/rus/docs/K1500000414",
)

# 4. Embeddings
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

# 5. Vector Store
vector_store = Chroma(
    collection_name="kazakhstan_codes_v3",
    embedding_function=embeddings,
    persist_directory="./chroma_db_v3",
)

# Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    add_start_index=True
)

db = SessionLocal()

try:
    for url in web_paths:
        try:
            logger.info(f"Загрузка URL: {url}...")
            response = requests.get(url, verify=False, timeout=30)
            response.encoding = 'utf-8'
            docs = parse_adilet_html(response.text, url)
            logger.info(f"Найдено статей/разделов для индексации: {len(docs)}")
            
            for doc in docs:
                # 1. Save Full Article to Postgres
                logger.info(f"  Сохранение в PostgreSQL: {doc.metadata['title']}")
                db_article = Article(
                    title=doc.metadata["title"],
                    content=doc.page_content,
                    source_url=url,
                    article_id=doc.metadata["article_id"],
                    meta_info=doc.metadata
                )
                db.add(db_article)
                db.commit()
                db.refresh(db_article)
                
                # 2. Split Article into Chunks
                splits = text_splitter.split_documents([doc])
                logger.info(f"    Статья разбита на {len(splits)} чанков.")
                
                for i, split in enumerate(splits):
                    chroma_id = str(uuid.uuid4())
                    # Add metadata linking to Postgres
                    split.metadata["postgres_article_id"] = db_article.id
                    split.metadata["chunk_index"] = i
                    
                    # 3. Add to Chroma
                    logger.info(f"      Добавление чанка #{i} в ChromaDB (ID: {chroma_id})...")
                    vector_store.add_documents([split], ids=[chroma_id])
                    
                    # 4. Save Chunk info to Postgres
                    db_chunk = Chunk(
                        article_id=db_article.id,
                        chunk_index=i,
                        chroma_id=chroma_id
                    )
                    db.add(db_chunk)
                
                db.commit()
                logger.info(f"  Статья '{doc.metadata['title']}' полностью обработана.")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке {url}: {e}", exc_info=True)
            db.rollback()

finally:
    db.close()

logger.info("Индексация завершена.")
