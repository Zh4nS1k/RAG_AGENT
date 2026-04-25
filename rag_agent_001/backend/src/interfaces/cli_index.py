from src.infrastructure.llm import get_embeddings
from src.infrastructure.vector_store import VectorStoreManager
from src.application.indexing_service import IndexingService
import os

def main():
    embeddings = get_embeddings()
    # Using a new collection and directory to avoid conflicts during refactoring if needed, 
    # but the requirement is to use the existing logic. 
    # I'll use kazakhstan_codes_v4 to ensure a clean start with local files.
    vector_store = VectorStoreManager(
        embeddings, 
        collection_name="kazakhstan_codes_v4", 
        persist_directory="./chroma_db_v4"
    )
    
    indexer = IndexingService(vector_store)
    documents_folder = os.path.join(os.getcwd(), "documents")
    
    indexer.index_documents_from_folder(documents_folder)

if __name__ == "__main__":
    main()
