"""
create_report_4.py — Programmatic generation of Cache-Craft Reporting 4 Final Report.
Preserves original template formatting, styles, headers, and evaluation rubrics.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

TEMPLATE_PATH = "files/Internship_UDP_Training_Report_Template for reporting 4.docx"
OUTPUT_PATH = "Cache-Craft_Reporting_4_Final.docx"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def format_cell_text(cell, text, bold=False, font_size=10, font_name="Calibri", color_rgb=(0, 0, 0), align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.bold = bold
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.color.rgb = RGBColor(*color_rgb)

def main():
    print(f"Loading template: {TEMPLATE_PATH}")
    doc = docx.Document(TEMPLATE_PATH)

    # ============================================================
    # 1. Fill Table 0: Student Information
    # ============================================================
    t0 = doc.tables[0]
    student_info = [
        ("Student Name", "AAKASH BHARATBHAI JAYANI"),
        ("Enrollment Number", "23SE02IT140"),
        ("Program/Branch", "B.Tech IT"),
        ("Semester", "7th"),
        ("Contact Number", "8160356800"),
        ("Email ID", "23SE02IT140@PPSU.AC.IN")
    ]
    for idx, (label, val) in enumerate(student_info):
        format_cell_text(t0.rows[idx].cells[0], label, bold=True, font_size=10.5)
        format_cell_text(t0.rows[idx].cells[1], val, bold=False, font_size=10.5)

    # ============================================================
    # 2. Fill Table 1: Internship / UDP Details
    # ============================================================
    t1 = doc.tables[1]
    internship_info = [
        ("Type", "UDP"),
        ("Company/Organization", "PPSU"),
        ("Department/Domain", "SOE"),
        ("Mentor Name (Company)", ""),
        ("Mentor Name (Institute)", "Mr. Anurag Yadav"),
        ("Start Date", "08/06/2026"),
        ("End Date", "03/10/2026")
    ]
    for idx, (label, val) in enumerate(internship_info):
        format_cell_text(t1.rows[idx].cells[0], label, bold=True, font_size=10.5)
        format_cell_text(t1.rows[idx].cells[1], val, bold=False, font_size=10.5)

    # ============================================================
    # 3. Work Progress Summary & Project Title
    # ============================================================
    # P[6]: Project Title:
    # P[7]: [Underline placeholder] -> replace with Project Title
    p7 = doc.paragraphs[7]
    p7.text = ""
    r = p7.add_run("             Cache-Craft: Autonomous Semantic RAG Router - A High-Performance Multi-Tier Semantic Caching Middleware for LLM Inference")
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(11)

    # P[9]: b) Brief Overview of Work Completed After Reporting 2 -> change to Reporting 3
    p9 = doc.paragraphs[9]
    p9.text = ""
    r = p9.add_run("b) Brief Overview of Work Completed After Reporting 3")
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(11)

    # P[10]: Mention only the work completed... -> replace with Major tasks completed
    p10 = doc.paragraphs[10]
    p10.text = ""
    r1 = p10.add_run("Major tasks completed: ")
    r1.bold = True
    r2 = p10.add_run("Successfully transitioned the project from the interim SQLite3 prototype to a production-grade multi-tier architecture using PostgreSQL 16 with pgvector and Redis 7. Implemented a context-aware conversational caching engine to solve referential follow-ups. Developed an enterprise-grade dark/glass dashboard in Next.js 15. Integrated pluggable cloud/local inference (Google Gemini 3.8 Flash and local Ollama Llama 3.2 with automatic fallback). Implemented dual-tier TTL cache lifecycle management with automated database cleanup. Designed and executed an end-to-end 1,200-query benchmark evaluation suite. Orchestrated a full 4-service containerized deployment stack using Docker Compose.")

    # P[11]: Modules completed
    p11 = doc.paragraphs[11]
    p11.text = ""
    r1 = p11.add_run("Modules completed: ")
    r1.bold = True
    r2 = p11.add_run("1) Multi-Tier Routing Core (L1 Redis Exact + L2 pgvector HNSW Semantic), 2) Multi-Turn Conversational Context Binder, 3) Pluggable Multi-LLM Inference & Fallback Engine, 4) Dual-Tier TTL Cache Lifecycle Manager, 5) Real-Time SSE Metrics Streaming Pipeline, 6) Next.js 15 Cupertino Dashboard & Chat Playground, 7) Automated 1,200-Query Benchmark Evaluation Engine.")

    # P[12]: New features implemented
    p12 = doc.paragraphs[12]
    p12.text = ""
    r = p12.add_run("New features implemented:")
    r.bold = True

    # P[13]: Feature 1
    p13 = doc.paragraphs[13]
    p13.text = ""
    r1 = p13.add_run("1. Multi-Turn Context-Aware Caching: ")
    r1.bold = True
    r2 = p13.add_run("Implemented conversation turn binding (<prior_query> -> <follow_up>) with pgvector partition filtering, enabling follow-up questions (e.g., 'summarize it', 'why', 'elaborate') to be cached without colliding with parent queries.")

    # P[14]: Feature 2
    p14 = doc.paragraphs[14]
    p14.text = ""
    r1 = p14.add_run("2. Pluggable Cloud & Local LLM Engine: ")
    r1.bold = True
    r2 = p14.add_run("Dual inference support for local Ollama llama3.2 (100% offline privacy and zero cost) and Google Gemini (gemini-3.8-flash) with automatic, resilient fallback to local Ollama during API spikes or rate limits.")

    # P[15]: Feature 3 & Research
    p15 = doc.paragraphs[15]
    p15.text = ""
    r1 = p15.add_run("3. Dual-Tier TTL Lifecycle Management: ")
    r1.bold = True
    r2 = p15.add_run("Coordinated cache expiration across Redis (EX <ttl>) and PostgreSQL (expires_at TIMESTAMP with B-tree index), featuring 6 UI presets (1h, 6h, 24h, 7d, 30d, Permanent) and on-demand database vacuuming.\n")
    r3 = p15.add_run("4. Real-Time Analytics & SSE Streaming: ")
    r3.bold = True
    r4 = p15.add_run("Server-Sent Events endpoint (/api/metrics/stream) delivering live query volume, hit-rate, latency distributions, and cost-savings counters to the Next.js frontend.\n")
    r5 = p15.add_run("5. 1,200-Query Benchmark Evaluation Suite: ")
    r5.bold = True
    r6 = p15.add_run("Automated evaluation pipeline testing 500 seeds, 500 paraphrases, and 200 unrelated queries across 6 cosine similarity thresholds (0.70 to 0.95), comparing against No-Cache and Exact Redis baselines.")

    # P[16]: Research / development work completed
    # If P[16] exists, fill it, or add new paragraph
    # Let's inspect paragraphs 16, 17, 18
    p16 = doc.paragraphs[16]
    p16.text = ""
    r1 = p16.add_run("Research / development work completed: ")
    r1.bold = True
    r2 = p16.add_run("Researched dense vector embedding distance spaces (unit L2-normalized cosine similarity vs Euclidean distance in HNSW graphs). Investigated vector drift and catastrophic interference in multi-turn conversational caching. Evaluated latency and memory trade-offs between Redis in-memory key-value lookups and pgvector index scans. Formulated optimal threshold boundaries (0.70–0.85) balancing 100% precision with maximum recall.\n")
    r3 = p16.add_run("Integration work completed: ")
    r3.bold = True
    r4 = p16.add_run("Unified the 4 decoupled application tiers (Next.js 15 frontend, FastAPI Python backend, Redis 7 in-memory cache, and PostgreSQL 16 + pgvector database) within a unified Docker Compose network with health checks and GPU passthrough.")

    # P[18]: Overall Project Completion: ______ %
    p18 = doc.paragraphs[18]
    p18.text = ""
    r1 = p18.add_run("Overall Project Completion: ")
    r1.bold = True
    r2 = p18.add_run("__100____ %")
    r2.bold = True

    # ============================================================
    # 4. Fill Table 2: Overall Project Completion Status
    # ============================================================
    t2 = doc.tables[2]
    # Rows: Requirement, Design, Development, Integration, Testing, Documentation, Deployment
    for row_idx in range(1, len(t2.rows)):
        format_cell_text(t2.rows[row_idx].cells[1], "Completed", bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell_text(t2.rows[row_idx].cells[2], "100%", bold=True, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    # ============================================================
    # 5. Section 4: Advanced Implementation & Table 3
    # ============================================================
    t3 = doc.tables[3]
    # Ensure Table 3 has 5 rows of data (total 6 rows including header)
    while len(t3.rows) < 6:
        t3.add_row()

    modules_data = [
        ("Dual-Tier Cache Router (L1 Redis + L2 pgvector)", "Engineered L1 Redis SHA-256 exact matching (<2ms) and L2 pgvector HNSW cosine similarity search (~25ms) using sentence-transformers/all-MiniLM-L6-v2.", "Completed"),
        ("Multi-Turn Context Binder", "Developed referential query detection with conversation history aggregation and pgvector partition filtering for follow-up questions.", "Completed"),
        ("Pluggable Multi-LLM Inference Engine", "Integrated Google Gemini Cloud (gemini-3.8-flash) and local Ollama (llama3.2) with automatic cloud-to-local fallback and token usage logging.", "Completed"),
        ("Dual-Tier TTL Lifecycle Manager", "Implemented coordinated cache expiration across Redis and PostgreSQL with 6 lifecycle presets and background cleanup.", "Completed"),
        ("Next.js 15 Dashboard & Analytics UI", "Built an Apple-grade dark/glass web dashboard with Overview, Chat Playground, Vector Explorer, and Settings panels.", "Completed")
    ]

    for idx, (m_name, m_work, m_status) in enumerate(modules_data, 1):
        format_cell_text(t3.rows[idx].cells[0], m_name, bold=True, font_size=9.5)
        format_cell_text(t3.rows[idx].cells[1], m_work, bold=False, font_size=9.5)
        format_cell_text(t3.rows[idx].cells[2], m_status, bold=True, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)

    # Paragraphs 24 to 31: Integration / Development Details
    p24 = doc.paragraphs[24]
    p24.text = ""
    r = p24.add_run("Integration / Development Details")
    r.bold = True

    p25 = doc.paragraphs[25]
    p25.text = ""
    r1 = p25.add_run("Module integration: ")
    r1.bold = True
    r2 = p25.add_run("The Next.js 15 frontend application interfaces seamlessly with the FastAPI backend through typed REST endpoints and SSE streams. The Cache Router tightly couples the SHA-256 pre-filter, the PyTorch SentenceTransformer embedder, the database layer, and the upstream LLM client into a unified, non-blocking pipeline.")

    p26 = doc.paragraphs[26]
    p26.text = ""
    r1 = p26.add_run("API integration: ")
    r1.bold = True
    r2 = p26.add_run("Integrated external Google Gemini REST API v1beta for high-throughput cloud inference and the local Ollama HTTP REST daemon (http://localhost:11434) for private on-premise execution, wrapped in a common abstract interface with automatic fallback logic.")

    p27 = doc.paragraphs[27]
    p27.text = ""
    r1 = p27.add_run("Database integration: ")
    r1.bold = True
    r2 = p27.add_run("Upgraded storage to PostgreSQL 16 with the pgvector extension. Configured connection pooling via psycopg 3 with native vector registration. Created HNSW index with vector_cosine_ops parameters (m=16, ef_construction=64) for sub-linear ANN search over 384-dimensional embeddings. Added Redis 7 container for sub-2ms exact match key-value lookups.")

    p28 = doc.paragraphs[28]
    p28.text = ""
    r1 = p28.add_run("Hardware integration: ")
    r1.bold = True
    r2 = p28.add_run("N/A — Purely software and database middleware architecture, utilizing host CPU/GPU SIMD instructions for local PyTorch vector tensor operations.")

    p29 = doc.paragraphs[29]
    p29.text = ""
    r1 = p29.add_run("Software integration: ")
    r1.bold = True
    r2 = p29.add_run("Integrated SentenceTransformers (all-MiniLM-L6-v2), pgvector, Redis-Py, NumPy, Pydantic v2, and Next.js 15 with Tailwind CSS and Lucide React into a cohesive, production-grade microservices stack.")

    p30 = doc.paragraphs[30]
    p30.text = ""
    r1 = p30.add_run("Major coding / development work: ")
    r1.bold = True
    r2 = p30.add_run("Implemented over 2,500 lines of robust, modular code across the backend, core routing algorithms, database persistence, and Next.js frontend. Solved critical edge cases including conversational semantic drift, dynamic TTL synchronization, cloud LLM rate-limit resilience, and matrix-vectorized benchmark evaluation.")

    # P[34]: Diagram & Insert Image
    p34 = doc.paragraphs[34]
    p34.text = ""
    r_diag = p34.add_run("Diagrams:\n")
    r_diag.bold = True

    # P[35]: Insert Architecture Image & Decision Flowchart
    p35 = doc.paragraphs[35]
    p35.text = ""
    p35.alignment = WD_ALIGN_PARAGRAPH.CENTER
    arch_img_path = "reports_assets/arch_diagram_v4.png"
    flow_img_path = "reports_assets/flowchart_decision_tree.png"

    diag_list = [
        ("Figure 1: Production Multi-Tier System Architecture (Decoupled Microservices Stack)\n", "reports_assets/arch_diagram_v4.png"),
        ("Figure 2: Autonomous Request Routing & Multi-Tier Decision Flowchart\n", "reports_assets/flowchart_decision_tree.png"),
        ("Figure 4.3: Cache-Craft System Block Diagram and Component Interaction\n", "reports_assets/figure_4_3_block_diagram.png"),
        ("Figure 4.4: Cache-Craft Consolidated UML Architectural Blueprints\n", "reports_assets/figure_4_4_uml_diagram.png"),
        ("Figure 4.5: Cache-Craft End-to-End Process Flow Diagram\n", "reports_assets/figure_4_5_process_flow_diagram.png")
    ]

    for d_title, d_path in diag_list:
        if os.path.exists(d_path):
            r_f = p35.add_run(d_title)
            r_f.bold = True
            r_f.font.size = Pt(9.5)
            p35.add_run().add_picture(d_path, width=Inches(6.2))
            p35.add_run("\n\n")

    # P[36]: Brief Explanation
    p36 = doc.paragraphs[36]
    p36.text = ""
    r1 = p36.add_run("Brief Explanation:\n")
    r1.bold = True
    r2 = p36.add_run("The updated system architecture implements a decoupled, three-tier cloud/on-premise deployment model illustrated in Figure 1 and Figure 2. Tier 1 (Presentation) is built with Next.js 15 and Tailwind CSS, providing an Apple-grade glassmorphic interface for chat, analytics, cache inspection, and settings controls. Tier 2 (Application Middleware) is powered by Python 3.11 and FastAPI, executing SHA-256 exact matching, dense vector embedding generation (all-MiniLM-L6-v2, 384-dim), conversational turn binding, and resilient LLM routing. Tier 3 (Storage & Inference) combines an in-memory Redis 7 instance for sub-2ms exact hash hits, a PostgreSQL 16 + pgvector instance with an HNSW cosine similarity index for sub-25ms semantic hits, and a pluggable LLM inference layer supporting both local Ollama (llama3.2) and cloud Google Gemini (gemini-3.8-flash). Requests flow sequentially through L1 -> L2 -> L3, ensuring minimum latency and maximum token cost savings.")

    # ============================================================
    # 6. Fill Table 4: Final Testing and Validation
    # ============================================================
    t4 = doc.tables[4]
    test_rows_data = [
        ("Functional Testing", "Exact hash hit, semantic similarity hit, cache miss, multi-turn follow-up binding, TTL expiration, DB vacuuming, and settings updates.", "65", "0", "Passed"),
        ("Integration Testing", "Frontend ↔ Backend REST/SSE, Backend ↔ Redis 7, Backend ↔ PostgreSQL 16 + pgvector, Backend ↔ Ollama, Backend ↔ Gemini API.", "35", "0", "Passed"),
        ("System Testing", "End-to-end user query lifecycle, multi-turn conversational chat, automated fallback from Gemini to Ollama upon simulated 503 error.", "25", "0", "Passed"),
        ("Performance Testing", "1,200-query benchmark corpus, multi-threshold sensitivity evaluation, latency profiling under concurrent requests.", "20", "0", "Passed"),
        ("User Acceptance Testing", "Dashboard UI responsiveness, dark-mode glassmorphism rendering, interactive slider updates, real-time metrics streaming.", "18", "0", "Passed")
    ]

    for idx, (t_area, t_conducted, t_passed, t_failed, t_status) in enumerate(test_rows_data, 1):
        format_cell_text(t4.rows[idx].cells[0], t_area, bold=True, font_size=9.5)
        format_cell_text(t4.rows[idx].cells[1], t_conducted, bold=False, font_size=9)
        format_cell_text(t4.rows[idx].cells[2], t_passed, bold=True, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell_text(t4.rows[idx].cells[3], t_failed, bold=False, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell_text(t4.rows[idx].cells[4], t_status, bold=True, font_size=9.5, color_rgb=(16, 149, 106), align=WD_ALIGN_PARAGRAPH.CENTER)

    # ============================================================
    # 7. Fill Table 5: Critical Bugs / Issues
    # ============================================================
    t5 = doc.tables[5]
    while len(t5.rows) < 5:
        t5.add_row()

    issues_data = [
        ("Multi-Turn Follow-up Semantic Collision: When prefixing follow-ups as <prior_query> -> <follow_up>, dense vector embeddings had ~0.97 cosine similarity to the un-summarized parent query, returning raw parent answers instead of summaries.", "High", "Implemented referential intent detection and partition filtering in pgvector (WHERE query_text LIKE '% -> %' vs NOT LIKE '% -> %'), isolating follow-up queries.", "Resolved"),
        ("Cloud LLM Availability Spikes: Google Gemini API occasionally returned HTTP 503 high-demand errors or quota limits during heavy benchmark runs.", "High", "Implemented automatic, graceful cloud-to-local fallback in llm_client.py, rerouting failed cloud calls to the local Ollama llama3.2 daemon with zero user disruption.", "Resolved"),
        ("Benchmark Execution Overhead: Iterating 4,200 individual PostgreSQL queries across separate connections caused substantial TCP connection overhead (~30s runtime).", "Medium", "Vectorized the multi-threshold evaluation using matrix multiplication in NumPy (np.dot(eval_mat, seed_mat.T)), reducing 1,200-query evaluation time to ~2 seconds while sampling live PostgreSQL queries for real HNSW latency profiling.", "Resolved"),
        ("Cache Staleness & Drift: Cached LLM responses risk becoming outdated without an expiration mechanism.", "Medium", "Implemented a dual-tier TTL system applying native Redis expiration (EX <ttl>) and PostgreSQL expires_at indexing, with an on-demand vacuum button.", "Resolved")
    ]

    for idx, (issue, severity, resolution, final_status) in enumerate(issues_data, 1):
        format_cell_text(t5.rows[idx].cells[0], issue, bold=False, font_size=9)
        format_cell_text(t5.rows[idx].cells[1], severity, bold=True, font_size=9.5, color_rgb=(220, 38, 38) if severity=="High" else (217, 119, 6), align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell_text(t5.rows[idx].cells[2], resolution, bold=False, font_size=9)
        format_cell_text(t5.rows[idx].cells[3], final_status, bold=True, font_size=9.5, color_rgb=(16, 149, 106), align=WD_ALIGN_PARAGRAPH.CENTER)

    # Validation statement
    p45 = doc.paragraphs[45]
    p45.text = ""
    r = p45.add_run("☑ Yes\n☐ Yes, with minor improvements\n☐ No")
    r.bold = True

    # ============================================================
    # 8. Output / Result Screenshots (P48 to P56)
    # ============================================================
    # We will format 5 complete screenshots with images & descriptions!
    # Let's inspect where screenshots are in template:
    # P47: b) Output / Result Screenshots
    # P48: Screenshot 1: ...
    screenshots_info = [
        ("Screenshot 1: The Main Overview & Real-Time Analytics Dashboard",
         "reports_assets/1_dashboard_overview.png",
         "Description: The Cache-Craft central overview dashboard built with Next.js 15, visualizing real-time query volume, cache hit/miss distributions, total estimated cost savings, and average hit latency."),
        ("Screenshot 2: Interactive Chat Playground with Semantic Cache Hit",
         "reports_assets/2_chat_playground.png",
         "Description: Live interactive query execution in the Chat Playground. A paraphrased query triggers a semantic cache hit with ~25ms response time, 0.92 cosine similarity score, and zero token generation cost."),
        ("Screenshot 3: Vector Cache Explorer & Index Inspection",
         "reports_assets/3_cache_explorer.png",
         "Description: Direct inspection of the persistent PostgreSQL pgvector storage layer, displaying query texts, truncated SHA-256 hashes, hit frequencies, response contents, and source origin tags."),
        ("Screenshot 4: System Settings, Dynamic Threshold & Dual-Tier TTL Lifecycle",
         "reports_assets/3_settings_controls.png",
         "Description: The administrative configuration panel allowing runtime tuning of the cosine similarity threshold (0.70 to 0.95), dual-tier TTL cache expiration policies (1h to Permanent), active LLM inference provider switching (Ollama vs. Gemini), and manual database vacuum cleanup."),
        ("Figure 5: Empirical Benchmark Deep Dive & Multi-Baseline Performance Analysis",
         "reports_assets/benchmark_deep_dive.png",
         "Description: Comprehensive 4-panel evaluation across 1,200 benchmark queries: (A) Baseline latency comparison (3.2x overall speedup, 98.9% reduction on hits); (B) Threshold sensitivity curves for Precision, Recall, and F1-score; (C) Hit rate % and LLM token cost savings %; (D) Tail latency percentiles (p50, p90, p99) comparing cache hits vs. LLM cold calls.")
    ]

    # Let's handle screenshots by replacing P48..P56 and inserting necessary paragraphs
    # In template:
    # P48: Screenshot 1:
    # P49: Description:
    # P51: Screenshot 2:
    # P52: Description:
    # P54: Screenshot 3:
    # P55: Description:

    # Screenshot 1
    p48 = doc.paragraphs[48]
    p48.text = ""
    r1 = p48.add_run(screenshots_info[0][0] + "\n")
    r1.bold = True
    p48.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(screenshots_info[0][1]):
        p48.add_run().add_picture(screenshots_info[0][1], width=Inches(6.0))

    p49 = doc.paragraphs[49]
    p49.text = ""
    r1 = p49.add_run("Description: ")
    r1.bold = True
    r2 = p49.add_run(screenshots_info[0][2].replace("Description: ", ""))

    # Screenshot 2
    p51 = doc.paragraphs[51]
    p51.text = ""
    r1 = p51.add_run(screenshots_info[1][0] + "\n")
    r1.bold = True
    p51.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(screenshots_info[1][1]):
        p51.add_run().add_picture(screenshots_info[1][1], width=Inches(6.0))

    p52 = doc.paragraphs[52]
    p52.text = ""
    r1 = p52.add_run("Description: ")
    r1.bold = True
    r2 = p52.add_run(screenshots_info[1][2].replace("Description: ", ""))

    # Screenshot 3
    p54 = doc.paragraphs[54]
    p54.text = ""
    r1 = p54.add_run(screenshots_info[2][0] + "\n")
    r1.bold = True
    p54.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(screenshots_info[2][1]):
        p54.add_run().add_picture(screenshots_info[2][1], width=Inches(6.0))

    p55 = doc.paragraphs[55]
    p55.text = ""
    r1 = p55.add_run("Description: ")
    r1.bold = True
    r2 = p55.add_run(screenshots_info[2][2].replace("Description: ", ""))

    # Now add Screenshot 4 and 5 sequentially before P57
    p_anchor = doc.paragraphs[57]
    for s_title, s_path, s_desc in screenshots_info[3:]:
        p_s = p_anchor.insert_paragraph_before()
        p_s.paragraph_format.space_before = Pt(12)
        p_s.paragraph_format.space_after = Pt(4)
        p_s.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_t = p_s.add_run(s_title + "\n")
        r_t.bold = True
        if os.path.exists(s_path):
            p_s.add_run().add_picture(s_path, width=Inches(6.0))
        
        p_d = p_anchor.insert_paragraph_before()
        p_d.paragraph_format.space_after = Pt(10)
        r_d1 = p_d.add_run("Description: ")
        r_d1.bold = True
        p_d.add_run(s_desc.replace("Description: ", ""))

    # ============================================================
    # 9. Section 7: Final Results and Outcomes
    # ============================================================
    # Look for checkbox paragraph in Section 7
    for p in doc.paragraphs:
        if "Partially Completed" in p.text and "Work in Progress" in p.text:
            p.text = ""
            r = p.add_run("☑ Completed\n☐ Mostly Completed\n☐ Partially Completed\n☐ Work in Progress")
            r.bold = True
        elif p.text.strip() == "Completed Components":
            p.text = ""
            r1 = p.add_run("Completed Components :- ")
            r1.bold = True
            r2 = p.add_run("Decoupled Multi-Tier Architecture (FastAPI + Next.js 15), In-Memory Redis 7 Exact Cache, PostgreSQL 16 + pgvector HNSW Index, Dense Embedding Pipeline (all-MiniLM-L6-v2), Multi-Turn Context Binding & Partition Filtering, Pluggable Multi-LLM Inference Engine (Ollama llama3.2 & Google Gemini 3.8 Flash with Automatic Fallback), Dual-Tier TTL Cache Lifecycle Management, Real-Time SSE Metrics Streaming, 1,200-Query Benchmark Evaluation Suite, 4-Service Docker Compose Containerization Stack.")
        elif p.text.strip() == "Pending Components":
            p.text = ""
            r1 = p.add_run("Pending Components :- ")
            r1.bold = True
            r2 = p.add_run("None")

    # ============================================================
    # 10. Section 8: References and Resources Used (APA 7th Edition)
    # ============================================================
    references_data = [
        '[1] Reiss, F. (2023). "GPTCache: An open-source semantic cache for LLM applications," Towards Data Science. https://towardsdatascience.com/gptcache-an-open-source-semantic-cache-for-llm-applications',
        '[2] Malkov, Y. A., & Yashunin, D. A. (2020). "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs," IEEE Transactions on Pattern Analysis and Machine Intelligence, 42(4), 824–836. https://doi.org/10.1109/TPAMI.2018.2889473',
        '[3] Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), 3982–3992. https://doi.org/10.18653/v1/D19-1410',
        '[4] PostgreSQL Global Development Group. (2024). "PostgreSQL 16 documentation: The pgvector extension for vector similarity search," https://github.com/pgvector/pgvector',
        '[5] Redis Ltd. (2024). "Redis documentation: Memory optimization and eviction policies," https://redis.io/docs/latest/develop/reference/eviction/',
        '[6] Ramírez, S. (2024). "FastAPI documentation: High-performance, modern Python web framework," https://fastapi.tiangolo.com/',
        '[7] Vercel Inc. (2024). "Next.js 15 documentation: The React framework for the Web," https://nextjs.org/docs',
        '[8] Google DeepMind. (2024). "Gemini API documentation: Highly capable multimodal reasoning models," Google Cloud AI. https://ai.google.dev/docs'
    ]

    # Find the [1] Author Name... placeholders and replace them
    ref_idx = 0
    for p in doc.paragraphs:
        if any(p.text.strip().startswith(f"[{i}]") for i in range(1, 6)):
            if ref_idx < len(references_data):
                p.text = ""
                r_num = p.add_run(references_data[ref_idx][:4])
                r_num.bold = True
                p.add_run(references_data[ref_idx][4:])
                ref_idx += 1
        elif "Reference Requirements" in p.text and ref_idx < len(references_data):
            # Insert remaining references before Reference Requirements
            for remaining in references_data[ref_idx:]:
                p_new = p.insert_paragraph_before()
                p_new.paragraph_format.space_before = Pt(2)
                p_new.paragraph_format.space_after = Pt(3)
                r_num = p_new.add_run(remaining[:4])
                r_num.bold = True
                p_new.add_run(remaining[4:])
            ref_idx = len(references_data)

    print(f"Saving finalized report...")
    try:
        doc.save(OUTPUT_PATH)
        print(f"SUCCESS: {OUTPUT_PATH} successfully generated!")
    except PermissionError:
        fallback_path = "Cache-Craft_Reporting_4_Updated.docx"
        print(f"Notice: {OUTPUT_PATH} is currently open in Microsoft Word. Saving to {fallback_path} instead.")
        doc.save(fallback_path)
        print(f"SUCCESS: {fallback_path} successfully generated!")

if __name__ == "__main__":
    main()
