This sprint is arguably the **heart of the entire AI Code Library**. Everything else—OKF, embeddings, RAG, retrieval—is downstream of the quality of the knowledge extracted here. If this prompt extracts shallow facts, the library becomes a searchable API reference. If it extracts engineering knowledge, the library becomes a software engineer.

I would make this a major sprint with a clear architectural objective.

---

# Sprint X — Engineering Knowledge Extraction Engine (EKE)

## Objective

Transform source code into reusable engineering knowledge rather than documentation.

The system shall identify the knowledge contained within source code and express that knowledge as high-value question-answer pairs that help future engineers understand, modify, extend, debug, deploy, and maintain the software.

The goal is **not** code summarization.

The goal is **knowledge extraction**.

---

# Vision

Traditional documentation answers:

> "What does this function do?"

The AI Code Library should answer:

> "What do I need to understand before I change this?"

Every extracted Q&A should reduce the amount of code another engineer must read before making a correct modification.

The resulting knowledge base should serve as a long-term engineering memory for the project.

---

# Problem Statement

Current prompt:

* describes syntax
* extracts API details
* summarizes snippets

This produces documentation.

It does **not** capture engineering knowledge.

Engineering knowledge includes:

* why something exists
* how it interacts with the rest of the system
* assumptions
* hidden constraints
* operational implications
* architectural significance
* modification risks

These are significantly more valuable than simple code summaries.

---

# Goals

The extraction engine shall identify knowledge that enables engineers to:

* understand unfamiliar code
* safely modify behavior
* debug failures
* extend functionality
* integrate new components
* refactor confidently
* deploy correctly
* troubleshoot production systems

---

# Design Philosophy

The prompt should think like:

> Principal Software Architect

not

> Documentation generator

The model should imagine another engineer asking:

> "I need to modify this software."

and extract the knowledge required to do so successfully.

---

# Knowledge-First Extraction

The model shall first identify:

> What knowledge exists?

Only afterwards shall it formulate questions.

Questions are merely an interface to engineering knowledge.

They are not the primary objective.

---

# High-Value Knowledge Categories

The prompt shall prioritize extracting:

## Purpose

Why does this component exist?

What responsibility does it own?

---

## Business Logic

Decision making

Algorithms

Policies

Rules

Calculations

Transformations

---

## Architecture

Component responsibilities

Layer boundaries

Dependencies

Coupling

Extension points

Plugin interfaces

Public contracts

---

## State

State transitions

Lifecycle

Initialization

Shutdown

Persistence

Recovery

---

## Behaviour

Normal execution

Alternative execution paths

Failure paths

Recovery paths

Retry logic

Fallback behaviour

---

## Error Handling

Exceptions

Validation

Failure modes

Graceful degradation

Recovery

---

## Hidden Assumptions

Preconditions

Postconditions

Invariants

Ordering constraints

Required call sequences

Implicit dependencies

---

## Operational Knowledge

Configuration

Feature flags

Environment variables

Deployment

Health checks

Restart requirements

Hot reload

Hot swap

Monitoring

Observability

Performance implications

Scaling considerations

---

## Security

Authentication

Authorization

Validation

Secrets

Permissions

Trust boundaries

---

## Data

Schemas

Serialization

Protocols

Persistence

Caching

Indexes

Network communication

---

## Integration

External services

Third-party libraries

Databases

Queues

REST

RPC

Messaging

---

## Modification Guidance

What could break?

What depends on this?

What assumptions must remain true?

Which components are likely affected?

---

# Question Generation Principles

Questions should represent what experienced engineers naturally ask.

Good examples:

* Why is this algorithm implemented this way?
* When should this configuration be changed?
* What assumptions does this component make?
* How does this class participate in the request lifecycle?
* What happens if this dependency fails?
* What guarantees does this function provide?
* Under what conditions is this code executed?
* What state must exist before this method is called?
* Which components depend on this behavior?
* What should an engineer know before modifying this logic?

Poor examples:

* What parameters does foo() take?
* What class is Bar?
* What module contains Baz?
* What constant is defined here?

Unless those details have architectural significance.

---

# Knowledge Density

The prompt should optimize for knowledge density.

Every generated Q&A should contain information that remains valuable months after the code was written.

Avoid extracting temporary implementation noise.

Avoid restating obvious syntax.

Prefer fewer, higher-value questions over many trivial ones.

---

# Engineering Value Ranking

Every extracted Q&A shall include an importance rating.

Suggested values:

* Critical
* High
* Medium
* Low

Importance should reflect:

* architectural impact
* modification risk
* debugging usefulness
* operational significance
* likelihood another engineer will need this knowledge

---

# Knowledge Categories

Each Q&A shall include a category.

Examples:

* Architecture
* Business Logic
* Algorithm
* Configuration
* API
* Security
* State
* Error Handling
* Deployment
* Performance
* Data Model
* Integration
* Lifecycle
* Operations
* Extension Point

---

# Concept Extraction

Every Q&A shall include concept tags.

Example:

```json
{
    "concepts": [
        "authentication",
        "jwt",
        "refresh token",
        "session lifecycle"
    ]
}
```

Concepts become:

* OKF tags
* retrieval metadata
* graph nodes
* semantic links
* navigation aids

---

# Output Schema

The prompt should evolve from:

```json
{
    "question": "...",
    "answer": "..."
}
```

to something closer to:

```json
{
    "question": "...",
    "answer": "...",
    "category": "Architecture",
    "importance": "High",
    "concepts": [
        "dependency injection",
        "configuration"
    ],
    "confidence": 0.97
}
```

Future fields may include:

* affected_components
* related_questions
* prerequisites
* assumptions
* source_symbols

---

# Hallucination Policy

The model SHALL:

* answer only from the supplied code
* never infer undocumented behavior
* never invent architecture
* never speculate

If evidence is insufficient:

* omit the Q&A

If the snippet contains only:

* imports
* boilerplate
* comments
* trivial getters/setters
* declarations without behavior

return an empty array.

---

# Success Criteria

The sprint is successful when:

* Engineers can understand unfamiliar code without reading every file.
* Retrieved Q&A explains **why** code exists, not only **what** it does.
* Retrieved knowledge assists in making safe modifications.
* Questions are reusable across future development and maintenance.
* Generated concepts naturally form the basis of an AI-native software knowledge graph.

---

# Future Work

This sprint lays the foundation for future capabilities, including:

* automatic OKF concept generation
* cross-file reasoning
* architectural dependency graphs
* modification impact analysis
* implementation playbooks
* debugging guides
* design decision capture
* repository-wide engineering knowledge graphs

Rather than treating the prompt as a simple Q&A generator, this sprint establishes it as the **Engineering Knowledge Extraction Engine (EKE)**—the core intelligence responsible for transforming source code into durable, actionable engineering knowledge that powers the entire AI Code Library.

