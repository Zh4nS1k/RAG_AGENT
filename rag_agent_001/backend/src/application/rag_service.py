from langchain_core.prompts import ChatPromptTemplate
from src.infrastructure.database import SessionLocal
from src.domain.models import Article
from src.utils.logger import setup_logger

logger = setup_logger("rag_service", "logs/rag_agent.log")

class RAGService:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm
        self.prompt_template = ChatPromptTemplate.from_template("""
Вы — эксперт-юрист по законодательству Республики Казахстан. 
Используйте только предоставленный контекст для ответа на вопрос. 

Если в контексте нет прямого ответа, скажите: "В базе данных законов РК не найдена информация по этому вопросу". Не выдумывайте нормы.

Структура ответа:
1. Ссылка на статью: [Укажите ссылку из метаданных]
2. Прямой ответ: [Ваш ответ]
3. Обоснование: [Название статьи и краткая цитата/суть]

Дисклеймер: "Данный ответ носит информационный характер и не является официальной юридической консультацией."

Контекст: {context}
Вопрос: {question}
Ответ: """)

    def answer_question(self, question):
        logger.info(f"🔍 Получен вопрос: {question}")
        
        # 1. Search in Chroma
        try:
            retrieved_docs = self.vector_store.similarity_search(question, k=3)
            logger.info(f"📚 Извлечено {len(retrieved_docs)} чанков из ChromaDB")
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске в ChromaDB: {e}")
            raise

        # 2. Enrich with PostgreSQL and format context
        docs_with_metadata = []
        db = SessionLocal()
        try:
            for i, doc in enumerate(retrieved_docs):
                title = doc.metadata.get("title", "Без названия")
                link = doc.metadata.get("link", "Нет ссылки")
                postgres_id = doc.metadata.get("postgres_article_id")
                
                full_article_info = ""
                if postgres_id:
                    article = db.query(Article).filter(Article.id == postgres_id).first()
                    if article:
                        full_article_info = f"✅ Найдено в Postgres (ID: {postgres_id})"
                        logger.debug(f"📄 Чанк {i+1}: {title} (ID: {postgres_id})")
                
                docs_with_metadata.append(
                    f"Title: {title}\n"
                    f"Link: {link}\n"
                    f"Chunk Text: {doc.page_content}\n"
                    f"{full_article_info}"
                )
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при обогащении данными из Postgres: {e}")
        finally:
            db.close()

        context = "\n---\n".join(docs_with_metadata)
        
        # 3. Generate answer
        prompt = self.prompt_template.invoke({"question": question, "context": context})
        logger.info("🤖 Отправка промпта в LLM...")
        
        try:
            response = self.llm.invoke(prompt)
            logger.info("✨ Ответ от LLM успешно получен.")
            return response.content
        except Exception as e:
            logger.error(f"❌ Ошибка при вызове LLM: {e}")
            raise
