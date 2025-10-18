import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

from config import get_settings

settings = get_settings()

async def index_knowledge_base():
    """Индексировать Knowledge Base в векторное хранилище"""
    
    print("🔄 Индексация Knowledge Base...")
    
    # Загрузить документы
    kb_path = "./data/knowledge_base/islamic_finance_kb.md"
    
    if not os.path.exists(kb_path):
        print("⚠️  Knowledge Base не найдена")
        return
    
    with open(kb_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Разбить на chunks по разделам
    chunks = split_by_sections(content)
    
    # Создать документы
    documents = []
    for i, chunk in enumerate(chunks):
        metadata = extract_metadata(chunk)
        metadata["chunk_id"] = i
        
        doc = Document(
            page_content=chunk,
            metadata=metadata
        )
        documents.append(doc)
    
    # Создать embeddings
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_base_url
    )
    
    # Создать или обновить векторное хранилище
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=settings.chroma_collection,
        persist_directory="./data/embeddings/chroma_db"
    )
    
    print(f"✅ Индексировано {len(documents)} chunks")
    
    return vectorstore

def split_by_sections(content: str) -> List[str]:
    """Разбить контент по разделам"""
    sections = []
    current_section = []
    
    for line in content.split("\n"):
        if line.startswith("## РАЗДЕЛ"):
            if current_section:
                sections.append("\n".join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    if current_section:
        sections.append("\n".join(current_section))
    
    return sections

def extract_metadata(chunk: str) -> dict:
    """Извлечь метаданные из chunk"""
    metadata = {}
    
    # Извлечь номер раздела
    if "## РАЗДЕЛ" in chunk:
        section_line = chunk.split("\n")[0]
        metadata["section"] = section_line.strip()
        
        # Определить тип контента
        if "ТЕРМИН" in section_line or "ГЛОССАРИЙ" in section_line:
            metadata["type"] = "term"
        elif "FAQ" in section_line or "ВОПРОС" in section_line:
            metadata["type"] = "faq"
        elif "ПРОДУКТ" in section_line:
            metadata["type"] = "product"
        else:
            metadata["type"] = "concept"
    
    return metadata