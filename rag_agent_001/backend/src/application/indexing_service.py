import uuid
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.domain.models import Article, Chunk
from src.infrastructure.database import SessionLocal, init_db
from src.utils.parser import parse_law_text
from src.utils.logger import setup_logger

logger = setup_logger("indexing_service", "logs/indexing.log")

class IndexingService:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            add_start_index=True
        )
        init_db()

    def index_documents_from_folder(self, folder_path):
        db = SessionLocal()
        try:
            files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
            logger.info(f"Found {len(files)} files to index in {folder_path}")

            for filename in files:
                file_path = os.path.join(folder_path, filename)
                logger.info(f"📂 Обработка файла: {filename}...")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                    
                    docs = parse_law_text(text, filename)
                    logger.info(f"📑 Распознано {len(docs)} статей в {filename}")

                    for doc in docs:
                        # 1. Save to Postgres
                        db_article = Article(
                            title=doc.metadata["title"],
                            content=doc.page_content,
                            source_url=filename,
                            article_id=doc.metadata["article_id"],
                            meta_info=doc.metadata
                        )
                        db.add(db_article)
                        db.commit()
                        db.refresh(db_article)

                        # 2. Split into chunks
                        splits = self.text_splitter.split_documents([doc])
                        
                        for i, split in enumerate(splits):
                            chroma_id = str(uuid.uuid4())
                            split.metadata["postgres_article_id"] = db_article.id
                            split.metadata["chunk_index"] = i
                            
                            # 3. Add to Chroma
                            self.vector_store.add_documents([split], ids=[chroma_id])
                            
                            # 4. Save Chunk to Postgres
                            db_chunk = Chunk(
                                article_id=db_article.id,
                                chunk_index=i,
                                chroma_id=chroma_id
                            )
                            db.add(db_chunk)
                        
                        db.commit()
                        logger.debug(f"✅ Статья '{db_article.title}' успешно проиндексирована ({len(splits)} чанков)")
                except Exception as file_e:
                    logger.error(f"❌ Ошибка при обработке файла {filename}: {file_e}")
                    db.rollback()
                    continue

            logger.info("🎉 Индексация успешно завершена!")
        except Exception as e:
            logger.error(f"Error during indexing: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()
