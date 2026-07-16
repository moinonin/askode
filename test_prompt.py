import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOllama(model='mistral-nemo:12b', base_url='http://localhost:11434', temperature=0.1)

parser = JsonOutputParser()
code_prompt = ChatPromptTemplate.from_template(
    'You are a Senior Software Engineer creating a technical Q&A reference for this codebase.\n'
    'Generate {num_questions} precise question-answer pairs covering:\n'
    '- Specific function/class behavior, parameters, return values\n'
    '- Edge cases, error handling, invariants\n'
    '- Configuration keys, environment variables, constants\n'
    '- Non-obvious logic, algorithms, or side effects\n'
    '- Dependencies and coupling\n'
    '- **Service restart triggers, hot-reload capabilities, and hot-swap procedures**\n'
    '- **Health check endpoints, readiness/liveness probes, and failure modes**\n\n'
    'CRITICAL RULES (VIOLATION = INVALID OUTPUT):\n'
    '1. Answer ONLY from the provided snippet. If information is not in the snippet, say "Not specified in the provided snippet."\n'
    '2. Do NOT invent environment variables, endpoints, or behaviors not explicitly in the snippet.\n'
    '3. Do NOT use general knowledge to fill gaps. If the snippet does not contain the answer, state that.\n'
    '4. Each Q&A must be grounded in the snippet. If the snippet is too generic (boilerplate, imports only), return empty array [].\n'
    '5. Do not hallucinate beyond the provided text.\n\n'
    'Output Schema (JSON only, no markdown, no extra text):\n'
    '[\n'
    '  {{\n'
    '    "question": "string",\n'
    '    "answer": "string",\n'
    '    "category": "Architecture|Configuration|Deployment|Operations|Integration|Data Model|Security|Performance|Business Logic|Algorithm|API|State|Error Handling|Lifecycle|Extension Point",\n'
    '    "importance": "Critical|High|Medium|Low",\n'
    '    "concepts": ["string", "..."],\n'
    '    "confidence": 0.0-1.0\n'
    '  }}\n'
    ']\n'
    'Rules:\n'
    '- Category must be one of the listed values\n'
    '- Importance must be Critical|High|Medium|Low\n'
    '- Concepts: 3-8 tags representing key engineering concepts\n'
    '- Confidence: 0.0-1.0, how grounded the answer is in the snippet\n'
    '- Return ONLY raw JSON array. No backticks, no markdown, no extra text.\n'
    '- If snippet is too generic (boilerplate, imports only), return empty array []\n\n'
    'Source file: {source}\n'
    'Snippet:\n{text}\n\n'
).partial(format_instructions=parser.get_format_instructions())

chain = code_prompt | llm | parser

snippet = """
services:
  karakana-shadow-trader:
    restart: unless-stopped
    command: ["python", "-m", "karakana.runtime.shadow_trader", "--watch", "--policy-root", "/freqtrade/user_data/karakana_policy/watch"]
    environment:
      - KARAKANA_SHADOW_SOURCE=/freqtrade/user_data/freqtrade_signals_karakana.csv
      - KARAKANA_SHADOW_OUTPUT_CSV=/freqtrade/user_data/reports/karakana_shadow_trade_history.csv
      - KARAKANA_SHADOW_POLICY_ROOT=/freqtrade/user_data/karakana_policy/watch
    volumes:
      - ./user_data:/freqtrade/user_data

  freqtrade:
    restart: unless-stopped
    command: ["trade", "--strategy", "Strategy322sgo"]
"""

result = chain.invoke({'source': 'docker-compose.yml', 'text': snippet, 'num_questions': 2})
print(json.dumps(result, indent=2))