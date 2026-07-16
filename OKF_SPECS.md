Here is a specification you can use directly as an implementation document.

# Documentation Ingestion Pipeline Specification

## Purpose

The documentation ingestion pipeline converts project documentation into a structured Open Knowledge Format (OKF) knowledge base before indexing it into a Retrieval-Augmented Generation (RAG) system.

The objective is to preserve semantic structure, relationships, and metadata so that both humans and AI agents can accurately retrieve and reason over project knowledge.

---

# Design Principles

The pipeline SHALL:

* preserve semantic boundaries
* preserve document hierarchy
* preserve relationships between concepts
* attach structured metadata to every concept
* produce deterministic output
* be independent of any specific vector database or LLM

Documentation SHALL NOT be chunked directly.

Instead, documentation SHALL first be converted into OKF concepts.

---

# High-Level Pipeline

```
Project Repository
        │
        ▼
Documentation Discovery
        │
        ▼
Convert Documentation → OKF
        │
        ▼
Validate OKF Bundle
        │
        ▼
Generate Cross Links
        │
        ▼
(Optional) AI Enrichment
        │
        ▼
Semantic Chunking
        │
        ▼
Embeddings
        │
        ▼
Vector Database
        │
        ▼
RAG
```

---

# Phase 1 – Documentation Discovery

The ingestion system SHALL recursively discover documentation under directories such as:

```
docs/
README.md
CHANGELOG.md
examples/
tutorials/
guides/
```

Additional directories MAY be configured.

Supported source formats SHOULD include:

* Markdown
* HTML
* reStructuredText
* AsciiDoc
* PDF (converted before processing)

---

# Phase 2 – OKF Conversion

Every documentation file SHALL be converted into one or more OKF concept documents.

Concept boundaries SHOULD follow logical sections rather than token counts.

For example:

```
Installation

Configuration

Architecture

Authentication

Training

Inference

Docker

REST API

Troubleshooting

FAQ
```

Each concept SHALL contain YAML frontmatter.

Example:

```yaml
---
type: Guide
title: Installing Karakana
description: Installation using Docker Compose
tags:
  - installation
  - docker
resource:
timestamp:
---
```

---

# Concept Requirements

Each concept SHOULD represent exactly one coherent topic.

Concepts SHOULD remain below the target context size of the embedding model whenever practical.

Large sections SHALL be divided into multiple concepts using semantic headings.

Concepts SHALL NOT be divided at arbitrary token boundaries.

---

# Metadata

The following metadata SHALL be attached to every concept.

Required:

* type

Recommended:

* title
* description
* tags
* timestamp
* resource

Additional ingestion metadata SHOULD be added:

```
source_file
source_directory
repository
branch
commit
section_heading
document_type
language
```

These metadata fields SHALL later become vector database metadata.

---

# Preserve Directory Hierarchy

The generated OKF bundle SHALL preserve the documentation hierarchy.

Example:

```
docs/
    architecture/
        overview.md
        components.md
        state-machine.md

    api/
        authentication.md
        trading.md

    deployment/
        docker.md
```

becomes

```
knowledge/
    architecture/
        overview.md
        components.md
        state-machine.md

    api/
        authentication.md
        trading.md

    deployment/
        docker.md
```

Directory-level `index.md` files SHOULD be generated automatically.

---

# Phase 3 – Validation

The generated bundle SHALL be validated against the OKF specification.

Validation SHOULD verify:

* valid YAML
* required fields
* valid paths
* internal links
* duplicate identifiers

Validation errors SHALL be reported before indexing.

---

# Phase 4 – Relationship Generation

Relationships SHALL be preserved whenever possible.

Examples include:

* references
* dependencies
* architecture links
* API references
* implementation references

The ingestion system SHOULD generate Markdown links between related concepts.

Example:

```
Installation Guide
        │
        ▼
Docker Compose
        │
        ▼
Configuration
        │
        ▼
Trading Engine
```

These links become traversal paths for downstream AI agents.

---

# Phase 5 – Optional AI Enrichment

The pipeline MAY perform AI enrichment before indexing.

Possible enrichments include:

* summary generation
* keyword extraction
* tag generation
* prerequisite identification
* related concept suggestions
* glossary extraction
* API parameter descriptions
* architecture summaries

AI-generated content SHALL remain separate from original documentation.

---

# Phase 6 – Semantic Chunking

Chunking SHALL operate on OKF concepts instead of raw documentation.

If a concept exceeds the embedding context window, it SHALL be divided using semantic structure such as:

* headings
* lists
* tables
* code blocks

Chunk metadata SHALL include:

```
concept_id
chunk_number
title
type
tags
path
```

Chunking SHALL preserve parent-child relationships.

---

# Phase 7 – Embedding

Each chunk SHALL be embedded independently.

Embedding metadata SHALL include all inherited OKF metadata.

Example:

```
title

type

tags

repository

source_file

section

concept_id

timestamp
```

This enables structured filtering during retrieval.

Example queries:

```
type = API Endpoint

tags = docker

type = Architecture

repository = trading-engine
```

---

# Phase 8 – Vector Database

Only semantic chunks SHALL be indexed.

The vector store SHALL NOT receive raw documentation files.

Each indexed record SHALL contain:

* embedding
* chunk text
* metadata
* concept identifier
* source path

---

# Dual Knowledge Bundles

The system SHALL maintain two independent OKF bundles.

## Documentation Bundle

Generated from:

```
docs/

README.md

CHANGELOG.md

examples/

tutorials/
```

Purpose:

Human-authored documentation.

---

## Code Bundle

Generated using an OKF code generator.

Contents include:

* packages
* modules
* classes
* methods
* functions
* interfaces
* dependencies
* call graph information

Purpose:

Machine-generated software knowledge.

---

# Cross-Bundle Linking

Documentation concepts SHOULD link to implementation concepts.

Example:

```
Installation Guide
        │
        ▼
Docker Compose
        │
        ▼
Python Module
        │
        ▼
TradingEngine
        │
        ▼
predict_action()
```

Likewise, implementation concepts SHOULD reference relevant documentation.

Example:

```
predict_action()

        │

        ▼

Trading Strategy Guide
```

This creates a navigable knowledge graph spanning documentation and source code.

---

# Expected Benefits

Compared with direct document chunking, the OKF-first approach provides:

* higher semantic coherence
* improved retrieval precision
* richer metadata filtering
* explicit knowledge relationships
* deterministic chunk boundaries
* improved explainability
* easier incremental updates
* better compatibility with AI agents
* reusable knowledge independent of any RAG implementation

---

# Future Extensions

Potential future enhancements include:

* automated knowledge graph generation
* repository-wide architecture extraction
* execution flow documentation
* dependency visualization
* API usage graph
* change impact analysis
* test coverage mapping
* design decision tracking
* conversational repository exploration
* multi-repository knowledge federation

This specification is intentionally implementation-agnostic so it can serve as the architectural foundation regardless of the specific OKF tooling, embedding model, or vector database you choose.

