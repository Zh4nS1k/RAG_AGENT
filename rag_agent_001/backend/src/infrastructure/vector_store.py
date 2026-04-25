from langchain_chroma import Chroma

class VectorStoreManager:
    def __init__(self, embeddings, collection_name="kazakhstan_codes_v4", persist_directory="./chroma_db_v4"):
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )

    def add_documents(self, documents, ids):
        self.vector_store.add_documents(documents, ids=ids)

    def similarity_search(self, query, k=3):
        return self.vector_store.similarity_search(query, k=k)
