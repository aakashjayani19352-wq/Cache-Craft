"""
build_report/chapters_6_to_10.py — Chapters 6 through 10 of Cache-Craft Final Hard-Bound Report.
Covers System Analysis & Design, Technology Stack, System Implementation, Testing & Validation,
and Results & Performance Analysis with high-resolution visual embeddings and empirical tables.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from build_report.styles import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BODY,
    add_h1, add_h2, add_h3, add_p, add_bullet, add_styled_table,
    add_figure, add_callout, add_code_snippet
)
from build_report.metadata import (
    MODULE_DESIGN_DATA, DATABASE_SCHEMA_DATA, TECH_SELECTION_RATIONALE_DATA,
    API_ENDPOINTS_DATA, UNIT_TESTS_DATA, FUNCTIONAL_TESTS_DATA,
    INTEGRATION_TESTS_DATA, SYSTEM_TESTS_DATA, PERFORMANCE_TESTS_DATA,
    UAT_TESTS_DATA, DEFECTS_BUGS_RESOLUTION_DATA, OBJECTIVE_ACHIEVEMENTS_DATA,
    THRESHOLD_SWEEP_DATA, BASELINE_COMPARISON_DATA
)

def build_chapters_6_to_10(doc):
    """Builds Chapters 6 through 10 with complete architectural narratives and diagrams."""

    # =========================================================================
    # CHAPTER 6: SYSTEM ANALYSIS AND DESIGN
    # =========================================================================
    add_h1(doc, "CHAPTER 6\nSYSTEM ANALYSIS AND DESIGN")

    add_h2(doc, "6.1 Existing System / Current Practice")
    add_p(
        doc,
        "In current generative AI and enterprise RAG implementations, client applications interact with large language models "
        "through naive request-response loops. Each incoming user query is tokenized, enriched with vector-retrieved context chunks, "
        "and transmitted directly to a commercial cloud LLM API endpoint (e.g., OpenAI GPT-4 or Google Gemini). Under this traditional "
        "architecture, the system treats every incoming request as entirely novel.",
        space_after=8
    )
    add_p(
        doc,
        "This architectural pattern exhibits critical structural deficiencies:\n"
        "1. Complete Redundancy: Up to 68% of enterprise queries in customer support and documentation search are paraphrased "
        "variations of previously resolved questions, yet they trigger full cloud LLM generation.\n"
        "2. Costly Token Consumption: Every duplicate query consumes hundreds of input and output tokens, multiplying cloud costs.\n"
        "3. High Unmitigated Latency: Round-trip times consistently range from 1,800 to 4,000 milliseconds, degrading UX.\n"
        "4. Vulnerability to Cloud Outages: Any upstream disruption (HTTP 503 high demand or HTTP 429 quota exhaustion) causes total service outage.",
        space_after=12
    )

    add_h2(doc, "6.2 Proposed System")
    add_p(
        doc,
        "Cache-Craft fundamentally reimagines LLM inference by introducing an autonomous, multi-tier semantic caching middleware. "
        "The proposed system sits transparently between user clients and foundation LLMs, intercepting queries and evaluating them "
        "across a three-tier hierarchical cache before invoking expensive generative intelligence.",
        space_after=8
    )
    add_p(
        doc,
        "Key architectural innovations of the proposed system include:\n"
        "• L0 Sub-Millisecond Exact Match Bypass: Evaluates SHA-256 query hashes in memory, returning identical matches in <2 ms.\n"
        "• L2 High-Performance Semantic Vector Cache: Uses sentence-transformers/all-MiniLM-L6-v2 and PostgreSQL 16 pgvector HNSW "
        "indexing to evaluate cosine similarity in ~25 ms, retrieving semantically identical answers.\n"
        "• Dynamic Threshold Slider: Allows operators to tune similarity sensitivity (tau = 0.50 to 1.00) in real time.\n"
        "• Multi-Turn Context-Aware Partition Isolation: Prevents conversational follow-up questions from colliding with parent queries.\n"
        "• Automated Cloud-to-Local Fallback: Seamlessly falls back from Google Gemini to local Ollama llama3.2 during outages.\n"
        "• Hardware Device Security Boundary: Enforces host signature verification to protect local GPU resources from external clients.",
        space_after=12
    )

    add_h2(doc, "6.3 System Architecture")
    add_p(
        doc,
        "The system architecture of Cache-Craft is decoupled into four logical layers: (1) Client Presentation Tier, (2) Middleware "
        "Routing Tier, (3) Storage & Vector Indexing Tier, and (4) Generative Intelligence Tier. Figure 6.1 illustrates this architecture.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/arch_diagram_v4.png",
        "6.1",
        "High-Performance Multi-Tier System Architecture Diagram (L0/L1/L2 Hierarchy)",
        width_inches=5.8
    )
    add_p(
        doc,
        "As shown in Figure 6.1, the Next.js 15 presentation layer communicates with the FastAPI middleware via asynchronous REST endpoints "
        "and Server-Sent Events (SSE). Incoming queries undergo text normalization and SHA-256 hashing. If an L0 exact match is found, "
        "the response is returned in <2 ms. If missed, the 384-dimensional dense embedding is generated and queried against the "
        "PostgreSQL 16 pgvector HNSW index. If cosine similarity meets the threshold (tau), the cached answer is returned in ~25 ms. "
        "Upon a cache miss, the query routes to Google Gemini Cloud, which automatically falls back to local Ollama llama3.2 upon failure. "
        "The newly generated answer is asynchronously stored in the cache for future acceleration.",
        space_after=12
    )

    add_h2(doc, "6.4 Workflow / Process Flow")
    add_p(
        doc,
        "The operational lifecycle of every query is governed by an autonomous multi-tier decision tree. Figure 6.2 details the "
        "decision branching logic executed by the middleware router.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/flowchart_decision_tree.png",
        "6.2",
        "Autonomous Semantic Routing Decision Tree and Multi-Tier Logic Flowchart",
        width_inches=5.8
    )

    add_h2(doc, "6.5 UML / Design Diagrams")
    add_p(
        doc,
        "To provide rigorous object-oriented and structural documentation, Figure 6.3 presents a multi-panel UML design depicting the "
        "Class Hierarchy, Sequence Flow, and Component Architecture of Cache-Craft.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/uml_diagram.png",
        "6.3",
        "Multi-Panel UML Class, Sequence, and Component Architecture Diagrams",
        width_inches=5.8
    )
    add_p(
        doc,
        "Figure 6.4 illustrates the physical deployment block diagram, depicting the hardware compute boundaries, Docker container "
        "network segmentation, GPU hardware allocation, and client-server boundaries.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/block_diagram.png",
        "6.4",
        "Hardware Infrastructure and Middleware Layer Physical Block Diagram",
        width_inches=5.8
    )

    add_h2(doc, "6.6 Module-wise Detailed Design")
    add_p(
        doc,
        "The system is decomposed into seven decoupled, single-responsibility modules. Table 6.1 documents their architectural "
        "responsibilities, input-output contracts, and primary source implementations.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Module Name", "Architectural Functionality", "Input Contract", "Output Contract", "Source File"],
        MODULE_DESIGN_DATA,
        col_widths=[1.5, 2.0, 1.2, 1.3, 1.0],
        caption="Table 6.1: Module-wise Architectural Design and Functional Responsibilities"
    )

    add_h2(doc, "6.7 Database / Relational pgvector Data Design")
    add_p(
        doc,
        "The data layer utilizes PostgreSQL 16 extended with pgvector v0.7.0. Table 6.2 documents the relational schema, field types, "
        "constraints, and indexing strategies.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Table Name", "Column Identifier", "PostgreSQL Data Type", "Constraint & Engineering Context"],
        DATABASE_SCHEMA_DATA,
        col_widths=[1.4, 1.4, 1.8, 2.4],
        caption="Table 6.2: PostgreSQL Database Schema and pgvector Index Definitions"
    )

    add_h2(doc, "6.8 User Interface & Experience Design System")
    add_p(
        doc,
        "The user interface is designed as an Apple-grade, high-contrast dark dashboard with glassmorphism aesthetics. Key UI features include:\n"
        "• Real-Time Stat Cards: Four header cards display Total Queries, Cache Hits, Semantic Hit Rate %, and Average Speedup Factor, "
        "polling the backend every 5 seconds or streaming via SSE.\n"
        "• Interactive Chat Playground: Features a conversational layout where user prompts appear as blue bubbles and AI responses "
        "appear with color-coded badges (green for CACHE_HIT with latency and similarity score; red for CACHE_MISS).\n"
        "• Prompt History Recall: Up-Arrow keyboard listener allows instant retrieval of previous prompts for immediate L0 hit demonstrations.\n"
        "• Persistent State Navigation: Chat messages and active states persist across sidebar navigation tabs using client-side React state.\n"
        "• Vector Cache Explorer: A searchable card grid displaying cached queries, hit counts, and response excerpts with on-demand clearing.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 7: TECHNOLOGY STACK AND DEVELOPMENT ENVIRONMENT
    # =========================================================================
    add_h1(doc, "CHAPTER 7\nTECHNOLOGY STACK AND DEVELOPMENT ENVIRONMENT")

    add_h2(doc, "7.1 Programming Languages")
    add_p(
        doc,
        "Cache-Craft uses a modern polyglot technology stack optimized for high-performance AI systems engineering:\n"
        "• Python 3.11.9: Powers the backend API and machine learning pipeline, leveraging asynchronous asyncio, type hints, and PyTorch.\n"
        "• TypeScript 5.0: Powers the frontend Next.js application, ensuring end-to-end type safety and eliminating runtime errors.\n"
        "• SQL / PL/pgSQL: Powers vector queries, HNSW index definitions, and database maintenance in PostgreSQL 16.",
        space_after=8
    )

    add_h2(doc, "7.2 Frameworks, Libraries & External APIs")
    add_p(
        doc,
        "Core software libraries include:\n"
        "• FastAPI 0.115.0: Asynchronous web framework offering high throughput, Pydantic validation, and SSE streaming.\n"
        "• sentence-transformers 3.0.1: PyTorch-based embedding framework running all-MiniLM-L6-v2 for 384-d vector generation.\n"
        "• Google Gemini API: Cloud foundation model endpoint utilizing gemini-3.8-flash for high-speed inference.\n"
        "• Ollama 0.3.12: Local inference runtime serving 4-bit quantized llama3.2 (3B parameters) for offline fallback.\n"
        "• Next.js 15.0 + React 19: Full-stack React framework with App Router, server/client components, and Tailwind CSS 3.4.",
        space_after=8
    )

    add_h2(doc, "7.3 Database & In-Memory Storage Systems")
    add_p(
        doc,
        "Storage consists of PostgreSQL 16 with pgvector v0.7.0 for ACID-compliant relational storage and HNSW vector index acceleration, "
        "coupled with Redis 7.2 for in-memory session buffering, and SQLite3 as an embedded lightweight fallback.",
        space_after=8
    )

    add_h2(doc, "7.4 Hardware, Cloud & Deployment Environments")
    add_p(
        doc,
        "The production deployment leverages a modern cloud container topology:\n"
        "• Frontend: Deployed on Vercel's global edge network (https://cache-craft.vercel.app).\n"
        "• Backend & Storage: Containerized via Docker and deployed on Railway cloud infrastructure.\n"
        "• Local Development: Orchestrated using Docker Desktop with WSL2 Ubuntu backend on the host engineering workstation.",
        space_after=8
    )

    add_h2(doc, "7.5 Development, Version Control & Testing Tooling")
    add_p(
        doc,
        "Development utilized Visual Studio Code with Python and TypeScript extensions, Git for distributed version control hosted "
        "on GitHub, pytest for unit and functional test automation, and Postman for API testing.",
        space_after=8
    )

    add_h2(doc, "7.6 Technology Selection Rationale")
    add_p(
        doc,
        "Every technology in Cache-Craft was selected after rigorous architectural trade-off analysis. Table 7.6 details the rationale.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Architectural Decision", "Selected Technology", "Engineering Justification & Trade-Off Analysis"],
        TECH_SELECTION_RATIONALE_DATA,
        col_widths=[2.0, 1.8, 3.2],
        caption="Table 7.6: Technology Selection Rationale and Architectural Trade-Off Analysis"
    )

    # =========================================================================
    # CHAPTER 8: SYSTEM IMPLEMENTATION
    # =========================================================================
    add_h1(doc, "CHAPTER 8\nSYSTEM IMPLEMENTATION")

    add_h2(doc, "8.1 Implementation Architecture Overview")
    add_p(
        doc,
        "Cache-Craft is implemented as a clean, modular Python and TypeScript codebase located across the core/ backend directory "
        "and the frontend/ web application directory. The core execution pipeline orchestrates query intake, vectorization, multi-tier "
        "routing, LLM invocation, and telemetry streaming.",
        space_after=8
    )

    add_h2(doc, "8.2 Module 1: Multi-Tier Cache Router Core")
    add_p(
        doc,
        "Implemented in core/cache_router.py, the router coordinates the L0, L1, and L2 tiers. It normalizes inbound query strings "
        "(lowercasing, trimming whitespace, removing trailing punctuation) and generates an SHA-256 hash. If an L0 exact match exists, "
        "the cached response is returned immediately in under 2 ms. If absent, the router triggers L2 semantic vector evaluation.",
        space_after=8
    )

    add_h2(doc, "8.3 Module 2: Dense Vector Embedding & Normalization Engine")
    add_p(
        doc,
        "The embedding engine employs the all-MiniLM-L6-v2 model via sentence-transformers. Inbound queries are tokenized and mapped "
        "to 384-dimensional dense vectors. Critically, embeddings undergo L2 unit normalization such that ||v|| = 1.0. This ensures that "
        "cosine distance is directly proportional to Euclidean distance, maximizing vector comparison throughput.",
        space_after=8
    )

    add_h2(doc, "8.4 Module 3: Dynamic Multi-LLM Router & Failover Engine")
    add_p(
        doc,
        "Implemented in core/llm_client.py, this module wraps both Google Gemini 3.8 Flash and local Ollama llama3.2. When a cache miss "
        "occurs, the query routes first to Google Gemini. If Gemini returns an HTTP 503 high demand error, HTTP 429 quota exhaustion, "
        "or connection timeout, the failover circuit catches the exception and immediately invokes the local Ollama daemon without "
        "propagating errors to the user.",
        space_after=8
    )

    add_h2(doc, "8.5 Module 4: Hardware Device Authorization & Isolation Boundary")
    add_p(
        doc,
        "Implemented in core/device_auth.py, this security module inspects incoming client network signatures and remote IP addresses. "
        "Local requests originating from loopback (127.0.0.1, ::1) or authorized local subnet addresses are permitted to trigger local "
        "Ollama GPU inference. Requests from unauthorized external web clients are blocked from consuming host GPU resources, returning "
        "an informative security alert while preserving cloud LLM functionality.",
        space_after=8
    )

    add_h2(doc, "8.6 Module 5: Real-Time Observability & SSE Telemetry Engine")
    add_p(
        doc,
        "Telemetry is managed in main.py via the /api/metrics and /api/metrics/stream endpoints. The engine computes cumulative total "
        "queries, cache hits, misses, semantic hit rate %, average hit latency, average miss latency, speedup factors, and estimated "
        "token cost savings, streaming real-time updates to connected clients via Server-Sent Events.",
        space_after=8
    )

    add_h2(doc, "8.7 Module 6: Interactive Web Dashboard & Chat Playground")
    add_p(
        doc,
        "Implemented in frontend/src/app/, the web interface features a modern dark-glassmorphism dashboard with four panels: "
        "(1) Overview Dashboard with live metrics, (2) Chat Playground with hit/miss badges and up-arrow prompt history, (3) Vector "
        "Cache Explorer with entry cards and delete controls, and (4) Settings with dynamic threshold tuning sliders.",
        space_after=8
    )

    add_h2(doc, "8.8 Module 7: Automated Benchmarking & Matrix Validation Suite")
    add_p(
        doc,
        "Implemented in seed_cache.py, the benchmark suite evaluates 1,200 curated queries across thresholds tau = 0.50 to 0.95. "
        "It vectorizes distance calculations using NumPy matrix dot products (np.dot(eval_mat, seed_mat.T)), computing True Positives, "
        "False Positives, False Negatives, True Negatives, Precision, Recall, and F1-scores in under 2 seconds.",
        space_after=12
    )

    add_h2(doc, "8.9 Mathematical Formulations: Cosine Metric & HNSW Graph Indexing")
    add_p(
        doc,
        "The mathematical foundation of Cache-Craft rests on cosine similarity in unit-normalized vector space. Given query vector q "
        "and cached vector c, cosine similarity S_cos(q, c) is defined as:\n\n"
        "    S_cos(q, c) = (q · c) / (||q|| · ||c||)\n\n"
        "Because embeddings are pre-normalized such that ||q|| = ||c|| = 1.0, the calculation simplifies to the dot product:\n\n"
        "    S_cos(q, c) = q · c = sum(q_i · c_i) for i = 1 to 384\n\n"
        "In PostgreSQL pgvector, the cosine distance operator <=> computes:\n\n"
        "    D_cos(q, c) = 1 - S_cos(q, c)\n\n"
        "A cache hit occurs when D_cos(q, c) <= (1 - tau), where tau is the similarity threshold. The HNSW index accelerates nearest "
        "neighbor search with parameters m = 16 (bi-directional links per node) and ef_construction = 64 (size of dynamic candidate list), "
        "providing logarithmic search complexity O(log N).",
        space_after=12
    )

    add_h2(doc, "8.10 RESTful API Endpoints Specification")
    add_p(
        doc,
        "The FastAPI backend exposes a clean RESTful interface. Table 8.1 details the complete endpoint specification.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["HTTP Method", "Endpoint URI", "Functional Description", "Request Contract", "Response Contract"],
        API_ENDPOINTS_DATA,
        col_widths=[1.0, 1.8, 1.8, 1.2, 1.2],
        caption="Table 8.1: Cache-Craft RESTful API Endpoints Specification"
    )

    add_h2(doc, "8.11 Database Implementation & pgvector DDL Excerpts")
    add_p(
        doc,
        "Below is an excerpt of the core DDL script that initializes the pgvector extension, table schemas, and HNSW index in PostgreSQL:",
        space_after=4
    )
    add_code_snippet(
        doc,
        "-- PostgreSQL 16 pgvector Initialization DDL\n"
        "CREATE EXTENSION IF NOT EXISTS vector;\n\n"
        "CREATE TABLE IF NOT EXISTS semantic_cache (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    query_text TEXT NOT NULL,\n"
        "    query_hash VARCHAR(64) UNIQUE NOT NULL,\n"
        "    response_text TEXT NOT NULL,\n"
        "    embedding vector(384),\n"
        "    hit_count INTEGER DEFAULT 1,\n"
        "    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\n"
        "    expires_at TIMESTAMP WITH TIME ZONE\n"
        ");\n\n"
        "CREATE INDEX IF NOT EXISTS idx_semantic_cache_hnsw\n"
        "ON semantic_cache USING hnsw (embedding vector_cosine_ops)\n"
        "WITH (m = 16, ef_construction = 64);\n\n"
        "CREATE INDEX IF NOT EXISTS idx_query_hash ON semantic_cache(query_hash);"
    )

    add_h2(doc, "8.12 Security Architecture, CORS & GPU Access Control")
    add_p(
        doc,
        "Security is enforced at multiple layers:\n"
        "• CORS Middleware: Restricts cross-origin browser requests to authorized origins (Vercel frontend domain).\n"
        "• Environment Isolation: API keys (GEMINI_API_KEY) and database credentials are injected via environment variables (.env).\n"
        "• Hardware Boundary Protection: device_auth.py prevents remote web clients from invoking local GPU Ollama inference.\n"
        "• SQL Injection Prevention: All database queries utilize parameterized SQL statements via psycopg2, preventing injection.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 9: TESTING AND VALIDATION
    # =========================================================================
    add_h1(doc, "CHAPTER 9\nTESTING AND VALIDATION")

    add_h2(doc, "9.1 Multi-Tiered Testing Strategy & Verification Methodology")
    add_p(
        doc,
        "Quality assurance for Cache-Craft followed a rigorous multi-tiered verification methodology spanning six testing dimensions: "
        "Unit Testing (25 tests), Functional Testing (40 tests), Integration Testing (35 tests), System Testing (25 tests), "
        "Performance Testing (20 tests), and User Acceptance Testing (18 tests). In total, 163 distinct test cases were executed, "
        "achieving a 100% pass rate (163/163 passed).",
        space_after=10
    )

    add_h2(doc, "9.2 Unit and Module Testing Suite (25 Tests)")
    add_p(
        doc,
        "Unit tests validated low-level functions including embedding dimensions, vector normalization, hash generation, and distance formulas. "
        "Table 9.1 documents key representative test cases from the 25 unit tests.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Test ID", "Component Under Test", "Test Condition & Input", "Expected Verification Criteria", "Status"],
        UNIT_TESTS_DATA,
        col_widths=[1.2, 1.8, 2.2, 1.3, 0.7],
        caption="Table 9.1: Unit and Module Testing Test Cases (25 Tests)"
    )

    add_h2(doc, "9.3 Functional Testing Suite (40 Tests)")
    add_p(
        doc,
        "Functional tests verified end-to-end features including exact hits, semantic hits, misses, dynamic threshold updates, and cache clearing. "
        "Table 9.2 documents key representative test cases from the 40 functional tests.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Test ID", "Feature Under Test", "Execution Scenario", "Expected Outcome", "Status"],
        FUNCTIONAL_TESTS_DATA,
        col_widths=[1.2, 1.8, 2.2, 1.3, 0.7],
        caption="Table 9.2: Functional Testing Test Cases (40 Tests)"
    )

    add_h2(doc, "9.4 Integration Testing Suite (35 Tests)")
    add_p(
        doc,
        "Integration tests verified cross-service communications between FastAPI, PostgreSQL pgvector, Redis, Ollama, Gemini API, and Next.js. "
        "Table 9.3 documents key representative test cases from the 35 integration tests.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Test ID", "Subsystem Boundary", "Integration Scenario", "Verification Criteria", "Status"],
        INTEGRATION_TESTS_DATA,
        col_widths=[1.2, 1.8, 2.2, 1.3, 0.7],
        caption="Table 9.3: Integration Testing Test Cases (35 Tests)"
    )

    add_h2(doc, "9.5 System and Resilience Testing Suite (25 Tests)")
    add_p(
        doc,
        "System tests validated full end-to-end query lifecycles, container cold starts, network interruptions, and automated failover. "
        "Table 9.4 documents key representative test cases from the 25 system tests.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Test ID", "System Scenario", "Execution Condition", "Verification Criteria", "Status"],
        SYSTEM_TESTS_DATA,
        col_widths=[1.2, 1.8, 2.2, 1.3, 0.7],
        caption="Table 9.4: End-to-End System and Resilience Testing Test Cases (25 Tests)"
    )

    add_h2(doc, "9.6 Performance, Load & Concurrency Testing Suite (20 Tests)")
    add_p(
        doc,
        "Performance tests profiled latency, sustained throughput (RPS), and memory consumption under concurrent load. "
        "Table 9.5 documents key representative test cases from the 20 performance tests.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Test ID", "Performance Metric", "Load Condition & Scenario", "Measured Result", "Status"],
        PERFORMANCE_TESTS_DATA,
        col_widths=[1.2, 1.8, 2.2, 1.3, 0.7],
        caption="Table 9.5: Performance, Load, and Concurrency Testing Test Cases (20 Tests)"
    )

    add_h2(doc, "9.7 User Acceptance Testing (UAT) Scenarios (18 Tests)")
    add_p(
        doc,
        "User acceptance testing evaluated usability, prompt history recall, sidebar layout, and hardware alerts with student evaluators. "
        "Table 9.6 documents key representative test cases from the 18 UAT scenarios.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Test ID", "Usability Scenario", "Evaluation Step & Criteria", "Evaluator Finding", "Status"],
        UAT_TESTS_DATA,
        col_widths=[1.2, 1.8, 2.2, 1.3, 0.7],
        caption="Table 9.6: User Acceptance Testing Usability Scenarios (18 Tests)"
    )

    add_h2(doc, "9.8 Experimental Validation on 1,200 Benchmark Corpus")
    add_p(
        doc,
        "Empirical validation was performed across the curated 1,200-query benchmark corpus (500 seeds, 500 paraphrases, 200 unrelated). "
        "With 500 seed queries cached, 700 evaluation queries were submitted across similarity thresholds tau = 0.70 to 0.95. "
        "At tau = 0.70, Cache-Craft achieved 481 True Positives, 0 False Positives, 19 False Negatives, and 200 True Negatives, "
        "yielding 100.0% precision, 96.20% recall, and an F1-score of 0.9806.",
        space_after=12
    )

    add_h2(doc, "9.9 Defects Discovered, Root Causes & Technical Resolutions")
    add_p(
        doc,
        "During system development and benchmarking, five major architectural defects were discovered, diagnosed, and resolved. "
        "Table 9.7 documents the defects, severities, root causes, and technical resolutions.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Bug ID", "Defect Description", "Severity", "Root Cause Analysis", "Technical Resolution", "Status"],
        DEFECTS_BUGS_RESOLUTION_DATA,
        col_widths=[0.8, 1.8, 0.8, 1.8, 1.4, 0.6],
        caption="Table 9.7: Major Defects Discovered, Root Causes, and Technical Resolutions"
    )

    add_h2(doc, "9.10 Final Validation Statement")
    add_p(
        doc,
        "Based on the execution and verification of all 163 software test cases across unit, functional, integration, system, performance, "
        "and user acceptance testing suites, Cache-Craft has successfully satisfied all functional and non-functional requirements. "
        "The system demonstrated 100.0% test pass fidelity, zero unhandled runtime exceptions, and verified operational readiness.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 10: RESULTS AND PERFORMANCE ANALYSIS
    # =========================================================================
    add_h1(doc, "CHAPTER 10\nRESULTS AND PERFORMANCE ANALYSIS")

    add_h2(doc, "10.1 Final Empirical Results Summary")
    add_p(
        doc,
        "The empirical results substantiate the core research hypothesis: multi-tier semantic caching dramatically reduces inference "
        "latency and financial expenditures while preserving 100% semantic precision. The system achieved a 68.71% semantic hit rate, "
        "a 3.2x end-to-end speedup factor, and a 68.71% token cost reduction at optimal threshold tau = 0.70.",
        space_after=8
    )

    add_h2(doc, "10.2 Objective-wise Milestone Achievement")
    add_p(
        doc,
        "Table 10.1 evaluates the final performance achievements against the seven primary engineering objectives established in Chapter 1.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Project Objective", "Quantitative Target", "Final Achieved Metric (Empirical)", "Status"],
        OBJECTIVE_ACHIEVEMENTS_DATA,
        col_widths=[1.8, 2.0, 2.4, 1.0],
        caption="Table 10.1: Objective-wise Milestone and Metric Achievement Summary"
    )

    add_h2(doc, "10.3 Similarity Threshold Sweep & Metric Analysis")
    add_p(
        doc,
        "To identify the optimal mathematical operating point, an exhaustive threshold sweep was conducted from tau = 0.70 to 0.95 across "
        "the 700 evaluation queries. Table 10.2 presents the complete confusion matrix, precision, recall, F1-scores, latencies, speedup, "
        "and cost reductions.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Threshold (\\tau)", "TP", "FP", "FN", "TN", "Precision", "Recall", "F1", "Hit Rate", "Hit Lat.", "Avg Lat.", "Speedup", "Cost Sav."],
        THRESHOLD_SWEEP_DATA,
        col_widths=[1.0, 0.4, 0.4, 0.4, 0.4, 0.7, 0.7, 0.7, 0.7, 0.7, 0.8, 0.6, 0.7],
        caption="Table 10.2: Empirical Similarity Threshold Sweep and Benchmark Evaluation (N=700)"
    )

    add_h2(doc, "10.4 Baseline Comparative Results")
    add_p(
        doc,
        "Table 10.3 compares Cache-Craft against the two industry baselines: (1) Direct LLM inference (no caching), and (2) Exact-Match "
        "caching (Redis SHA-256 only) on paraphrased queries.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["System Architecture", "Hit Rate", "Average Latency", "Speedup", "Cost ($)", "Savings", "Operational Behavior"],
        BASELINE_COMPARISON_DATA,
        col_widths=[1.8, 0.8, 1.0, 0.9, 0.8, 0.8, 1.1],
        caption="Table 10.3: Baseline Comparative Results (Direct LLM vs. Exact Hash vs. Cache-Craft)"
    )

    add_h2(doc, "10.5 Empirical Charts & Production Screenshots")
    add_p(
        doc,
        "Figure 10.1 illustrates the empirical latency reduction and cost curves across benchmark trials, showing the 3.2x speedup and 68.71% savings.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/benchmark_chart.png",
        "10.1",
        "Empirical Latency Profiling and Cloud Cost Reduction Benchmark Curves",
        width_inches=5.8
    )

    add_p(
        doc,
        "Figure 10.2 presents the threshold sensitivity analysis, highlighting the optimal F1-score peak at tau = 0.70 and the trade-off "
        "between precision and recall as thresholds increase toward 0.95.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/benchmark_deep_dive.png",
        "10.2",
        "Threshold Sensitivity vs. Precision, Recall, and F1-Score Trade-Off Analysis",
        width_inches=5.8
    )

    add_p(
        doc,
        "Figure 10.3 displays the Next.js 15 Overview Dashboard, showcasing real-time stat cards, hit rate gauges, and recent query history.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/1_dashboard_overview.png",
        "10.3",
        "Next.js 15 Web Dashboard and Real-Time Telemetry Overview",
        width_inches=5.8
    )

    add_p(
        doc,
        "Figure 10.4 shows the Interactive Chat Playground with color-coded badges indicating CACHE_HIT (green) with latency and similarity score.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/2_chat_playground.png",
        "10.4",
        "Interactive Semantic Chat Playground with L1 Cache-Hit Highlighting",
        width_inches=5.8
    )

    add_p(
        doc,
        "Figure 10.5 displays the Vector Cache Explorer, providing a searchable card grid of cached knowledge entries and hit counts.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/3_cache_explorer.png",
        "10.5",
        "Vector Cache Explorer and Semantic Inverted Index Browser",
        width_inches=5.8
    )

    add_p(
        doc,
        "Figure 10.6 shows the Settings panel featuring the dynamic threshold tuning slider and hardware device authorization controls.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/3_settings_controls.png",
        "10.6",
        "Dynamic Similarity Threshold Controls and Device Authorization Panel",
        width_inches=5.8
    )

    add_h2(doc, "10.6 Results Discussion")
    add_p(
        doc,
        "The empirical findings provide critical insights for systems engineers deploying semantic caching in production:\n"
        "1. Threshold Selection: Operating at tau = 0.70 is optimal for general English NLP queries, achieving 100% precision with zero "
        "false positives and a near-perfect F1 of 0.9806. Higher thresholds (e.g., tau = 0.95) are overly strict, dropping recall to 76.2%.\n"
        "2. Exact Match Synergy: L0 exact hash bypass handles repeated identical queries in 1.84 ms, offloading vector database compute.\n"
        "3. Economic Viability: Reducing API expenditures by 68.71% yields substantial savings at enterprise scale, where millions of "
        "tokens are consumed daily.",
        space_after=12
    )
