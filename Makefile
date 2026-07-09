.PHONY: setup generate run clean help

# Default target when someone types just 'make'
help:
	@echo "========================================================================"
	@echo "                  Karakana RAG Workspace Controller                      "
	@echo "========================================================================"
	@echo "make setup    - Install project dependencies via pip"
	@echo "make generate - One-off compilation task to turn docs into Q&A data"
	@echo "make run      - Launch the interactive Chainlit Chatbot interface"
	@echo "make clean    - Wipe local generated datasets and cache frameworks"
	@echo "========================================================================"

# Step 1: Install required workspace libraries
setup:
	@echo "Installing pipeline dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

# Step 2: One-off knowledge compiler sequence 
generate:
	@echo "Triggering document ingestion and context pairing routines..."
	@if [ ! -d "docs" ]; then mkdir docs; echo "Created missing docs/ directory. Drop files inside."; fi
	python scripts/quizgen.py

# Step 3: Spin up interactive UI agent matrix
run:
	@echo "Starting up interactive chat interface agent..."
	@if [ ! -f "qa_pairs.jsonl" ]; then \
		echo "ERROR: qa_pairs.jsonl missing! Automatically executing 'make generate' first..."; \
		make generate; \
	fi
	chainlit run src/bot.py -w

# Cleanup temporary compilation folders and data maps
clean:
	@echo "Wiping local environment state assets..."
	rm -f qa_pairs.jsonl
	rm -rf .chroma
	find . -type d -name "__pycache__" -exec rm -rf {} +

