.PHONY: setup generate run run-local run-nvidia run-cloud clean help

# ============================================================================
# CONFIGURATION - Override with: make run PROVIDER=nvidia MODEL=... EMBEDDING=...
# ============================================================================

# Default provider (can be overridden: make run PROVIDER=nvidia)
PROVIDER ?= local

# Model settings (auto-set based on PROVIDER, or override explicitly)
MODEL ?= 
EMBEDDING_MODEL ?= 
BASE_URL ?= 
API_KEY ?= 

# Read API keys from environment if not explicitly provided
# Priority: explicit API_KEY > NVIDIA_API_KEY > OPENAI_API_KEY
ifeq ($(API_KEY),)
    ifneq ($(shell printenv NVIDIA_API_KEY 2>/dev/null),)
        API_KEY := $(shell printenv NVIDIA_API_KEY)
    else ifneq ($(shell printenv OPENAI_API_KEY 2>/dev/null),)
        API_KEY := $(shell printenv OPENAI_API_KEY)
    endif
endif

# ============================================================================
# PROVIDER-SPECIFIC DEFAULTS (target-specific variables for shortcuts)
# ============================================================================

run-local: PROVIDER := local
run-local: MODEL := mistral-nemo:12b
run-local: EMBEDDING_MODEL := nomic-embed-text
run-local: BASE_URL := http://localhost:11434/v1
run-local: API_KEY := local-no-key-needed

run-nvidia: PROVIDER := nvidia
run-nvidia: MODEL := nvidia/nemotron-3-ultra-550b-a55b
run-nvidia: EMBEDDING_MODEL := nvidia/nv-embed-v1
run-nvidia: BASE_URL := https://integrate.api.nvidia.com/v1
run-nvidia: API_KEY := $(shell printenv NVIDIA_API_KEY)

run-cloud: PROVIDER := cloud
run-cloud: MODEL := gpt-4o-mini
run-cloud: EMBEDDING_MODEL := text-embedding-3-small
run-cloud: BASE_URL := https://api.openai.com/v1
run-cloud: API_KEY := $(shell printenv OPENAI_API_KEY)

# Also apply to generate shortcuts
generate-local: PROVIDER := local
generate-local: MODEL := mistral-nemo:12b
generate-local: EMBEDDING_MODEL := nomic-embed-text
generate-local: BASE_URL := http://localhost:11434/v1
generate-local: API_KEY := local-no-key-needed

generate-nvidia: PROVIDER := nvidia
generate-nvidia: MODEL := nvidia/nemotron-3-ultra-550b-a55b
generate-nvidia: EMBEDDING_MODEL := nvidia/nv-embed-v1
generate-nvidia: BASE_URL := https://integrate.api.nvidia.com/v1
generate-nvidia: API_KEY := $(shell printenv NVIDIA_API_KEY)

generate-cloud: PROVIDER := cloud
generate-cloud: MODEL := gpt-4o-mini
generate-cloud: EMBEDDING_MODEL := text-embedding-3-small
generate-cloud: BASE_URL := https://api.openai.com/v1
generate-cloud: API_KEY := $(shell printenv OPENAI_API_KEY)

# ============================================================================
# EXPORT VARIABLES - these are now set in each recipe to use target-specific vars
# ============================================================================

# ============================================================================
# TARGETS
# ============================================================================

help:
	@echo "========================================================================"
	@echo "                  Karakana RAG Workspace Controller                      "
	@echo "========================================================================"
	@echo "Usage: make <target> [PROVIDER=local|nvidia|cloud] [MODEL=...] [EMBEDDING_MODEL=...] [BASE_URL=...] [API_KEY=...]"
	@echo ""
	@echo "Targets:"
	@echo "  make setup           - Install project dependencies via pip"
	@echo "  make generate        - Run Q&A generation (dual-pass)"
	@echo "  make run-local       - Run with Ollama (local)"
	@echo "  make run-nvidia      - Run with NVIDIA API"
	@echo "  make run-cloud       - Run with OpenAI API"
	@echo "  make clean           - Wipe generated artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make run-local                          # Use Ollama (default)"
	@echo "  make run-nvidia                         # Use NVIDIA API"
	@echo "  make run-cloud                          # Use OpenAI API"
	@echo "  make run PROVIDER=nvidia MODEL=nvidia/llama-3.1-nemotron-70b-instruct"
	@echo "  make generate PROVIDER=local MODEL=llama3.1:8b"
	@echo "========================================================================"

setup:
	@echo "Installing pipeline dependencies..."
	pip install --upgrade pip
	pip install --ignore-installed -r requirements.txt

generate-local: generate
generate-nvidia: generate
generate-cloud: generate

generate:
	@if [ -z "$(MODEL)" ] || [ -z "$(EMBEDDING_MODEL)" ] || [ -z "$(BASE_URL)" ]; then \
		echo "Error: Missing required settings. Use generate-local, generate-nvidia, or generate-cloud."; \
		exit 1; \
	fi
	export LLM_PROVIDER=$(PROVIDER) && \
	export LLM_MODEL=$(MODEL) && \
	export EMBEDDING_MODEL=$(EMBEDDING_MODEL) && \
	export LLM_BASE_URL=$(BASE_URL) && \
	if [ "$(PROVIDER)" = "nvidia" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY) && \
		export NVIDIA_API_KEY=$(API_KEY); \
	elif [ "$(PROVIDER)" = "cloud" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY) && \
		export OPENAI_API_KEY=$(API_KEY); \
	elif [ "$(PROVIDER)" = "local" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY); \
	fi && \
	echo "Triggering document ingestion and context pairing routines..." && \
	echo "  Provider: $(PROVIDER)" && \
	echo "  Model: $(MODEL)" && \
	echo "  Embedding: $(EMBEDDING_MODEL)" && \
	echo "  Base URL: $(BASE_URL)" && \
	if [ ! -d "docs" ]; then mkdir docs; echo "Created missing docs/ directory. Drop files inside."; fi && \
	python scripts/quizgen.py

run-local: run
run-nvidia: run
run-cloud: run

run:
	@if [ -z "$(MODEL)" ] || [ -z "$(EMBEDDING_MODEL)" ] || [ -z "$(BASE_URL)" ]; then \
		echo "Error: Missing required settings. Use run-local, run-nvidia, or run-cloud."; \
		exit 1; \
	fi
	export LLM_PROVIDER=$(PROVIDER) && \
	export LLM_MODEL=$(MODEL) && \
	export EMBEDDING_MODEL=$(EMBEDDING_MODEL) && \
	export LLM_BASE_URL=$(BASE_URL) && \
	if [ "$(PROVIDER)" = "nvidia" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY) && \
		export NVIDIA_API_KEY=$(API_KEY); \
	elif [ "$(PROVIDER)" = "cloud" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY) && \
		export OPENAI_API_KEY=$(API_KEY); \
	elif [ "$(PROVIDER)" = "local" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY); \
	fi && \
	echo "Starting interactive chat interface..." && \
	echo "  Provider: $(PROVIDER)" && \
	echo "  Model: $(MODEL)" && \
	echo "  Embedding: $(EMBEDDING_MODEL)" && \
	echo "  Base URL: $(BASE_URL)" && \
	if [ ! -f "qa_pairs.jsonl" ]; then \
		echo "ERROR: qa_pairs.jsonl missing! Running 'make generate' first..."; \
		$(MAKE) generate; \
	fi && \
	chainlit run src/bot.py -w --port 3000

clean:
	@echo "Wiping local environment state assets..."
	rm -f qa_pairs.jsonl
	rm -rf .chroma
	find . -type d -name "__pycache__" -exec rm -rf {} +

all: clean setup generate run