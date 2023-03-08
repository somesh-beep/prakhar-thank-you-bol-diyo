import re
from pathlib import Path
from typing import Dict

import toml as toml
from steamship import File, Tag
from steamship import Steamship
from steamship.upload.utils import index_book
from steamship_langchain.vectorstores import SteamshipVectorStore


def add_author_info(client: Steamship, index_name: str, author_info: Dict[str, str]):
    for file in File.query(client, tag_filter_query='all').files:
        file.delete()

    File.create(client, tags=[
        Tag(kind="AuthorTag", name=index_name, value=author_info)
    ])


def to_snake(author_name: str):
    return '_'.join(
        re.sub('([A-Z][a-z]+)', r' \1',
               re.sub('([A-Z]+)', r' \1',
                      author_name.replace('-', ' '))).split()).lower()


for folder in Path("uploads/authors").iterdir():
    author_name = folder.name
    index_name = to_snake(author_name)
    print(index_name)

    # Connect to the workspace
    client = Steamship(workspace=index_name)

    # Load author metadata
    metadata = toml.load(folder / "metadata.toml")
    # Add author info file
    add_author_info(client=client, index_name=index_name, author_info={
        "authorName": author_name,
        **metadata
    })

    # Connect to vector store
    doc_index = SteamshipVectorStore(client=client,
                                     index_name=index_name,
                                     embedding="text-embedding-ada-002")

    # Reset vector store
    doc_index.index.reset()

    # Add books to the vector store
    for book in folder.iterdir():
        if book.suffix == ".pdf":
            print(f"\t{book}")
            index_book(book, doc_index)
