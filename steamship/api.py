import json
from typing import Type, Optional, Dict, Any, List
from uuid import uuid1

import langchain
from langchain import PromptTemplate
from langchain.chains import ChatVectorDBChain
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from steamship import Steamship, File
from steamship.invocable import Config
from steamship.invocable import PackageService, post, get
from steamship_langchain import OpenAI
from steamship_langchain.vectorstores import SteamshipVectorStore

from chat_history import ChatHistory

langchain.llm_cache = None

DEBUG = False


class AskMyBook(PackageService):
    class AskMyBookConfig(Config):
        index_name: str
        default_chat_session_id: Optional[str] = "default"

    config: AskMyBookConfig

    def __init__(
            self,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.qa_chain = self._get_chain()

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return cls.AskMyBookConfig

    def _get_index(self):
        return SteamshipVectorStore(client=self.client,
                                    index_name=self.config.index_name,
                                    embedding="text-embedding-ada-002"
                                    )

    def _get_chain(self):
        doc_index = self._get_index()
        condense_question_prompt_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Standalone question:"""
        condense_question_prompt = PromptTemplate.from_template(condense_question_prompt_template)

        qa_prompt_template = """I want you to ANSWER a QUESTION based on the following pieces of CONTEXT. 

        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Your ANSWER should be analytical and straightforward. 
        Try to share deep, thoughtful insights and explain complex ideas in a simple and concise manner. 
        When appropriate use analogies and metaphors to illustrate your point. 
        Your ANSWER should have a strong focus on clarity, logic, and brevity.
        Your ANSWER should be truthful and correct according to the given SOURCES
        
        CONTEXT: {context}
        
        QUESTION: {question}
        
        ANSWER:
        """
        qa_prompt = PromptTemplate(
            template=qa_prompt_template, input_variables=["context", "question"]
        )

        doc_chain = load_qa_chain(OpenAI(client=self.client, temperature=0, verbose=DEBUG),
                                  chain_type="stuff",
                                  prompt=qa_prompt,
                                  verbose=DEBUG)
        question_chain = LLMChain(
            llm=OpenAI(client=self.client, temperature=0, verbose=DEBUG),
            prompt=condense_question_prompt,
        )
        return ChatVectorDBChain(
            vectorstore=doc_index,
            combine_docs_chain=doc_chain,
            question_generator=question_chain,
            return_source_documents=True,
            top_k_docs_for_context=2
        )

    @get("/books")
    def get_indexed_books(self) -> List[str]:
        return list(
            set(json.loads(item.metadata)["source"] for item in self._get_index().index.index.list_items().items))

    @get("/author")
    def get_author_info(self) -> Dict[str, str]:
        try:
            f = File.query(self.client, tag_filter_query=f'kind "AuthorTag" and name "{self.config.index_name}"')
            return f.files[0].tags[0].value
        except Exception:
            return {}

    @post("/verify")
    def verify(self, question: str, answer: str, sources: List[Document]) -> bool:
        template = """I want you to verify the truthfulness and correctness of a given ANSWER. 

        Answer "incorrect" if you think the ANSWER is incorrect in light of the SOURCES. 
        Answer "correct" if you think the ANSWER is correct in light of the SOURCES. 

        QUESTION: {question}

        ANSWER: {answer}

        SOURCES: {sources}

        DECISION: """

        if "I do not know" in answer or "I don't know" in answer or "No sources found" in answer:
            return True
        if not sources:
            return False

        llm_chain = LLMChain(
            prompt=PromptTemplate(template=template, input_variables=["question", "answer", "sources"]),
            llm=OpenAI(client=self.client)
        )

        response = llm_chain.run(question=question,
                                 answer=answer,
                                 sources="\n".join([doc.page_content for doc in sources]))
        return "incorrect" not in response.lower()

    @post("/answer")
    def answer(self, question: str, chat_session_id: Optional[str] = None) -> Dict[str, Any]:
        chat_session_id = chat_session_id or self.config.default_chat_session_id
        chat_history = ChatHistory(self.client, chat_session_id)

        result = self.qa_chain(
            {"question": question, "chat_history": chat_history.load()}
        )
        if len(result["source_documents"]) == 0:
            return {"answer": "No sources found to answer your question. Please try another question.",
                    "sources": result["source_documents"]}

        answer = result["answer"]
        sources = result["source_documents"]
        chat_history.append(question, answer)
        is_plausible = self.verify(question, answer, sources)

        return {"answer": answer.strip(),
                "sources": sources,
                "is_plausible": is_plausible}


if __name__ == "__main__":
    index_name = "simon_sinek"
    package = AskMyBook(client=Steamship(workspace=index_name), config={"index_name": index_name})

    for question in ["What color are bananas?", "This is a test", "how can I be happy?",
                     "Who is the author of this book?"][:1]:
        print("question", question)
        answer = package.answer(
            question=question,
            chat_session_id=str(uuid1())
        )
        print(answer)
        print("sources", answer["sources"])
        verified = package.verify(question=question, answer=answer["answer"], sources=answer["sources"])
        print(verified)
