Deterministic Hybrid Agentic AI Platform
Overview

This project implements a deterministic, LangGraph-based AI orchestration system designed for:

Hardware-aware execution (8GB RAM + GTX 1650)

GPU-first inference

Open-source LLM usage only

Hybrid retrieval (BM25 + Semantic API fallback)

Full traceability and replayability

Deterministic state transitions

Core Philosophy

LLMs do NOT control workflow.

LangGraph encodes allowed transitions.

All states are typed and validated.

Every execution is traceable.

System is fully testable with pytest.

Architecture Overview

flowchart TD

    USER["User Request"]
    API["FastAPI Layer"]
    GRAPH["LangGraph StateGraph Orchestrator"]

    USER --> API
    API --> GRAPH

    GRAPH --> INTENT["Intent Classifier (Local GPU LLM)"]
    INTENT --> ROUTER{Deterministic Routing}

    ROUTER --> JOB[Job Agent]
    ROUTER --> RESUME[Resume Agent]
    ROUTER --> RAG[RAG Agent]

    RAG --> BM25[BM25 Retrieval]
    BM25 --> CONF{Confidence Threshold Met?}

    CONF -->|Yes| LOCAL_FUSION[Local LLM Fusion]
    CONF -->|No| EMB[HF Embedding API]
    EMB --> RERANK[Semantic Rerank]
    RERANK --> HF_REASON[HF LLM Deep Reasoning]

    JOB --> VALIDATOR[Validator]
    RESUME --> VALIDATOR
    LOCAL_FUSION --> VALIDATOR
    HF_REASON --> VALIDATOR

    VALIDATOR --> LOG["Trace Logger + SQLite Checkpoint"]
    LOG --> END_SUCCESS([END_SUCCESS])

    VALIDATOR --> END_FAILURE([END_FAILURE])


Used for:

Intent classification

Validation

Short reasoning

Formatting

Runs:

GPU-first

CPU fallback

Tier 2 – Hugging Face Inference API (Open Source Models)

Used for:

Deep reasoning

Long-context synthesis

Complex RAG fusion

Example models:

Mixtral

Qwen

DeepSeek

Retrieval Strategy

Primary:

BM25 (rank-bm25)

Fallback:

Hugging Face embedding API

Semantic rerank

Deep reasoning via HF LLM

This ensures:

Low latency by default

Heavy reasoning only when needed

Deterministic Orchestration

LangGraph controls:

Allowed transitions

Forbidden transitions

Explicit END states

Retry limits

Failure routing

LLM never decides graph flow.

Observability

SQLite trace store

Node-level logging

State transition logs

Execution replay capability

Testing Strategy

Using pytest:

Unit tests for nodes

Graph transition tests

Golden trace validation

Performance benchmarks

Failure path testing

Hardware Optimization

Target system:

8GB RAM

GTX 1650 GPU (4GB VRAM)

Design choices:

Quantized models

GPU-first inference

BM25 primary retrieval

Remote embedding fallback