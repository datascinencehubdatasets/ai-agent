from typing import List
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

from config import get_settings

settings = get_settings()

class RAGRetriever:
    """Поиск релевантной информации из Knowledge Base"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url
        )
        
        self.vectorstore = Chroma(
            collection_name=settings.chroma_collection,
            embedding_function=self.embeddings,
            persist_directory="./data/embeddings/chroma_db"
        )
    
    async def retrieve(
        self,
        query: str,
        k: int = 3,
        filter_metadata: dict = None
    ) -> List[str]:
        """Найти релевантные документы"""
        
        # Поиск похожих документов
        docs = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_metadata
        )
        
        # Вернуть контент документов
        return [doc.page_content for doc in docs]