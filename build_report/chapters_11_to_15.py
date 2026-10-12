"""
build_report/chapters_11_to_15.py — Chapters 11 through 15 of Cache-Craft Final Hard-Bound Report.
Covers Challenges & Improvements, Individual Contribution, Limitations & Future Scope,
Conclusion, and References (APA 7th edition).
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from build_report.styles import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BODY,
    add_h1, add_h2, add_h3, add_p, add_bullet, add_styled_table, add_callout
)
from build_report.metadata import (
    PROJECT_TITLE, FULL_PROJECT_TITLE, STUDENT_NAME, ENROLLMENT_NO,
    ARCHITECTURAL_IMPROVEMENTS_DATA, TECHNICAL_SKILLS_DATA,
    PROFESSIONAL_SKILLS_DATA, LIMITATIONS_DATA, FUTURE_SCOPE_DATA,
    FINAL_STATUS_DATA, REFERENCES_LIST
)

def build_chapters_11_to_15(doc):
    """Builds Chapters 11 through 15 with exhaustive technical prose and APA citations."""

    # =========================================================================
    # CHAPTER 11: CHALLENGES, SOLUTIONS AND IMPROVEMENTS
    # =========================================================================
    add_h1(doc, "CHAPTER 11\nCHALLENGES, SOLUTIONS AND IMPROVEMENTS")

    add_h2(doc, "11.1 Major Architectural & Algorithmic Challenges")
    add_p(
        doc,
        "Engineering an autonomous semantic caching router across heterogeneous multi-tier storage layers and foundation LLMs presented "
        "several non-trivial architectural and algorithmic challenges. Bridging the gap between millisecond vector operations and multi-second "
        "generative inference required rigorous diagnostics, mathematical adaptations, and system-level refactoring.",
        space_after=8
    )

    add_h2(doc, "11.2 Technical Challenges & Engineering Resolutions")
    add_p(
        doc,
        "During development, five primary technical hurdles were encountered and resolved:",
        space_after=6
    )
    add_bullet(
        doc,
        "When caching multi-turn conversational follow-ups by prefixing history (e.g., '<parent_query> -> <follow_up>'), dense embeddings "
        "exhibited ~0.97 cosine similarity to the un-summarized parent query. Consequently, asking 'Can you summarize that?' mistakenly returned "
        "the raw parent answer rather than the summary. Resolution: Implemented referential intent detection and partition filtering in pgvector "
        "(WHERE query_text LIKE '% -> %' vs NOT LIKE '% -> %'), strictly isolating conversational turns from root semantic queries.",
        bold_prefix="1. Multi-Turn Follow-up Semantic Collision: "
    )
    add_bullet(
        doc,
        "During high-concurrency benchmark trials, the commercial Google Gemini API periodically returned HTTP 503 high-demand errors "
        "or HTTP 429 quota exhaustion limits. Resolution: Engineered an automatic, transparent cloud-to-local failover circuit in core/llm_client.py. "
        "When an upstream error is caught, the request is rerouted to the local Ollama llama3.2 daemon with zero disruption to the user.",
        bold_prefix="2. Cloud LLM Availability Spikes (HTTP 503/429): "
    )
    add_bullet(
        doc,
        "Iterating 4,200 individual PostgreSQL queries across separate connections to evaluate multiple thresholds on 700 queries took ~30 seconds "
        "due to TCP handshake overhead. Resolution: Vectorized the multi-threshold evaluation in NumPy using matrix dot products "
        "(np.dot(eval_mat, seed_mat.T)), cutting benchmark evaluation time from 30 seconds to ~2 seconds while sampling live PostgreSQL queries for real latency profiling.",
        bold_prefix="3. Benchmark Execution Overhead: "
    )
    add_bullet(
        doc,
        "Cached LLM answers risked becoming outdated over time without an automated expiration mechanism. Resolution: Implemented a dual-tier "
        "TTL system applying native Redis expiration (EX <ttl>) and PostgreSQL expires_at indexing, coupled with an on-demand vacuum button.",
        bold_prefix="4. Cache Staleness and Drift: "
    )
    add_bullet(
        doc,
        "When sharing the application with peers for testing, remote web clients could trigger heavy local GPU Ollama inference, overloading "
        "the developer workstation. Resolution: Developed device_auth.py with host signature and loopback verification, blocking remote "
        "clients from accessing local GPU resources while serving cloud intelligence.",
        bold_prefix="5. Local GPU Resource Remote Exploitation: "
    )

    add_h2(doc, "11.3 Process, Dataset & Environment Challenges")
    add_p(
        doc,
        "Beyond code implementation, significant effort was invested in curating the 1,200-query benchmark corpus. Synthesizing 500 semantically "
        "valid natural language paraphrases alongside 200 out-of-domain negative controls required strict domain filtering to avoid subtle "
        "data leakage or linguistic artifacts. Additionally, orchestrating multi-container Docker dependencies across Windows 11 WSL2 "
        "required careful port mapping and volume permission management.",
        space_after=8
    )

    add_h2(doc, "11.4 Architectural Improvements Made During Development")
    add_p(
        doc,
        "Table 11.1 highlights the six major architectural refinements introduced across the project lifecycle.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["System Component", "Initial Baseline Approach", "Final Refined Implementation", "Measured Engineering Impact"],
        ARCHITECTURAL_IMPROVEMENTS_DATA,
        col_widths=[1.5, 1.8, 1.8, 2.1],
        caption="Table 11.1: Architectural Improvements and Developmental Refinements"
    )

    add_h2(doc, "11.5 Lessons Learned from Systems Engineering Challenges")
    add_p(
        doc,
        "Overcoming these challenges yielded valuable engineering takeaways: (1) Unit normalization is vital in high-dimensional vector spaces "
        "to eliminate magnitude bias; (2) Multi-tier hierarchical caching significantly outperforms single-tier vector stores by absorbing "
        "exact hits; (3) Graceful degradation via automated local fallback is essential for mission-critical generative AI reliability.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 12: INDIVIDUAL CONTRIBUTION AND PROFESSIONAL LEARNING
    # =========================================================================
    add_h1(doc, "CHAPTER 12\nINDIVIDUAL CONTRIBUTION AND PROFESSIONAL LEARNING")

    add_h2(doc, "12.1 Individual Contribution & Project Ownership")
    add_p(
        doc,
        f"This User Defined Project was undertaken with 100% solo ownership by {STUDENT_NAME}. Every line of backend Python, frontend "
        "TypeScript, SQL schema, benchmark script, and documentation was individually researched, engineered, and validated. "
        "Managing the complete software engineering lifecycle independently fostered deep technical competence and rigorous self-discipline.",
        space_after=8
    )

    add_h2(doc, "12.2 Technical Competencies & Skills Acquired")
    add_p(
        doc,
        "Table 12.1 summarizes the core technical competencies and specialized tools mastered during the development of Cache-Craft.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Technical Domain / Competency", "Specific Engineering Skills & Technologies Acquired"],
        TECHNICAL_SKILLS_DATA,
        col_widths=[2.4, 4.8],
        caption="Table 12.1: Technical Skills and Engineering Competencies Acquired"
    )

    add_h2(doc, "12.3 Professional, Research & Architectural Skills Acquired")
    add_p(
        doc,
        "Table 12.2 summarizes the professional, project management, and research capabilities cultivated through this independent project.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Professional / Architectural Skill", "Demonstrated Capability & Practical Experience"],
        PROFESSIONAL_SKILLS_DATA,
        col_widths=[2.4, 4.8],
        caption="Table 12.2: Professional, Research, and Project Management Skills Acquired"
    )

    add_h2(doc, "12.4 Major Academic and Professional Learning Outcomes")
    add_p(
        doc,
        "The project bridged theoretical computer science concepts with industrial engineering practices:\n"
        "• Deepened mathematical understanding of high-dimensional vector geometry, cosine metrics, and ANN graph algorithms.\n"
        "• Provided practical mastery of ACID relational vector databases (PostgreSQL pgvector) versus dedicated vector stores.\n"
        "• Instilled production software engineering discipline: container orchestration, asynchronous APIs, type safety, and automated testing.\n"
        "• Cultivated scientific rigor in designing empirical benchmark corpora and calculating precision/recall/F1 metrics.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 13: LIMITATIONS AND FUTURE SCOPE
    # =========================================================================
    add_h1(doc, "CHAPTER 13\nLIMITATIONS AND FUTURE SCOPE")

    add_h2(doc, "13.1 Current Technical Limitations")
    add_p(
        doc,
        "While Cache-Craft successfully achieves its primary objectives, several operational constraints exist. Table 13.1 documents "
        "these boundaries.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Identified Limitation", "Technical Description", "Severity", "Mitigation Strategy"],
        LIMITATIONS_DATA,
        col_widths=[1.8, 2.8, 0.8, 1.8],
        caption="Table 13.1: Current System Limitations and Operational Boundaries"
    )

    add_h2(doc, "13.2 Future Scope & Developmental Roadmap")
    add_p(
        doc,
        "Future research and development will expand Cache-Craft across several promising frontiers. Table 13.2 details the roadmap.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Planned Future Enhancement", "Proposed Technical Implementation & Strategic Value"],
        FUTURE_SCOPE_DATA,
        col_widths=[2.4, 4.8],
        caption="Table 13.2: Future Scope, Planned Enhancements, and Scalability Opportunities"
    )

    add_h2(doc, "13.3 Scalability, Clustering & Enterprise Extension Opportunities")
    add_p(
        doc,
        "For multi-tenant enterprise scale, Cache-Craft can be extended with a distributed Redis Cluster for L1 caching, partitioned "
        "PostgreSQL pgvector shards for multi-million vector datasets, and Kubernetes GPU daemon sets for scalable local LLM inference.",
        space_after=12
    )

    # =========================================================================
    # CHAPTER 14: CONCLUSION
    # =========================================================================
    add_h1(doc, "CHAPTER 14\nCONCLUSION")

    add_h2(doc, "14.1 Final Project Completion Status")
    add_p(
        doc,
        "Cache-Craft has achieved 100% completion across all planned architectural tiers, algorithms, test suites, and deployment targets. "
        "Table 14.1 provides the comprehensive completion matrix.",
        space_after=6
    )
    add_styled_table(
        doc,
        ["Subsystem / Module", "Final Status", "Completion (%)", "Verified Operational Outcome"],
        FINAL_STATUS_DATA,
        col_widths=[2.0, 1.6, 1.0, 2.6],
        caption="Table 14.1: Final Comprehensive Project Completion Status Matrix"
    )

    add_h2(doc, "14.2 Concluding Remarks")
    add_p(
        doc,
        "In conclusion, Cache-Craft demonstrates that multi-tier semantic caching is an indispensable architectural pattern for scalable, "
        "cost-effective generative AI. By intercepting inbound queries and serving verified responses in 25 milliseconds via an optimized "
        "PostgreSQL 16 pgvector HNSW index, Cache-Craft slashes cloud LLM inference latency by 3.2x and reduces token expenditures by 68.71% "
        "while guaranteeing 100% precision. Combined with an automated cloud-to-local failover circuit and a modern Next.js 15 web dashboard, "
        "the project delivers an autonomous, production-ready middleware that satisfies all academic requirements for the B.Tech degree.",
        space_after=16
    )

    # =========================================================================
    # CHAPTER 15: REFERENCES
    # =========================================================================
    add_h1(doc, "CHAPTER 15\nREFERENCES")
    add_p(
        doc,
        "All citations adhere strictly to the American Psychological Association (APA) 7th Edition referencing style:",
        space_after=8
    )
    for ref in REFERENCES_LIST:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Inches(0.5)
        p_ref.paragraph_format.first_line_indent = Inches(-0.5)
        r = p_ref.add_run(ref)
        r.font.name = 'Cambria'
        r.font.size = Pt(10)
