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

# ============================================================================
# OKF Knowledge Bundle Targets
# ============================================================================

# Bundle generation
okf-generate-code:
	okf generate ./src ./docs/okfs/code_bundle

okf-generate-scripts:
	okf generate ./scripts ./docs/okfs/scripts_bundle

okf-generate-strategies:
	okf generate ./docs/strategies ./docs/okfs/strategies_bundle

okf-generate-docs:
	python scripts/convert_docs_to_okf.py --source docs --output docs/okfs/docs_bundle

okf-generate-all: okf-generate-code okf-generate-scripts okf-generate-strategies okf-generate-docs

# Incremental updates (fast - only changed files)
okf-update-code:
	okf update ./src ./docs/okfs/code_bundle

okf-update-scripts:
	okf update ./scripts ./docs/okfs/scripts_bundle

okf-update-strategies:
	okf update ./docs/strategies ./docs/okfs/strategies_bundle

okf-update-docs:
	python scripts/convert_docs_to_okf.py --source docs --output docs/okfs/docs_bundle

okf-update-all: okf-update-code okf-update-scripts okf-update-strategies okf-update-docs

# Watch mode (continuous updates during development)
okf-watch-code:
	okf update ./src ./docs/okfs/code_bundle --watch

okf-watch-scripts:
	okf update ./scripts ./docs/okfs/scripts_bundle --watch

okf-watch-strategies:
	okf update ./docs/strategies ./docs/okfs/strategies_bundle --watch

okf-watch-docs:
	okf update ./docs ./docs/okfs/docs_bundle --watch

# Chunking + Embedding + Indexing
okf-chunk:
	python scripts/chunk_okf_bundles.py --bundle docs/okfs/code_bundle --bundle docs/okfs/docs_bundle --bundle docs/okfs/scripts_bundle --bundle docs/okfs/strategies_bundle --output docs/okfs/chunks

okf-embed:
	python scripts/generate_embeddings.py

okf-index:
	python scripts/index_to_chromadb.py

okf-pipeline: okf-chunk okf-embed okf-index

# Cross-bundle links
okf-link:
	python scripts/add_cross_bundle_links.py

# Visualization
okf-viz-code:
	mkdir -p docs/okfs/viz && okf visualize ./docs/okfs/code_bundle docs/okfs/viz/code_viz.html

okf-viz-scripts:
	mkdir -p docs/okfs/viz && okf visualize ./docs/okfs/scripts_bundle docs/okfs/viz/scripts_viz.html

okf-viz-strategies:
	mkdir -p docs/okfs/viz && okf visualize ./docs/okfs/strategies_bundle docs/okfs/viz/strategies_viz.html

okf-viz-docs:
	mkdir -p docs/okfs/viz && okf visualize ./docs/okfs/docs_bundle docs/okfs/viz/docs_viz.html

okf-viz-all: okf-viz-code okf-viz-scripts okf-viz-strategies okf-viz-docs

# Live dashboard
okf-dashboard:
	okf dashboard ./docs/okfs/code_bundle --port 8700 --open

# Evaluation
okf-eval:
	python scripts/okf_eval.py

# OKF Chat (Chainlit over ChromaDB)
okf-chat:
	@if [ -z "$(MODEL)" ] || [ -z "$(EMBEDDING_MODEL)" ] || [ -z "$(BASE_URL)" ]; then \
		echo "Error: Missing required settings. Use okf-chat-local, okf-chat-nvidia, or okf-chat-cloud."; \
		exit 1; \
	fi
	export LLM_PROVIDER=$(LLM_PROVIDER) && \
	export LLM_MODEL=$(MODEL) && \
	export EMBEDDING_MODEL=$(EMBEDDING_MODEL) && \
	export LLM_BASE_URL=$(BASE_URL) && \
	if [ "$(LLM_PROVIDER)" = "nvidia" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY) && \
		export NVIDIA_API_KEY=$(API_KEY); \
	elif [ "$(LLM_PROVIDER)" = "cloud" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY) && \
		export OPENAI_API_KEY=$(API_KEY); \
	elif [ "$(LLM_PROVIDER)" = "local" ] && [ -n "$(API_KEY)" ]; then \
		export LLM_API_KEY=$(API_KEY); \
	fi && \
	echo "Starting OKF RAG chat interface..." && \
	echo "  Provider: $(LLM_PROVIDER)" && \
	echo "  Model: $(MODEL)" && \
	echo "  Embedding: $(EMBEDDING_MODEL)" && \
	echo "  Base URL: $(BASE_URL)" && \
	chainlit run src/okf_chat.py -w --port 3000
	chainlit run src/okf_chat.py -w --port 3000

okf-chat-local: LLM_PROVIDER := local
okf-chat-local: MODEL := mistral-nemo:12b
okf-chat-local: EMBEDDING_MODEL := nomic-embed-text
okf-chat-local: BASE_URL := http://localhost:11434/v1
okf-chat-local: API_KEY := local-no-key-needed
okf-chat-local: okf-chat

okf-chat-nvidia: LLM_PROVIDER := nvidia
okf-chat-nvidia: MODEL := nvidia/nemotron-3-ultra-550b-a55b
okf-chat-nvidia: EMBEDDING_MODEL := nvidia/nv-embed-v1
okf-chat-nvidia: BASE_URL := https://integrate.api.nvidia.com/v1
okf-chat-nvidia: API_KEY := $(shell printenv NVIDIA_API_KEY)
okf-chat-nvidia: okf-chat

okf-chat-cloud: LLM_PROVIDER := cloud
okf-chat-cloud: MODEL := gpt-4o-mini
okf-chat-cloud: EMBEDDING_MODEL := text-embedding-3-small
okf-chat-cloud: BASE_URL := https://api.openai.com/v1
okf-chat-cloud: API_KEY := $(shell printenv OPENAI_API_KEY)
okf-chat-cloud: okf-chat

# Agent integration
okf-install-agents:
	okf install all

# Lookup helper
okf-lookup:
	@if [ -z "$(CONCEPT)" ]; then \
		echo "Usage: make okf-lookup CONCEPT=<ConceptName> BUNDLE=<bundle_name>"; \
		echo "Bundles: code_bundle, scripts_bundle, strategies_bundle, docs_bundle"; \
		exit 1; \
	fi
	okf lookup --bundle ./docs/okfs/$(BUNDLE) "$(CONCEPT)"

# Full rebuild
okf-full-rebuild: clean okf-generate-all okf-pipeline okf-link

all: clean setup generate run

okf-all: okf-full-rebuild okf-install-agents