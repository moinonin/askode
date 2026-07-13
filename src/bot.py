import os
import json
import chainlit as cl
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from pydantic import SecretStr
import openai
import ollama

# Parse application landscape parameters
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-nemo:12b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "local-no-key-needed")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", LLM_API_KEY)

# Advanced RAG Custom Param Hooks
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.3))
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", 4))


class OllamaEmbeddingsFixed(Embeddings):
    """Custom Ollama embeddings that works without /tokenize endpoint."""
    
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.client = ollama.Client(host=base_url)
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self.client.embed(model=self.model, input=texts)
        return result['embeddings']
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class NVIDIAEmbeddings(Embeddings):
    """Custom NVIDIA embeddings that bypasses tiktoken tokenization."""
    
    def __init__(self, model: str, base_url: str, api_key: str):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.client = openai.OpenAI(base_url=base_url, api_key=api_key)
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [d.embedding for d in result.data]
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


# 1. Routing runtime vector maps
if LLM_PROVIDER == "cloud":
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=SecretStr(LLM_API_KEY))
elif LLM_PROVIDER == "nvidia":
    # NVIDIA uses custom embeddings to bypass tiktoken
    embeddings = NVIDIAEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=LLM_BASE_URL,
        api_key=NVIDIA_API_KEY
    )
else:
    ollama_root = LLM_BASE_URL.replace("/v1", "").strip()
    embeddings = OllamaEmbeddingsFixed(model=EMBEDDING_MODEL, base_url=ollama_root)

# 2. Main Generation Engine setup
if LLM_PROVIDER == "nvidia":
    # NVIDIA uses OpenAI-compatible API format
    local_llm = ChatOpenAI(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=SecretStr(NVIDIA_API_KEY),
        temperature=LLM_TEMPERATURE
    )
else:
    local_llm = ChatOpenAI(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=SecretStr(LLM_API_KEY),
        temperature=LLM_TEMPERATURE
    )

# 3. Dynamic Memory Store Creation
qa_list = []
try:
    with open("qa_pairs.jsonl", "r", encoding="utf-8") as f:
        qa_list = [json.loads(line) for line in f if line.strip()]
except FileNotFoundError:
    print("Reference database index missing. Generate qa_pairs.jsonl first.")

documents = [
    Document(
        page_content=f"Question: {qa['question']}\nAnswer: {qa['answer']}\nSource: {qa['source']}",
        metadata={"source": qa['source']}
    ) for qa in qa_list
]

if documents:
    print(f"Assembling search context spaces using Top-K limit: {RETRIEVER_TOP_K}...")
    vector_store = Chroma.from_documents(documents, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K})
else:
    retriever = None

prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a technical expert answering questions about a software project using a curated Q&A knowledge base.\n"
        "Each context entry has a source file (shown as 'Source: filename'). Use this to ground your answer.\n\n"
        "Rules:\n"
        "1. Answer ONLY from the provided context. Do not use external knowledge.\n"
        "2. Cite sources inline like [Source: filename] after each claim.\n"
        "3. If context is irrelevant or missing, say: 'I cannot find that in my project files.'\n"
        "4. If context partially answers, give what you have and note gaps.\n"
        "5. Be concise. Prefer code-level specifics over generalities.\n\n"
        "--- CONTEXT ---\n"
        "{context}\n"
        "----------------"
    )),
    ("human", "{question}")
])

rag_chain = prompt_template | local_llm | StrOutputParser()


@cl.on_message
async def main(message: cl.Message):
    user_query = message.content
    
    if retriever:
        matched_docs = retriever.invoke(user_query)
        context = "\n\n".join([doc.page_content for doc in matched_docs])
    else:
        context = "No reference database compiled."
        
    msg = cl.Message(content="")
    await msg.send()
    
    # Track the full response string as it streams
    full_response = ""
    
    async for chunk in rag_chain.astream({"context": context, "question": user_query}):
        await msg.stream_token(chunk)
        full_response += chunk  # Append each token chunk
        
    await msg.update()

    # Append the completed turn to a local log file
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        f.write(f"--- Chat Turn ---\n")
        f.write(f"User: {user_query}\n")
        f.write(f"Bot: {full_response}\n\n")