"""
build_report/chapters_1_to_5.py — Chapters 1 through 5 of Cache-Craft Final Hard-Bound Report.
Covers Introduction, Organization Profile, Literature Review, Requirements Analysis, and Methodology.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from build_report.styles import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BODY,
    add_h1, add_h2, add_h3, add_p, add_bullet, add_styled_table,
    add_figure, add_callout
)
from build_report.metadata import (
    PROJECT_TITLE, FULL_PROJECT_TITLE, STUDENT_NAME, ENROLLMENT_NO,
    PROGRAM_NAME, SEMESTER, INSTITUTE_MENTOR, INSTITUTE_NAME, SCHOOL_NAME,
    DEPARTMENT_NAME, ACADEMIC_YEAR,
    SCOPE_MATRIX_DATA, EXPECTED_VS_FINAL_DATA, WORKSTATION_SPECS_DATA,
    EXISTING_APPROACHES_DATA, COMPARATIVE_MATRIX_DATA,
    FUNCTIONAL_REQUIREMENTS_DATA, NON_FUNCTIONAL_REQUIREMENTS_DATA,
    HARDWARE_REQUIREMENTS_DATA, SOFTWARE_REQUIREMENTS_DATA, DATASET_REQUIREMENTS_DATA,
    PROJECT_PHASES_DATA, PROGRESS_REPORTS_CONSOLIDATION_DATA, PROJECT_SCHEDULE_GANTT_DATA
)

def build_chapters_1_to_5(doc):
    """Builds Chapters 1 through 5, setting up Section 2 with Arabic page numbers."""
    sec2 = doc.add_section()
    sec2.page_width = Inches(8.27)
    sec2.page_height = Inches(11.69)
    sec2.left_margin = Inches(1.25)
    sec2.right_margin = Inches(1.0)
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(0.75)

    # Set Arabic (decimal) page numbering starting at 1
    sectPr2 = sec2._sectPr
    pgNumType2 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>')
    sectPr2.append(pgNumType2)

    # Header configuration
    sec2.header.is_linked_to_previous = False
    hp2 = sec2.header.paragraphs[0]
    hp2.text = f"{PROJECT_TITLE}\t{INSTITUTE_NAME} | {SCHOOL_NAME}"
    hp2.runs[0].font.name = 'Cambria'
    hp2.runs[0].font.size = Pt(8.5)
    hp2.runs[0].font.color.rgb = RGBColor(120, 120, 120)

    # Footer configuration
    sec2.footer.is_linked_to_previous = False
    fp2 = sec2.footer.paragraphs[0]
    fp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld2 = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    fp2._p.append(fld2)

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_h1(doc, "CHAPTER 1\nINTRODUCTION", page_break=False)

    add_h2(doc, "1.1 Background of the Project")
    add_p(
        doc,
        "The contemporary computing landscape is experiencing an epochal paradigm shift driven by the rapid maturation and "
        "industrial integration of Large Language Models (LLMs) such as OpenAI's GPT-4, Google's Gemini, and Meta's Llama series. "
        "Enterprises and academic institutions increasingly deploy these models within Retrieval-Augmented Generation (RAG) pipelines "
        "to deliver conversational intelligence, code synthesis, document summarization, and customer support. By anchoring foundation "
        "models to external vector knowledge repositories, RAG frameworks dramatically reduce factual hallucinations and empower "
        "systems with domain-specific precision.",
        space_after=8
    )
    add_p(
        doc,
        "However, this widespread adoption has exposed severe operational vulnerabilities in modern AI architectures. Foundation "
        "model inference is compute-intensive, memory-bound, and economically costly. Cloud providers bill LLM access on a granular "
        "per-token consumption model, transforming high-traffic conversational workloads into substantial, recurring operational "
        "expenses. Concurrently, inference latency frequently ranges from 1,500 to over 4,000 milliseconds per query, severely "
        "degrading the user experience in interactive and real-time environments.",
        space_after=8
    )
    add_p(
        doc,
        "In traditional web systems, high latency and repeated computational costs are systematically mitigated through deterministic "
        "key-value caching mechanisms (such as Memcached or standard Redis). Unfortunately, deterministic caching relies on exact "
        "cryptographic key matching (e.g., SHA-256 string hashes). In generative AI applications, natural language queries expressing "
        "identical underlying user intent exhibit infinite lexical and syntactic variations (e.g., 'What is a semantic cache?' "
        "versus 'Can you explain semantic caching?'). Exact-match caches experience a near 100% miss rate against paraphrased inputs, "
        "forcing the underlying system to re-invoke expensive LLM inference repeatedly. Cache-Craft was conceived to solve this "
        "fundamental architectural bottleneck through high-performance semantic routing and multi-tier vector caching.",
        space_after=12
    )

    add_h2(doc, "1.2 Problem Statement")
    add_p(
        doc,
        "Modern LLM-powered applications suffer from three interrelated systemic deficiencies that constrain their scalability:",
        space_after=6
    )
    add_bullet(doc, " In conversational RAG systems, up to 60–70% of inbound queries in customer support and documentation search express semantic intent identical to previously resolved prompts. Due to lexical variations, current systems re-execute the entire RAG pipeline, generating millions of redundant tokens and wasting financial capital.", bold_prefix="1. Redundant Cloud API Expenditures:")
    add_bullet(doc, " End-to-end generation times spanning 2 to 4 seconds introduce cognitive friction, degrade conversational responsiveness, and prevent integration into latency-critical enterprise SLAs.", bold_prefix="2. Unacceptable Inference Latency:")
    add_bullet(doc, " Cloud LLM APIs are inherently susceptible to transient network congestion, rate limiting (HTTP 429), and upstream service outages (HTTP 503). Relying exclusively on single-provider cloud endpoints introduces a brittle single point of failure that halts customer workflows.", bold_prefix="3. Single-Point-of-Failure Fragility:")
    add_p(
        doc,
        "Formally, the engineering problem addressed by this project is: How can we architect an autonomous, low-overhead middleware "
        "that accurately determines semantic equivalence between incoming natural language prompts and historical responses in real "
        "time (<30 ms), serves verified answers from an optimized multi-tier cache, and dynamically orchestrates fallback between cloud "
        "and local LLM providers without sacrificing contextual precision or security?",
        space_after=12
    )

    add_h2(doc, "1.3 Need / Motivation for the Project")
    add_p(
        doc,
        "The motivation for Cache-Craft stems from both academic necessity and pressing industrial demand. As generative AI transitions "
        "from experimental prototypes to mission-critical infrastructure, computational efficiency and operational autonomy become "
        "paramount. Organizations cannot sustain exponentially growing cloud bills for queries their systems have already answered thousands "
        "of times. Furthermore, data privacy mandates require mechanisms that can keep sensitive user queries confined to local hardware "
        "without sacrificing performance.",
        space_after=8
    )
    add_p(
        doc,
        "By constructing a multi-tier semantic router that combines sub-millisecond cryptographic hash checks with dense vector similarity "
        "searches over an ACID-compliant PostgreSQL 16 pgvector store, Cache-Craft provides an enterprise-ready bridge between "
        "traditional caching performance and modern generative AI flexibility. Crucially, providing an automated local fallback engine "
        "(via Ollama llama3.2) alongside cloud intelligence (Google Gemini) democratizes resilient AI infrastructure.",
        space_after=12
    )

    add_h2(doc, "1.4 Objectives of the Project")
    add_p(
        doc,
        "The primary engineering and research objectives established for Cache-Craft are:",
        space_after=6
    )
    add_bullet(doc, "Construct a three-tier caching hierarchy incorporating an L0 sub-millisecond SHA-256 exact match bypass, an L1 in-memory session buffer, and an L2 persistent vector semantic cache.", bold_prefix="1. Multi-Tier Cache Hierarchy:")
    add_bullet(doc, "Integrate the lightweight sentence-transformers/all-MiniLM-L6-v2 model to project natural language queries into 384-dimensional unit-normalized dense embeddings within 10 milliseconds.", bold_prefix="2. Real-Time Vector Embedding:")
    add_bullet(doc, "Implement an accelerated Hierarchical Navigable Small World (HNSW) graph index in PostgreSQL pgvector to evaluate cosine distance (<=>) in sub-30 milliseconds.", bold_prefix="3. Sub-30ms Semantic Similarity Search:")
    add_bullet(doc, "Empirically evaluate precision, recall, F1-score, and cost curves across a curated 1,200-query benchmark corpus, identifying the optimal mathematical threshold (tau) to achieve 100% precision.", bold_prefix="4. Rigorous Mathematical Optimization:")
    add_bullet(doc, "Architect an automated fallback pipeline that seamlessly redirects traffic from Google Gemini Cloud to a local Ollama llama3.2 instance during API outages or rate limit spikes.", bold_prefix="5. Fault-Tolerant Multi-LLM Routing:")
    add_bullet(doc, "Implement referential intent detection and partition filtering in pgvector to prevent context collision and semantic drift between root queries and conversational follow-ups.", bold_prefix="6. Multi-Turn Context-Aware Caching:")
    add_bullet(doc, "Build an Apple-grade, responsive Next.js 15 dashboard featuring real-time Server-Sent Events (SSE) telemetry, chat playground, prompt history recall, and hardware device security boundaries.", bold_prefix="7. Modern Full-Stack Web Platform:")

    add_h2(doc, "1.5 Scope of the Project")
    add_p(
        doc,
        "The architectural scope of Cache-Craft covers the complete lifecycle of incoming natural language queries within text-based "
        "RAG and LLM systems. The project encompasses embedding generation, multi-tier cache evaluation, vector database indexing, "
        "cloud and local LLM orchestration, empirical benchmarking, and web telemetry. To maintain rigorous software engineering boundaries, "
        "Table 1.1 delineates the explicit scope matrix.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["In Scope (Delivered & Validated)", "Out of Scope (Boundaries)", "Architectural Remarks"],
        SCOPE_MATRIX_DATA,
        col_widths=[2.4, 2.2, 2.2],
        caption="Table 1.1: Cache-Craft Project Scope Matrix"
    )

    add_h2(doc, "1.6 Expected Outcomes vs. Final Achieved Outcomes")
    add_p(
        doc,
        "Throughout the four reporting milestones of the UDP lifecycle, project deliverables were tracked against quantitative "
        "engineering benchmarks. Table 1.2 presents the comparative evaluation of initial expectations versus final verified outcomes.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Performance Parameter", "Initial Expected Target", "Final Achieved Outcome (Empirical)"],
        EXPECTED_VS_FINAL_DATA,
        col_widths=[1.8, 2.5, 2.5],
        caption="Table 1.2: Expected vs. Final Achieved Project Outcomes"
    )

    add_h2(doc, "1.7 Report Organization")
    add_p(
        doc,
        "This final hard-bound report is structured into fifteen cohesive chapters and supporting appendices, following the official "
        "P P Savani University School of Engineering formatting standards:",
        space_after=6
    )
    add_bullet(doc, "Details institutional background, IT department domain, individual role, and development environment.", bold_prefix="Chapter 2 (Organization / UDP Profile):")
    add_bullet(doc, "Surveys existing caching literature (GPTCache, RedisVL, Towhee) and establishes the research gap.", bold_prefix="Chapter 3 (Literature Review):")
    add_bullet(doc, "Defines 10 functional requirements, 8 non-functional requirements, hardware/software specifications, and corpus data.", bold_prefix="Chapter 4 (Requirements Analysis):")
    add_bullet(doc, "Details the agile empirical research methodology, process workflow, milestones, and 16-week timeline.", bold_prefix="Chapter 5 (Methodology & Planning):")
    add_bullet(doc, "Presents system architecture, routing decision trees, UML diagrams, module designs, and database DDL.", bold_prefix="Chapter 6 (System Analysis & Design):")
    add_bullet(doc, "Reviews programming languages, libraries, databases, cloud runtimes, and selection rationales.", bold_prefix="Chapter 7 (Technology Stack):")
    add_bullet(doc, "Explains implementation details of the 7 core modules, mathematical logic, REST endpoints, and security.", bold_prefix="Chapter 8 (System Implementation):")
    add_bullet(doc, "Documents the complete 163-test verification suite (unit, functional, integration, system, perf, UAT) and defect resolutions.", bold_prefix="Chapter 9 (Testing & Validation):")
    add_bullet(doc, "Presents empirical benchmark results, threshold sweeps, latency speedups, and UI screenshot walkthroughs.", bold_prefix="Chapter 10 (Results & Analysis):")
    add_bullet(doc, "Analyzes major architectural challenges encountered (vector collision, 503 handling, TCP overhead) and solutions.", bold_prefix="Chapter 11 (Challenges & Solutions):")
    add_bullet(doc, "Reflects on 100% solo project ownership, technical competencies acquired, and professional development.", bold_prefix="Chapter 12 (Individual Contribution):")
    add_bullet(doc, "Identifies current operational constraints and outlines future research directions (multi-modal, clustering).", bold_prefix="Chapter 13 (Limitations & Future Scope):")
    add_bullet(doc, "Provides the formal closing assessment and completion status matrix.", bold_prefix="Chapter 14 (Conclusion):")
    add_bullet(doc, "Provides 28 authentic academic and industry citations formatted in APA 7th edition.", bold_prefix="Chapter 15 (References):")
    add_bullet(doc, "Includes reporting summaries, additional benchmarks, NPTEL OS certificate, repository links, and submission checklist.", bold_prefix="Appendices & Annexure:")

    # =========================================================================
    # CHAPTER 2: ORGANIZATION / UDP PROFILE
    # =========================================================================
    add_h1(doc, "CHAPTER 2\nORGANIZATION / UDP PROFILE")

    add_h2(doc, "2.1 Organization / Institutional Overview")
    add_p(
        doc,
        f"{INSTITUTE_NAME} (PPSU) is a premier state-private university established under the Gujarat Private Universities Act, 2014, "
        "located in Surat, Gujarat. The university is committed to fostering an ecosystem of academic excellence, multidisciplinary "
        "research, and practical engineering education. The {SCHOOL_NAME} (SOE) is the vanguard technical constituent of PPSU, "
        "dedicated to cultivating high-caliber engineers equipped with advanced problem-solving capabilities.",
        space_after=8
    )
    add_p(
        doc,
        "The School of Engineering emphasizes practical, project-based pedagogy through User Defined Projects (UDP) and industry "
        "collaborations. Under the UDP track, students identify critical technological frontiers, conduct rigorous independent research, "
        "and build production-grade software artifacts that address genuine computational inefficiencies.",
        space_after=12
    )

    add_h2(doc, "2.2 Department / Domain Profile")
    add_p(
        doc,
        f"This project was executed within the {DEPARTMENT_NAME} under the advanced domain of Artificial Intelligence Systems, "
        "Natural Language Processing (NLP), and Distributed High-Performance Systems Engineering. The department provides "
        "computational infrastructure, high-speed campus networks, and dedicated faculty mentorship to support deep-tech systems research.",
        space_after=8
    )
    add_p(
        doc,
        "The AI Systems domain within the department concentrates on the optimization of foundation model inference, vector database "
        "architectures, neural information retrieval, and edge computing. Cache-Craft directly aligns with this domain by addressing "
        "the real-world efficiency challenges inherent in deploying generative AI at scale.",
        space_after=12
    )

    add_h2(doc, "2.3 Role and Individual Responsibilities")
    add_p(
        doc,
        f"As a solo-engineered User Defined Project, I ({STUDENT_NAME}) assumed complete, 100% individual responsibility for every phase "
        "of the system development lifecycle. My responsibilities encompassed:",
        space_after=6
    )
    add_bullet(doc, "Conducted comprehensive literature surveys, reviewed open-source vector caching tools, and formulated the three-tier caching hypothesis.", bold_prefix="Systems Architect & Researcher:")
    add_bullet(doc, "Implemented the asynchronous FastAPI application, designed the PostgreSQL pgvector schema and HNSW indexes, integrated sentence-transformers, and built the multi-provider LLM router.", bold_prefix="Backend & Database Engineer:")
    add_bullet(doc, "Developed the responsive, dark-mode Next.js 15 web application with React 19, TypeScript, Tailwind CSS, SSE streaming, and interactive playground.", bold_prefix="Frontend UI/UX Developer:")
    add_bullet(doc, "Curated the 1,200-query benchmark corpus, authored vectorized evaluation scripts in NumPy, executed 163 software tests, and verified precision/recall curves.", bold_prefix="QA & Performance Benchmarker:")
    add_bullet(doc, "Configured Docker container multi-service orchestration, managed environment secrets, and deployed the production stack to Vercel and Railway.", bold_prefix="DevOps & Cloud Engineer:")

    add_h2(doc, "2.4 Development / Work Environment & Specifications")
    add_p(
        doc,
        "The research, algorithmic implementation, model training, containerized testing, and benchmark execution were conducted "
        "on a high-performance local engineering workstation. Table 2.1 documents the exact hardware and runtime specifications.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Hardware / System Component", "Technical Specifications", "Operational Role in Cache-Craft"],
        WORKSTATION_SPECS_DATA,
        col_widths=[2.2, 2.4, 2.2],
        caption="Table 2.1: Engineering Workstation Hardware and System Specifications"
    )

    add_h2(doc, "2.5 UDP Project Administrative Details")
    add_p(
        doc,
        f"The administrative particulars governing this User Defined Project are as follows:\n"
        f"• Project Category: User Defined Project (UDP) — Academic Track\n"
        f"• Candidate Name: {STUDENT_NAME} (Enrollment No.: {ENROLLMENT_NO})\n"
        f"• Academic Program: {PROGRAM_NAME}, {SEMESTER}\n"
        f"• Institute Mentor / Guide: {INSTITUTE_MENTOR}, Assistant Professor, Department of Information Technology\n"
        f"• Industry Mentor: Not Applicable (Academic Research UDP Track)\n"
        f"• Official Project Tenure: 08/06/2026 to 03/10/2026 (16 Academic Weeks)\n"
        f"• Institutional Affiliation: {INSTITUTE_NAME}, {SCHOOL_NAME}, Surat, Gujarat.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 3: LITERATURE REVIEW / BACKGROUND STUDY
    # =========================================================================
    add_h1(doc, "CHAPTER 3\nLITERATURE REVIEW / BACKGROUND STUDY")

    add_h2(doc, "3.1 Domain Background")
    add_p(
        doc,
        "The rapid integration of generative AI into production software has shifted focus from raw model accuracy to computational "
        "and financial efficiency. In standard RAG pipelines (Lewis et al., 2020), an incoming prompt undergoes dense retrieval against "
        "an external knowledge base, context injection, and foundation model inference. While effective, this pipeline incurs high token "
        "costs and latency overheads. Chen et al. (2023) demonstrated that in real-world conversational workloads, prompt queries "
        "frequently repeat with slight lexical modifications, creating significant opportunities for intelligent caching.",
        space_after=8
    )
    add_p(
        doc,
        "Unlike exact-match caching systems governed by deterministic hashing, semantic caching operates within dense continuous "
        "vector spaces. Dense text representations, popularized by Sentence-BERT (Reimers & Gurevych, 2019), map sentences to fixed-dimensional "
        "embeddings where semantic proximity corresponds to vector closeness. Approximate Nearest Neighbor (ANN) search algorithms, "
        "most notably Hierarchical Navigable Small World (HNSW) graphs (Malkov & Yashunin, 2018), enable logarithmic time-complexity "
        "retrieval over millions of vectors, making real-time semantic caching theoretically viable.",
        space_after=12
    )

    add_h2(doc, "3.2 Existing Approaches & Related Work")
    add_p(
        doc,
        "Several academic and open-source frameworks have emerged to explore vector caching for large language models. Table 3.1 "
        "provides an analytical overview of the primary contemporary approaches.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Existing System", "Core Architectural Concept", "Underlying Vector Engine", "Critical Architectural Limitations"],
        EXISTING_APPROACHES_DATA,
        col_widths=[1.5, 2.0, 1.5, 1.8],
        caption="Table 3.1: Overview of Existing Semantic Caching Approaches"
    )

    add_h2(doc, "3.3 Comparative Analysis")
    add_p(
        doc,
        "To rigorously evaluate Cache-Craft against the state of the art, a comprehensive feature-by-feature comparative matrix was "
        "constructed across ten critical engineering parameters. Table 3.2 details this comparison against GPTCache, LangChain Redis "
        "Semantic Cache, and Towhee.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Evaluation Parameter", "GPTCache (Zhong et al.)", "LangChain Redis VL", "Towhee / Milvus Stack", "Cache-Craft (This Work)"],
        COMPARATIVE_MATRIX_DATA,
        col_widths=[1.6, 1.3, 1.3, 1.3, 1.3],
        caption="Table 3.2: Comprehensive Comparative Matrix (Cache-Craft vs. State of the Art)"
    )

    add_h2(doc, "3.4 Research Gap and Project Justification")
    add_p(
        doc,
        "Despite recent advances in vector search, a rigorous survey of contemporary literature and open-source implementations reveals "
        "four critical engineering gaps that Cache-Craft directly resolves:",
        space_after=6
    )
    add_bullet(doc, " Existing semantic caches treat every incoming request as a vector search, incurring unnecessary embedding and index traversal overhead for identical queries. Cache-Craft resolves this by fronting the vector store with a sub-millisecond SHA-256 hash tier that bypasses vector math entirely for repeated prompts.", bold_prefix="1. Absence of Multi-Tier Hierarchical Bypass:")
    add_bullet(doc, " When caching multi-turn conversational follow-ups (e.g., 'Summarize that' or 'Tell me more'), conventional caches either fail to capture conversational context or suffer from severe vector collision with root queries. Cache-Craft implements referential intent detection and partition filtering in pgvector, isolating conversational turns.", bold_prefix="2. Context Drift and Semantic Collision in Multi-Turn Dialogues:")
    add_bullet(doc, " Existing libraries assume constant cloud availability. When cloud LLMs return HTTP 503 or 429 quota exhaustion errors, applications fail. Cache-Craft introduces a resilient dual-provider router with zero-downtime automated fallback from Google Gemini to local Ollama llama3.2.", bold_prefix="3. Single-Provider Cloud Vulnerability:")
    add_bullet(doc, " Local LLM instances expose expensive host GPU resources. When web applications are deployed or shared with peer testing groups, unauthorized clients can exhaust GPU compute. Cache-Craft implements cryptographic host signature verification (device_auth.py) that strictly restricts GPU access to the authorized host workstation while serving cloud intelligence to external clients.", bold_prefix="4. Lack of Hardware Device Security Boundaries:")

    # =========================================================================
    # CHAPTER 4: REQUIREMENTS ANALYSIS AND PROJECT SCOPE
    # =========================================================================
    add_h1(doc, "CHAPTER 4\nREQUIREMENTS ANALYSIS AND PROJECT SCOPE")

    add_h2(doc, "4.1 Functional Requirements Specification")
    add_p(
        doc,
        "Functional requirements define the core operational behaviors, transformations, and algorithmic capabilities of Cache-Craft. "
        "Table 4.1 documents the ten formal functional requirements (FR-01 to FR-10) alongside their verification test IDs.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Req. ID", "Functional Requirement Name", "Detailed Operational Specification", "Validation Status & Verification"],
        FUNCTIONAL_REQUIREMENTS_DATA,
        col_widths=[0.8, 1.8, 2.8, 1.4],
        caption="Table 4.1: Functional Requirements Specification (FR-01 to FR-10)"
    )

    add_h2(doc, "4.2 Non-Functional Requirements Specification")
    add_p(
        doc,
        "Non-functional requirements dictate the performance boundaries, quality attributes, security standards, and scalability "
        "thresholds required for enterprise production readiness. Table 4.2 presents the eight non-functional requirements.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Req. ID", "Quality Attribute", "Measurable Requirement Specification", "Empirical Verification Result"],
        NON_FUNCTIONAL_REQUIREMENTS_DATA,
        col_widths=[0.8, 1.6, 2.8, 1.6],
        caption="Table 4.2: Non-Functional Requirements Specification (NFR-01 to NFR-08)"
    )

    add_h2(doc, "4.3 Hardware Requirements and Infrastructure")
    add_p(
        doc,
        "To ensure reproducible deployment across development, cloud production, and client browser environments, Table 4.3 outlines "
        "the minimum and recommended hardware configurations.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Deployment Tier", "Minimum vs. Recommended Hardware Specification", "Functional Deployment Scope"],
        HARDWARE_REQUIREMENTS_DATA,
        col_widths=[1.8, 2.8, 2.2],
        caption="Table 4.3: Hardware Requirements and Infrastructure Specifications"
    )

    add_h2(doc, "4.4 Software Requirements and Dependencies")
    add_p(
        doc,
        "The software stack leverages modern, production-hardened open-source frameworks. Table 4.4 details the software runtime dependencies.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Software Component", "Version / Library Specification", "Architectural Functionality in Cache-Craft"],
        SOFTWARE_REQUIREMENTS_DATA,
        col_widths=[1.8, 2.6, 2.4],
        caption="Table 4.4: Software Requirements and Runtime Dependencies"
    )

    add_h2(doc, "4.5 Data / Dataset Requirements")
    add_p(
        doc,
        "To evaluate semantic routing precision without synthetic bias, a high-quality 1,200-query benchmark corpus was curated and "
        "structured. Table 4.5 details the composition of the benchmark dataset.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Corpus Subset", "Sample Volume & Category Description", "Methodological Purpose in Evaluation"],
        DATASET_REQUIREMENTS_DATA,
        col_widths=[1.8, 2.8, 2.2],
        caption="Table 4.5: Benchmark Dataset Requirements and Corpus Distribution"
    )

    add_h2(doc, "4.6 System Constraints and Operational Assumptions")
    add_p(
        doc,
        "The system operates under several documented engineering constraints and assumptions:",
        space_after=6
    )
    add_bullet(doc, "The embedding model (all-MiniLM-L6-v2) has a maximum sequence length of 512 wordpiece tokens. Input prompts exceeding this boundary are truncated during embedding generation.", bold_prefix="1. Token Truncation Boundary:")
    add_bullet(doc, "The primary cloud LLM endpoint relies on an active internet connection and valid Google Gemini API credentials. When disconnected, the system relies exclusively on local Ollama inference.", bold_prefix="2. Network Connectivity:")
    add_bullet(doc, "Local LLM inference via Ollama requires an NVIDIA GPU with at least 4 GB VRAM for optimal token generation speed (~30 tokens/sec). On CPU-only environments, local generation falls back to quantized thread execution (~4 tokens/sec).", bold_prefix="3. Hardware Acceleration:")

    # =========================================================================
    # CHAPTER 5: METHODOLOGY AND PROJECT PLANNING
    # =========================================================================
    add_h1(doc, "CHAPTER 5\nMETHODOLOGY AND PROJECT PLANNING")

    add_h2(doc, "5.1 Final Development and Research Methodology")
    add_p(
        doc,
        "Cache-Craft was engineered using an iterative Agile Empirical Research Methodology that seamlessly combined experimental "
        "data science with robust software engineering principles. The development lifecycle followed a four-stage evolutionary progression:",
        space_after=6
    )
    add_bullet(doc, "Investigated vector distance spaces, surveyed ANN literature, established mathematical definitions for cosine similarity thresholds, and formulated the core multi-tier routing hypothesis.", bold_prefix="1. Mathematical & Theoretical Modeling:")
    add_bullet(doc, "Constructed an isolated SQLite prototype to evaluate sentence transformer latency and determine baseline cosine similarity distributions on 100 sample query pairs.", bold_prefix="2. Experimental Prototyping:")
    add_bullet(doc, "Migrated storage to PostgreSQL 16 pgvector with HNSW indexing, introduced Redis exact-match caching, integrated dual LLM inference, and built the Next.js 15 web dashboard.", bold_prefix="3. Architectural Hardening & Integration:")
    add_bullet(doc, "Curated the 1,200-query benchmark corpus, executed multi-threshold sweeps (tau=0.70 to 0.95), conducted 163 software tests, and deployed the production stack to Vercel and Railway.", bold_prefix="4. Empirical Validation & Cloud Deployment:")

    add_h2(doc, "5.2 Project Workflow & Process Architecture")
    add_p(
        doc,
        "Figure 5.1 illustrates the comprehensive development, testing, and operational research workflow of Cache-Craft. As depicted, "
        "incoming queries traverse through a deterministic preprocessing pipeline, evaluate multi-tier cache stores, orchestrate "
        "LLM generation upon misses, update observability telemetry via SSE, and feed continuous empirical benchmarking metrics.",
        space_after=6
    )
    add_figure(
        doc,
        "reports_assets/process_flow_diagram.png",
        "5.1",
        "Cache-Craft End-to-End System Development and Research Workflow",
        width_inches=5.8
    )

    add_h2(doc, "5.3 Project Phases and Deliverables")
    add_p(
        doc,
        "The project was executed across four distinct, milestone-driven phases spanning sixteen academic weeks. Table 5.1 details the "
        "phases, timelines, and deliverables.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Development Phase", "Tenure & Schedule", "Major Deliverables & Technical Milestones Achieved"],
        PROJECT_PHASES_DATA,
        col_widths=[1.8, 1.8, 3.2],
        caption="Table 5.1: Project Phases, Milestones, and Key Deliverables"
    )

    add_h2(doc, "5.4 Progress Report Consolidation")
    add_p(
        doc,
        "Rather than pasting disparate reports together, this final hard-bound document consolidates the progressive evolutionary "
        "advancements documented across the four formal university reporting stages. Table 5.2 outlines this progression.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["University Reporting Stage", "Defense Date", "Key Developmental Evolution & Milestone Completed"],
        PROGRESS_REPORTS_CONSOLIDATION_DATA,
        col_widths=[1.8, 1.2, 3.8],
        caption="Table 5.2: Progress Report Consolidation and Developmental Evolution"
    )

    add_h2(doc, "5.5 Project Schedule and 16-Week Gantt Timeline")
    add_p(
        doc,
        "The project adhered to a strict 16-week timeline from June 8, 2026 to October 3, 2026. Table 5.3 presents the task breakdown, "
        "durations, ownership, and completion status.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Task Description / Phase", "Start", "End", "Status", "Owner", "Completion"],
        PROJECT_SCHEDULE_GANTT_DATA,
        col_widths=[2.4, 0.8, 0.8, 0.9, 1.2, 0.7],
        caption="Table 5.3: Comprehensive 16-Week Project Schedule and Timeline"
    )
