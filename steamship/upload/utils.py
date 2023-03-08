import re
from pathlib import Path
from typing import Optional, Set

import click
from langchain.document_loaders import PagedPDFSplitter
from steamship_langchain.vectorstores import SteamshipVectorStore


def index_book(book: Path, doc_index: SteamshipVectorStore, loaded_books: Optional[Set[str]] = None):
    loaded_books = loaded_books or set()

    if book.name in loaded_books:
        if click.confirm(f"The book \"{book.name}\" is already indexed, do you want me to skip it?", default=True):
            return

    loader = PagedPDFSplitter(str(book.resolve()))
    pages = loader.load_and_split()

    doc_index.add_texts(
        texts=[re.sub("\u0000", "", page.page_content) for page in pages],
        metadatas=[{**page.metadata, "source": book.name} for page in pages],
    )
