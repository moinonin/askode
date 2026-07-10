import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

# Load environmental configs safely
load_dotenv()

# System Engine Paths
DOCS_DIR = os.getenv("DOCS_DIR", "./docs")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-nemo:12b")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "local-no-key-needed")

# Advanced Generation Seeds
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))
GLOBAL_QUESTIONS = int(os.getenv("GLOBAL_QUESTIONS_PER_FILE", 3))
CODE_QUESTIONS = int(os.getenv("CODE_QUESTIONS_PER_CHUNK", 2))

# Advanced Chunking Seeds
CHUNKING_SIZE = int(os.getenv("CHUNKING_SIZE", 1500))
CHUNKING_OVERLAP = int(os.getenv("CHUNKING_OVERLAP", 150))


def load_project_files(directory_path: str):
    loaded_docs = []
    base_dir = Path(directory_path)
    if not base_dir.exists():
        print(f"Error: Target directory '{directory_path}' does not exist.")
        return []
    
    for ext in ["**/*.md", "**/*.py"]:
        for file_path in base_dir.glob(ext):
            try:
                content = file_path.read_text(encoding="utf-8")
                loaded_docs.append(Document(
                    page_content=content,
                    metadata={"source": str(file_path.name)}
                ))
            except Exception as e:
                print(f"Skipping file {file_path} due to error: {e}")
    return loaded_docs


print(f"Scanning target directory: {DOCS_DIR}...")
docs = load_project_files(DOCS_DIR)

if not docs:
    print("No document assets found. Exiting generation routine.")
    exit()

print(f"Initializing Generator Engine via provider [{LLM_PROVIDER}] using model: {LLM_MODEL}")
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    temperature=LLM_TEMPERATURE
)

parser = JsonOutputParser()

global_prompt = ChatPromptTemplate.from_template(
    "You are an expert Technical Architect documenting a software system.\n"
    "Generate {num_questions} high-level conceptual question-answer pairs that explain:\n"
    "- The document's purpose and role in the system\n"
    "- Key architectural decisions and trade-offs\n"
    "- Important configurations, interfaces, or data flows\n"
    "- Non-obvious assumptions or invariants\n\n"
    "Each question must be answerable from the document alone. "
    "Avoid generic questions (e.g., 'What is this file?'). "
    "Prefer specific, referenceable insights.\n\n"
    "Document: {source}\n"
    "Content:\n{text}\n\n"
    "{format_instructions}\n"
    "Return ONLY raw JSON array. No backticks, no markdown."
).partial(format_instructions=parser.get_format_instructions())

code_prompt = ChatPromptTemplate.from_template(
    "You are a Senior Software Engineer creating a technical Q&A reference for this codebase.\n"
    "Generate {num_questions} precise question-answer pairs covering:\n"
    "- Specific function/class behavior, parameters, return values\n"
    "- Edge cases, error handling, invariants\n"
    "- Configuration keys, environment variables, constants\n"
    "- Non-obvious logic, algorithms, or side effects\n"
    "- Dependencies and coupling\n\n"
    "Each Q&A must be grounded in the snippet. "
    "If the snippet is too generic (boilerplate, imports only), return empty array []."
    "Do not hallucinate beyond the provided text.\n\n"
    "Source file: {source}\n"
    "Snippet:\n{text}\n\n"
    "{format_instructions}\n"
    "Return ONLY raw JSON array. No backticks, no markdown."
).partial(format_instructions=parser.get_format_instructions())

global_chain = global_prompt | llm | parser
code_chain = code_prompt | llm | parser

all_qa = []

def process_generated_pairs(pairs, source_metadata):
    if isinstance(pairs, list):
        for qa in pairs:
            question = qa.get("question") or qa.get("q")
            answer = qa.get("answer") or qa.get("a")
            if question and answer:
                all_qa.append({
                    "id": f"qa_{len(all_qa)}",
                    "source": source_metadata,
                    "question": question,
                    "answer": answer
                })

# PASS 1: High-Level Core Profiler Pass
print(f"Pass 1: Profiling macro contexts ({GLOBAL_QUESTIONS} Qs/file) for {len(docs)} files...")
for doc in docs:
    text_to_process = doc.page_content[:12000] if len(doc.page_content) > 12000 else doc.page_content
    source = doc.metadata["source"]
    try:
        pairs = global_chain.invoke({"text": text_to_process, "num_questions": GLOBAL_QUESTIONS, "source": source})
        process_generated_pairs(pairs, source)
    except Exception as e:
        print(f"Error compiling global mappings for {source}: {e}")
    time.sleep(0.2)

# PASS 2: Detailed Fragment Splitting Pass
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNKING_SIZE, chunk_overlap=CHUNKING_OVERLAP)
chunks = splitter.split_documents(docs)

print(f"Pass 2: Processing code items ({CODE_QUESTIONS} Qs/chunk) across {len(chunks)} fragments...")
for i, chunk in enumerate(chunks):
    source = chunk.metadata["source"]
    try:
        pairs = code_chain.invoke({"text": chunk.page_content, "num_questions": CODE_QUESTIONS, "source": source})
        process_generated_pairs(pairs, source)
    except Exception as e:
        print(f"Error reading logic array at position {i}: {e}")
    time.sleep(0.2)

with open("qa_pairs.jsonl", "w", encoding="utf-8") as f:
    for entry in all_qa:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Success! {len(all_qa)} total QA records initialized inside qa_pairs.jsonl.")
