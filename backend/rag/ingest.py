# backend/rag/ingest.py
import os, argparse
from typing import List, Dict
from bs4 import BeautifulSoup
from backend.rag.embedder import Embedder
from backend.rag.store import LocalVectorStore

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_html_file(path: str) -> str:
    html = read_text_file(path)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")

def chunk_markdown(md: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    # простая разбиенка: сохраняем заголовки как «якоря» и режем текст на окна
    lines = [ln.strip() for ln in md.splitlines()]
    blocks: List[str] = []
    cur: List[str] = []
    for ln in lines:
        if ln.startswith("#"):  # новый раздел
            if cur:
                blocks.append("\n".join(cur).strip())
                cur = []
        cur.append(ln)
    if cur:
        blocks.append("\n".join(cur).strip())

    # вторичная нарезка крупных блоков на фиксированные чанки с перехлестом
    def sliding(text: str) -> List[str]:
        text = " ".join(text.split())
        out = []
        i = 0
        while i < len(text):
            out.append(text[i:i+chunk_size])
            i += chunk_size - overlap
        return out

    chunks: List[str] = []
    for b in blocks:
        if len(b) <= chunk_size:
            chunks.append(b)
        else:
            chunks.extend(sliding(b))
    return chunks

def ingest_single_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".html", ".htm"]:
        text = read_html_file(file_path)
    else:
        text = read_text_file(file_path)

    chunks = chunk_markdown(text)

    if not chunks:
        print("Файл пустой или не распарсен.")
        return

    embedder = Embedder()                     # text-embedding-3-small
    store = LocalVectorStore("data/embeddings")

    vecs = embedder.encode(chunks)
    metas: List[Dict] = [{"source": os.path.relpath(file_path), "chunk": i} for i in range(len(chunks))]
    store.add_texts(chunks, vecs, metas)

    print(f"OK: добавлено {len(chunks)} фрагментов из {file_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Путь к вашему .md/.txt/.html")
    args = parser.parse_args()
    ingest_single_file(args.file)
