from src.infrastructure.llm import get_embeddings, get_llm
from src.infrastructure.vector_store import VectorStoreManager
from src.application.rag_service import RAGService
import sys

def main():
    # Force UTF-8 for everything at the entry point
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    embeddings = get_embeddings()
    vector_store = VectorStoreManager(
        embeddings, 
        collection_name="kazakhstan_codes_v4", 
        persist_directory="./chroma_db_v4"
    )
    llm = get_llm()
    rag_service = RAGService(vector_store, llm)

    print("="*50)
    print("Юридический RAG-ассистент по законодательству РК")
    print("Введите ваш вопрос или 'exit' для выхода.")
    print("="*50)

    while True:
        try:
            sys.stdout.write("\nВы: ")
            sys.stdout.flush()
            
            # Use buffer to read raw bytes if necessary, but reconfigure should handle it
            line = sys.stdin.readline()
            if not line:
                break
            question = line.strip()
            
            if not question:
                continue
                
            if question.lower() in ["exit", "quit", "выход", "пока"]:
                print("До свидания!")
                break

            print("Ассистент думает...")
            answer = rag_service.answer_question(question)
            
            print("\n--- ОТВЕТ ---")
            print(answer)
            print("-" * 30)

        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            print("Попробуйте еще раз или проверьте настройки (например, API ключ).")

if __name__ == "__main__":
    main()
