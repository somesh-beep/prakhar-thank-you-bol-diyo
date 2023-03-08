"""Script to upload books to a vector index."""
import json
from pathlib import Path

import click
from steamship import Steamship
from steamship_langchain.vectorstores import SteamshipVectorStore

from utils import index_book

INDEX_NAME = "test-123"  # Step 1: NAME YOUR INDEX

BOOKS_OR_BOOK_FOLDERS = [
    # "uploads/authors/Naval Ravikant/the-almanack-of-naval-ravikant.pdf",
    "uploads/debug.pdf",
]  # Step 2: List the books or folders you want to index

client = Steamship(workspace=INDEX_NAME)

doc_index = SteamshipVectorStore(client=client,
                                 index_name=INDEX_NAME,
                                 embedding="text-embedding-ada-002")

books = set(json.loads(item.metadata)["source"]
            for item in doc_index.index.index.list_items().items)

if len(books) > 0:
    print("The index already contains the following books:")
    print("* " + "\n* ".join(books))
    if click.confirm('Do you want to reset your index?', default=True):
        print("Resetting your index, this will take a while ⏳")
        doc_index.index.reset()

for book in BOOKS_OR_BOOK_FOLDERS:
    book_path = Path(book)

    if book_path.is_dir():
        for folder in book_path.iterdir():
            index_book(book_path, doc_index, books)
    else:
        print("here")
        index_book(book_path, doc_index, books)
