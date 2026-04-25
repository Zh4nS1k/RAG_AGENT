from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from api import openrouter_api
from database import SessionLocal, Article

import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rag_agent.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 1. Инициализация модели эмбеддингов
logger.info("Инициализация модели эмбеддингов...")
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

# 2. Подключение к существующей векторной базе данных
logger.info("Подключение к ChromaDB...")
vector_store = Chroma(
    collection_name="kazakhstan_codes_v3",
    embedding_function=embeddings,
    persist_directory="./chroma_db_v3",
)

# 3. Создание шаблона промпта
template = """
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
Ответ: """
prompt = ChatPromptTemplate.from_template(template)

# 4. Инициализация языковой модели (LLM)
logger.info("Инициализация LLM (OpenRouter/Google Lyria)...")
llm = ChatOpenAI(
    model="google/lyria-3-pro-preview",
    openai_api_key=openrouter_api,
    base_url="https://openrouter.ai/api/v1"
)

# 5. Выполнение запроса
question = "Каков размер минимальной заработной платы согласно Трудовому кодексу РК?"
logger.info(f"ВОПРОС: {question}")

# Поиск релевантных документов (топ-3 чанка)
logger.info("Поиск релевантных документов в ChromaDB...")
retrieved_docs = vector_store.similarity_search(question, k=3)
logger.info(f"Найдено чанков: {len(retrieved_docs)}")

# Подготовка контекста с метаданными из Chroma и PostgreSQL
docs_with_metadata = []
db = SessionLocal()

try:
    for i, doc in enumerate(retrieved_docs):
        link = doc.metadata.get("link", "Нет ссылки")
        title = doc.metadata.get("title", "Нет заголовка")
        postgres_id = doc.metadata.get("postgres_article_id")
        
        logger.info(f"--- Чанк #{i+1} ---")
        logger.info(f"Заголовок: {title}")
        logger.info(f"Ссылка: {link}")
        logger.info(f"ID в Postgres: {postgres_id}")
        logger.info(f"Содержимое чанка (первые 100 символов): {doc.page_content[:100]}...")
        
        # Получаем полный текст статьи из PostgreSQL
        full_article_text = ""
        if postgres_id:
            article = db.query(Article).filter(Article.id == postgres_id).first()
            if article:
                full_article_text = f"(Полная статья доступна в БД, ID: {postgres_id})"
                logger.info("Связь с полной статьей в PostgreSQL подтверждена.")
        
        docs_with_metadata.append(
            f"Заголовок: {title}\n"
            f"Ссылка: {link}\n"
            f"Текст чанка: {doc.page_content}\n"
            f"{full_article_text}"
        )
finally:
    db.close()

docs_content = "\n---\n".join(docs_with_metadata)

# Формирование сообщения для LLM на основе шаблона и найденного контекста
message = prompt.invoke({"question": question, "context": docs_content})

logger.info("ОТПРАВКА В LLM:")
logger.info("==================== PROMPT START ====================")
logger.info(message.to_string())
logger.info("==================== PROMPT END ======================")

# Генерация ответа
logger.info("Ожидание ответа от LLM...")
answer = llm.invoke(message)

logger.info("ПОЛУЧЕН ОТВЕТ ОТ LLM:")
logger.info("==================== RESPONSE START ==================")
logger.info(answer.content)
logger.info("==================== RESPONSE END ====================")

# Вывод результата в консоль (дублирование для удобства)
print("\n--- ФИНАЛЬНЫЙ ОТВЕТ ---")
print(answer.content)