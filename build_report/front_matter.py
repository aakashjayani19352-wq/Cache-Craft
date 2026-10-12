"""
build_report/front_matter.py — Cover page, Certificate of Completion, Declaration,
Acknowledgement, Abstract, Table of Contents, List of Figures, List of Tables,
and List of Abbreviations according to official PPSU School of Engineering format.
Fully aligned with verified document pagination.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from build_report.styles import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BODY, COLOR_WHITE,
    HEX_HEADER_BG, HEX_ZEBRA_BG,
    set_cell_background, set_cell_margins, set_table_borders,
    add_h1, add_h2, add_p, add_styled_table
)
from build_report.metadata import (
    PROJECT_TITLE, PROJECT_SUBTITLE, FULL_PROJECT_TITLE,
    STUDENT_NAME, ENROLLMENT_NO, BRANCH_NAME, PROGRAM_NAME, SEMESTER,
    CONTACT_NO, EMAIL_ID, INSTITUTE_NAME, SCHOOL_NAME, DEPARTMENT_NAME,
    LOCATION, ACADEMIC_YEAR, PROJECT_TYPE, INSTITUTE_MENTOR, COMPANY_MENTOR,
    START_DATE, END_DATE, ABBREVIATIONS
)

def build_cover_page(doc):
    """Constructs the formal university hard-bound cover page in Section 0."""
    sec0 = doc.sections[0]
    sec0.page_width = Inches(8.27)
    sec0.page_height = Inches(11.69)
    sec0.left_margin = Inches(1.25)
    sec0.right_margin = Inches(1.0)
    sec0.top_margin = Inches(1.0)
    sec0.bottom_margin = Inches(0.8)

    # University Header
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_before = Pt(12)
    p_uni.paragraph_format.space_after = Pt(2)
    r1 = p_uni.add_run(f"{INSTITUTE_NAME}\n")
    r1.bold = True
    r1.font.name = 'Cambria'
    r1.font.size = Pt(18)
    r1.font.color.rgb = COLOR_PRIMARY

    r2 = p_uni.add_run(f"{SCHOOL_NAME}\n")
    r2.bold = True
    r2.font.name = 'Cambria'
    r2.font.size = Pt(14)
    r2.font.color.rgb = COLOR_SECONDARY

    r3 = p_uni.add_run(f"{DEPARTMENT_NAME}\n")
    r3.italic = True
    r3.font.name = 'Cambria'
    r3.font.size = Pt(12)
    r3.font.color.rgb = COLOR_SECONDARY

    # Report Category
    p_cat = doc.add_paragraph()
    p_cat.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cat.paragraph_format.space_before = Pt(24)
    p_cat.paragraph_format.space_after = Pt(4)
    r_cat = p_cat.add_run("FINAL PROJECT REPORT\n(Hard-Bound Academic Project Report)")
    r_cat.bold = True
    r_cat.font.name = 'Cambria'
    r_cat.font.size = Pt(13)
    r_cat.font.color.rgb = COLOR_PRIMARY

    # Project Title Box
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(28)
    p_title.paragraph_format.space_after = Pt(6)
    r_t = p_title.add_run(f"\"{PROJECT_TITLE}\"\n")
    r_t.bold = True
    r_t.font.name = 'Cambria'
    r_t.font.size = Pt(16)
    r_t.font.color.rgb = COLOR_PRIMARY

    r_sub = p_title.add_run(f"{PROJECT_SUBTITLE}")
    r_sub.italic = True
    r_sub.font.name = 'Cambria'
    r_sub.font.size = Pt(12.5)
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Submission Degree Note
    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(28)
    p_deg.paragraph_format.space_after = Pt(14)
    r_deg = p_deg.add_run(
        f"A Project Report Submitted in Partial Fulfillment of the Requirements\n"
        f"for the Degree of Bachelor of Technology in {BRANCH_NAME}\n"
        f"({SEMESTER})"
    )
    r_deg.font.name = 'Cambria'
    r_deg.font.size = Pt(11)
    r_deg.font.color.rgb = COLOR_BODY

    # Student Details Table
    student_table = doc.add_table(rows=6, cols=2)
    student_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(student_table)
    
    meta_rows = [
        ("Candidate Name", STUDENT_NAME),
        ("Enrollment Number", ENROLLMENT_NO),
        ("Branch / Discipline", PROGRAM_NAME),
        ("Project Classification", PROJECT_TYPE),
        ("Institute Guide / Mentor", INSTITUTE_MENTOR),
        ("Academic Year", ACADEMIC_YEAR)
    ]
    for idx, (label, val) in enumerate(meta_rows):
        row = student_table.rows[idx]
        set_cell_background(row.cells[0], HEX_ZEBRA_BG)
        set_cell_background(row.cells[1], "FFFFFF")
        set_cell_margins(row.cells[0], top=60, bottom=60, left=100, right=100)
        set_cell_margins(row.cells[1], top=60, bottom=60, left=100, right=100)
        
        p0 = row.cells[0].paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = 'Cambria'
        r0.font.size = Pt(10)

        p1 = row.cells[1].paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(val)
        r1.font.name = 'Cambria'
        r1.font.size = Pt(10)
        if label in ["Candidate Name", "Enrollment Number", "Institute Guide / Mentor"]:
            r1.bold = True

    for row in student_table.rows:
        row.cells[0].width = Inches(2.4)
        row.cells[1].width = Inches(3.6)

    # Footer note
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(28)
    p_foot.paragraph_format.space_after = Pt(0)
    r_foot = p_foot.add_run(f"{LOCATION} — OCTOBER 2026")
    r_foot.bold = True
    r_foot.font.name = 'Cambria'
    r_foot.font.size = Pt(11)
    r_foot.font.color.rgb = COLOR_PRIMARY


def build_front_matter_section(doc):
    """
    Creates Section 1 for Front Matter with lowerRoman page numbering (i, ii, ...),
    including Certificate, Declaration, Acknowledgement, Abstract, TOC, LOF, LOT, and Abbreviations.
    """
    sec1 = doc.add_section()
    sec1.page_width = Inches(8.27)
    sec1.page_height = Inches(11.69)
    sec1.left_margin = Inches(1.25)
    sec1.right_margin = Inches(1.0)
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(0.75)

    # Set lowerRoman page numbering starting at 1
    sectPr1 = sec1._sectPr
    pgNumType1 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>')
    sectPr1.append(pgNumType1)

    # Unlink header from cover page
    sec1.header.is_linked_to_previous = False
    hp1 = sec1.header.paragraphs[0]
    hp1.text = f"{PROJECT_TITLE}\t{INSTITUTE_NAME} | {SCHOOL_NAME}"
    hp1.runs[0].font.name = 'Cambria'
    hp1.runs[0].font.size = Pt(8.5)
    hp1.runs[0].font.color.rgb = RGBColor(120, 120, 120)

    # Unlink footer and insert centered page number
    sec1.footer.is_linked_to_previous = False
    fp1 = sec1.footer.paragraphs[0]
    fp1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld1 = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    fp1._p.append(fld1)

    # =========================================================================
    # CERTIFICATE OF COMPLETION
    # =========================================================================
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(12)
    p_cert_title.paragraph_format.space_after = Pt(2)
    r_c1 = p_cert_title.add_run(f"{INSTITUTE_NAME}\n{SCHOOL_NAME}\n")
    r_c1.bold = True
    r_c1.font.name = 'Cambria'
    r_c1.font.size = Pt(14)
    r_c1.font.color.rgb = COLOR_PRIMARY

    r_c2 = p_cert_title.add_run("CERTIFICATE OF COMPLETION")
    r_c2.bold = True
    r_c2.font.name = 'Cambria'
    r_c2.font.size = Pt(16)
    r_c2.font.color.rgb = COLOR_PRIMARY

    add_p(
        doc,
        f"This is to certify that Mr. {STUDENT_NAME}, Enrollment No.: {ENROLLMENT_NO}, a bonafide student of "
        f"{PROGRAM_NAME}, {SEMESTER}, has successfully completed the User Defined Project (UDP) titled "
        f"\"{FULL_PROJECT_TITLE}\" during the academic period from {START_DATE} to {END_DATE} at {INSTITUTE_NAME}, "
        f"{SCHOOL_NAME}, {DEPARTMENT_NAME}.",
        space_after=8
    )

    add_p(
        doc,
        "The project work, algorithmic implementation, multi-tier caching engine, empirical benchmark evaluation on "
        "the 1,200-query corpus, full-stack Next.js web application, and comprehensive documentation embodied in this "
        "report have been thoroughly investigated, implemented, and validated under our continuous supervision. The work "
        "demonstrated satisfies the academic and engineering standards prescribed by the University for the degree of "
        f"Bachelor of Technology in {BRANCH_NAME}.",
        space_after=24
    )

    p_issue = doc.add_paragraph()
    p_issue.paragraph_format.space_after = Pt(36)
    r_iss = p_issue.add_run(f"Date of Issue: 03 / 10 / 2026\t\tPlace: {LOCATION}")
    r_iss.bold = True
    r_iss.font.name = 'Cambria'
    r_iss.font.size = Pt(11)

    # Signatures Table
    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.rows[0].cells[0].paragraphs[0].text = "_________________________________________\nMr. Anurag Yadav\nInstitute Project Guide / Mentor\nDepartment of Information Technology"
    sig_table.rows[0].cells[1].paragraphs[0].text = "_________________________________________\nHead of Department\nDepartment of Information Technology\nSchool of Engineering, PPSU"
    sig_table.rows[1].cells[0].paragraphs[0].text = "\n\n_________________________________________\nExternal Examiner Signature"
    sig_table.rows[1].cells[1].paragraphs[0].text = "\n\n_________________________________________\nDean / Principal\nSchool of Engineering, PPSU"
    
    for row in sig_table.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.paragraphs[0].paragraph_format.line_spacing = 1.15
            for run in cell.paragraphs[0].runs:
                run.font.name = 'Cambria'
                run.font.size = Pt(10)
        row.cells[0].width = Inches(3.0)
        row.cells[1].width = Inches(3.0)

    # =========================================================================
    # DECLARATION
    # =========================================================================
    doc.add_page_break()
    p_dec_title = doc.add_paragraph()
    p_dec_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dec_title.paragraph_format.space_before = Pt(12)
    p_dec_title.paragraph_format.space_after = Pt(14)
    r_dec = p_dec_title.add_run("CANDIDATE DECLARATION")
    r_dec.bold = True
    r_dec.font.name = 'Cambria'
    r_dec.font.size = Pt(16)
    r_dec.font.color.rgb = COLOR_PRIMARY

    add_p(
        doc,
        f"I, {STUDENT_NAME}, Enrollment Number {ENROLLMENT_NO}, hereby declare that this final project report entitled "
        f"\"{FULL_PROJECT_TITLE}\" is a consolidated, authentic, and original record of the engineering research and "
        f"development work carried out by me as a User Defined Project (UDP) during the 7th Semester of the B.Tech program "
        f"in {BRANCH_NAME} at {INSTITUTE_NAME}, {SCHOOL_NAME}, Surat.",
        space_after=10
    )

    add_p(
        doc,
        "I further declare that this report represents my own intellectual and engineering efforts under the supervision "
        f"of my Institute Mentor, {INSTITUTE_MENTOR}. The codebase, empirical benchmark data across 1,200 corpus queries, "
        "system architecture diagrams, user interface components, and performance measurements presented herein are genuine "
        "and have not been submitted in part or full for the award of any other degree, diploma, fellowship, or similar title "
        "to any other university or institute.",
        space_after=10
    )

    add_p(
        doc,
        "All literature references, open-source software libraries, datasets, and foundational models (including PostgreSQL "
        "pgvector, sentence-transformers, Redis, Google Gemini, Ollama llama3.2, and Next.js) utilized during this work have "
        "been duly acknowledged and cited in accordance with academic standards and APA 7th edition formatting.",
        space_after=36
    )

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.space_after = Pt(10)
    r_s = p_sig.add_run(
        f"_________________________________________\n"
        f"{STUDENT_NAME}\n"
        f"Enrollment No.: {ENROLLMENT_NO}\n"
        f"B.Tech Information Technology, 7th Semester\n"
        f"P P Savani University, Surat"
    )
    r_s.font.name = 'Cambria'
    r_s.font.size = Pt(11)
    r_s.bold = True

    p_dp = doc.add_paragraph()
    p_dp.paragraph_format.space_before = Pt(20)
    r_dp = p_dp.add_run(f"Date: 03 / 10 / 2026\t\tPlace: {LOCATION}")
    r_dp.font.name = 'Cambria'
    r_dp.font.size = Pt(11)

    # =========================================================================
    # ACKNOWLEDGEMENT
    # =========================================================================
    doc.add_page_break()
    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack_title.paragraph_format.space_before = Pt(12)
    p_ack_title.paragraph_format.space_after = Pt(14)
    r_ack = p_ack_title.add_run("ACKNOWLEDGEMENT")
    r_ack.bold = True
    r_ack.font.name = 'Cambria'
    r_ack.font.size = Pt(16)
    r_ack.font.color.rgb = COLOR_PRIMARY

    add_p(
        doc,
        f"I take immense pleasure in expressing my profound gratitude and indebtedness to {INSTITUTE_NAME}, {SCHOOL_NAME}, "
        f"and the {DEPARTMENT_NAME} for providing an intellectually stimulating environment and outstanding computational "
        "facilities that made the successful execution of this User Defined Project possible.",
        space_after=10
    )

    add_p(
        doc,
        f"I express my deepest gratitude to my esteemed Institute Guide and Mentor, {INSTITUTE_MENTOR}, for his invaluable "
        "guidance, keen technical insights, constant encouragement, and constructive critique throughout the developmental "
        "lifecycle of Cache-Craft. His deep knowledge of distributed systems and machine learning pipelines proved instrumental "
        "in shaping the multi-tier routing architecture, resolving complex vector distance space anomalies, and establishing "
        "rigorous empirical benchmarking methodologies.",
        space_after=10
    )

    add_p(
        doc,
        "I also extend my sincere appreciation to the Head of the Department and the faculty members of the Department of "
        "Information Technology for their continuous academic support, constructive evaluations during the four milestone "
        "reporting defenses, and helpful feedback on system design and validation.",
        space_after=10
    )

    add_p(
        doc,
        "Special thanks are due to my peers and fellow researchers who participated in user acceptance testing and provided "
        "insightful feedback on the interactive chat playground and real-time observability telemetry. Lastly, I am eternally "
        "grateful to my parents and family for their unwavering moral support, patience, and encouragement throughout my academic journey.",
        space_after=30
    )

    p_acksig = doc.add_paragraph()
    p_acksig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_as = p_acksig.add_run(f"{STUDENT_NAME}\nEnrollment No.: {ENROLLMENT_NO}")
    r_as.bold = True
    r_as.font.name = 'Cambria'
    r_as.font.size = Pt(11)

    # =========================================================================
    # ABSTRACT / EXECUTIVE SUMMARY
    # =========================================================================
    doc.add_page_break()
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_title.paragraph_format.space_before = Pt(12)
    p_abs_title.paragraph_format.space_after = Pt(14)
    r_abs = p_abs_title.add_run("ABSTRACT / EXECUTIVE SUMMARY")
    r_abs.bold = True
    r_abs.font.name = 'Cambria'
    r_abs.font.size = Pt(16)
    r_abs.font.color.rgb = COLOR_PRIMARY

    add_p(
        doc,
        "The rapid industrial proliferation of Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) "
        "pipelines has created a critical operational bottleneck characterized by excessive inference latency (often exceeding "
        "2,000 to 4,000 milliseconds) and steep recurring financial expenditures driven by per-token cloud API billing. While "
        "traditional web architectures rely heavily on deterministic key-value caching, conventional exact-match caches fail "
        "entirely in generative AI workflows because natural language queries expressing identical semantic intent exhibit "
        "infinite syntactic variations. To overcome this fundamental limitation, this project designs, implements, and "
        "empirically evaluates Cache-Craft: an autonomous, multi-tier semantic RAG router and intelligent caching middleware.",
        space_after=10
    )

    add_p(
        doc,
        "Cache-Craft introduces an engineered three-tier hierarchical architecture consisting of: (1) an L0 sub-millisecond "
        "SHA-256 exact match bypass, (2) an L1 in-memory LRU session buffer, and (3) an L2 semantic vector cache powered by "
        "sentence-transformers/all-MiniLM-L6-v2 (384-dimensional dense embeddings) coupled with a PostgreSQL 16 pgvector "
        "Hierarchical Navigable Small World (HNSW) graph index. Incoming natural language queries are projected into a unit-normalized "
        "dense vector space, and semantic similarity is evaluated using an optimized cosine distance metric against a dynamically "
        "configurable similarity threshold (tau). When semantic similarity meets or exceeds the threshold, verified responses "
        "are delivered in approximately 25 milliseconds, completely bypassing costly LLM generation. When a semantic miss occurs, "
        "queries are routed to a dual-provider inference engine featuring Google Gemini 3.8 Flash with an automated, transparent "
        "fallback to an offline local Ollama llama3.2 daemon during HTTP 503 errors or quota limits.",
        space_after=10
    )

    add_p(
        doc,
        "Rigorous empirical validation conducted across a curated 1,200-query benchmark corpus (500 pre-seeded queries, 500 "
        "natural language paraphrases, and 200 out-of-domain negative controls) demonstrated that an optimal threshold of tau = 0.70 "
        "achieves an F1-score of 0.9806 with 100.0% precision (zero false positives) and 96.20% semantic recall. Under realistic "
        "evaluation workloads, Cache-Craft achieved a 68.71% semantic hit rate, reducing average end-to-end query latency from "
        "2,400.0 ms to 768.26 ms (a 3.2x overall speedup) while decreasing token API expenditures by exactly 68.71%. The entire "
        "system is packaged with an enterprise-grade Next.js 15 dark-glassmorphism dashboard featuring real-time Server-Sent Events "
        "(SSE) telemetry, interactive prompt history navigation, and hardware device authorization boundaries.",
        space_after=16
    )

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(8)
    p_kw.paragraph_format.space_after = Pt(8)
    r_kwt = p_kw.add_run("Keywords: ")
    r_kwt.bold = True
    r_kwt.font.name = 'Cambria'
    r_kwt.font.size = Pt(11)
    r_kw = p_kw.add_run(
        "Semantic Caching, Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), "
        "pgvector, Hierarchical Navigable Small World (HNSW), Cosine Similarity, FastAPI, Next.js 15, "
        "Inference Acceleration, Token Cost Reduction, Ollama, Google Gemini."
    )
    r_kw.italic = True
    r_kw.font.name = 'Cambria'
    r_kw.font.size = Pt(10.5)

    # =========================================================================
    # TABLE OF CONTENTS (EXACT ALIGNED PAGINATION)
    # =========================================================================
    doc.add_page_break()
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.paragraph_format.space_before = Pt(12)
    p_toc_title.paragraph_format.space_after = Pt(14)
    r_toc = p_toc_title.add_run("TABLE OF CONTENTS")
    r_toc.bold = True
    r_toc.font.name = 'Cambria'
    r_toc.font.size = Pt(16)
    r_toc.font.color.rgb = COLOR_PRIMARY

    toc_headers = ["Chapter / Section", "Title / Content Description", "Page No."]
    toc_data = [
        ["Preliminary", "Certificate of Completion", "i"],
        ["Preliminary", "Candidate Declaration", "ii"],
        ["Preliminary", "Acknowledgement", "iii"],
        ["Preliminary", "Abstract / Executive Summary", "iv"],
        ["Preliminary", "Table of Contents", "vi"],
        ["Preliminary", "List of Figures", "xi"],
        ["Preliminary", "List of Tables", "xii"],
        ["Preliminary", "List of Abbreviations and Acronyms", "xiv"],
        ["CHAPTER 1", "INTRODUCTION", "1"],
        ["1.1", "Background of the Project", "1"],
        ["1.2", "Problem Statement", "2"],
        ["1.3", "Need / Motivation for the Project", "3"],
        ["1.4", "Objectives of the Project", "3"],
        ["1.5", "Scope of the Project & Scope Matrix (Table 1.1)", "4"],
        ["1.6", "Expected Outcomes vs. Final Achieved Outcomes (Table 1.2)", "5"],
        ["1.7", "Organization of the Report", "6"],
        ["CHAPTER 2", "ORGANIZATION / UDP PROFILE", "7"],
        ["2.1", "Organization / Institutional Overview (P P Savani University)", "7"],
        ["2.2", "Department / Domain Profile (IT & AI Systems)", "7"],
        ["2.3", "Role and Individual Responsibilities", "7"],
        ["2.4", "Development / Work Environment & Specifications (Table 2.1)", "8"],
        ["2.5", "UDP Project Administrative Details", "9"],
        ["CHAPTER 3", "LITERATURE REVIEW / BACKGROUND STUDY", "10"],
        ["3.1", "Domain Background: Semantic Search & Inference Economics", "10"],
        ["3.2", "Existing Approaches & Related Work (Table 3.1)", "10"],
        ["3.3", "Comparative Analysis (Table 3.2)", "11"],
        ["3.4", "Research Gap and Project Justification", "12"],
        ["CHAPTER 4", "REQUIREMENTS ANALYSIS AND PROJECT SCOPE", "14"],
        ["4.1", "Functional Requirements Specification (Table 4.1)", "14"],
        ["4.2", "Non-Functional Requirements Specification (Table 4.2)", "15"],
        ["4.3", "Hardware Requirements and Infrastructure (Table 4.3)", "16"],
        ["4.4", "Software Requirements and Dependencies (Table 4.4)", "16"],
        ["4.5", "Data / Dataset Requirements (Table 4.5)", "17"],
        ["4.6", "System Constraints and Operational Assumptions", "18"],
        ["CHAPTER 5", "METHODOLOGY AND PROJECT PLANNING", "19"],
        ["5.1", "Final Development and Research Methodology", "19"],
        ["5.2", "Project Workflow & Process Architecture (Figure 5.1)", "19"],
        ["5.3", "Project Phases and Deliverables (Table 5.1)", "20"],
        ["5.4", "Progress Report Consolidation (Reports 1 to 4) (Table 5.2)", "21"],
        ["5.5", "Project Schedule and 16-Week Gantt Timeline (Table 5.3)", "21"],
        ["CHAPTER 6", "SYSTEM ANALYSIS AND DESIGN", "23"],
        ["6.1", "Existing System Analysis & Bottleneck Identification", "23"],
        ["6.2", "Proposed Multi-Tier Autonomous System Architecture", "23"],
        ["6.3", "High-Performance System Architecture (Figure 6.1)", "24"],
        ["6.4", "Autonomous Routing Decision Tree & Workflow (Figure 6.2)", "25"],
        ["6.5", "UML Class, Sequence, Component & Block Diagrams (Figures 6.3 & 6.4)", "25"],
        ["6.6", "Module-wise Detailed Design (Table 6.1)", "27"],
        ["6.7", "Database / Relational pgvector Data Design (Table 6.2)", "29"],
        ["6.8", "User Interface & Experience Design System", "30"],
        ["CHAPTER 7", "TECHNOLOGY STACK AND DEVELOPMENT ENVIRONMENT", "32"],
        ["7.1", "Programming Languages (Python 3.11, TypeScript, SQL)", "32"],
        ["7.2", "Frameworks, Libraries & External APIs", "32"],
        ["7.3", "Database & In-Memory Storage Systems", "32"],
        ["7.4", "Hardware, Cloud & Deployment Environments", "32"],
        ["7.5", "Development, Version Control & Testing Tooling", "33"],
        ["7.6", "Technology Selection Rationale & Trade-Off Analysis (Table 7.6)", "33"],
        ["CHAPTER 8", "SYSTEM IMPLEMENTATION", "35"],
        ["8.1", "Implementation Architecture Overview", "35"],
        ["8.2", "Module 1: Multi-Tier Cache Router Core", "35"],
        ["8.3", "Module 2: Dense Vector Embedding & Normalization Engine", "35"],
        ["8.4", "Module 3: Dynamic Multi-LLM Router & Failover Engine", "35"],
        ["8.5", "Module 4: Hardware Device Authorization & Isolation Boundary", "35"],
        ["8.6", "Module 5: Real-Time Observability & SSE Telemetry Engine", "36"],
        ["8.7", "Module 6: Interactive Web Dashboard & Chat Playground", "36"],
        ["8.8", "Module 7: Automated Benchmarking & Matrix Validation Suite", "36"],
        ["8.9", "Mathematical Formulations: Cosine Metric & HNSW Graph Indexing", "36"],
        ["8.10", "RESTful API Endpoints Specification (Table 8.1)", "37"],
        ["8.11", "Database Implementation & pgvector DDL Excerpts", "38"],
        ["8.12", "Security Architecture, CORS & GPU Access Control", "39"],
        ["8.13", "End-to-End System Integration", "39"],
        ["CHAPTER 9", "TESTING AND VALIDATION", "40"],
        ["9.1", "Multi-Tiered Testing Strategy & Verification Methodology", "40"],
        ["9.2", "Unit and Module Testing Suite (25 Tests) (Table 9.1)", "40"],
        ["9.3", "Functional Testing Suite (40 Tests) (Table 9.2)", "41"],
        ["9.4", "Integration Testing Suite (35 Tests) (Table 9.3)", "42"],
        ["9.5", "System and Resilience Testing Suite (25 Tests) (Table 9.4)", "43"],
        ["9.6", "Performance, Load & Concurrency Testing Suite (20 Tests) (Table 9.5)", "44"],
        ["9.7", "User Acceptance Testing (UAT) Scenarios (18 Tests) (Table 9.6)", "45"],
        ["9.8", "Experimental Validation on 1,200 Benchmark Corpus", "46"],
        ["9.9", "Defects Discovered, Root Causes & Resolutions (Table 9.7)", "46"],
        ["9.10", "Formal Validation Statement (163/163 Tests Passed)", "48"],
        ["CHAPTER 10", "RESULTS AND PERFORMANCE ANALYSIS", "49"],
        ["10.1", "Final Empirical Results Summary", "49"],
        ["10.2", "Objective-wise Milestone Achievement (Table 10.1)", "49"],
        ["10.3", "Similarity Threshold Sweep & Metric Analysis (Table 10.2)", "50"],
        ["10.4", "Baseline Comparative Results (Table 10.3)", "50"],
        ["10.5", "Empirical Charts & Production Screenshots (Figures 10.1 to 10.6)", "51"],
        ["10.6", "Results Discussion & Economic Cost Savings Analysis", "54"],
        ["CHAPTER 11", "CHALLENGES, SOLUTIONS AND IMPROVEMENTS", "55"],
        ["11.1", "Major Architectural & Algorithmic Challenges", "55"],
        ["11.2", "Technical Challenges & Engineering Resolutions", "55"],
        ["11.3", "Process, Dataset & Environment Challenges", "56"],
        ["11.4", "Architectural Improvements Made During Development (Table 11.1)", "56"],
        ["11.5", "Lessons Learned from Systems Engineering Challenges", "57"],
        ["CHAPTER 12", "INDIVIDUAL CONTRIBUTION AND PROFESSIONAL LEARNING", "58"],
        ["12.1", "Individual Contribution & Project Ownership (100% Solo Ownership)", "58"],
        ["12.2", "Technical Competencies & Skills Acquired (Table 12.1)", "58"],
        ["12.3", "Professional, Research & Architectural Skills Acquired (Table 12.2)", "59"],
        ["12.4", "Major Academic and Professional Learning Outcomes", "59"],
        ["CHAPTER 13", "LIMITATIONS AND FUTURE SCOPE", "60"],
        ["13.1", "Current Technical Limitations (Table 13.1)", "60"],
        ["13.2", "Future Scope & Developmental Roadmap (Table 13.2)", "60"],
        ["13.3", "Scalability, Clustering & Enterprise Extension Opportunities", "61"],
        ["CHAPTER 14", "CONCLUSION", "62"],
        ["14.1", "Final Project Completion Status (Table 14.1)", "62"],
        ["14.2", "Concluding Remarks & Architectural Significance", "62"],
        ["CHAPTER 15", "REFERENCES (APA 7th Edition)", "64"],
        ["APPENDICES", "SUPPORTING DOCUMENTS AND EVIDENCE", "66"],
        ["Appendix A", "Progress Report 1 Summary (Foundations & Concept)", "66"],
        ["Appendix B", "Progress Report 2 Summary (Prototype & Proof)", "66"],
        ["Appendix C", "Progress Report 3 Summary (pgvector & Frontend V1)", "66"],
        ["Appendix D", "Reporting 4 / Final Evaluation Summary", "67"],
        ["Appendix E", "Additional Benchmark Visualizations & Data Callouts", "67"],
        ["Appendix F", "Certificates & Academic Evidence (NPTEL OS Certificate)", "67"],
        ["Appendix G", "Source Code, Git Repository & Cloud Deployment Evidence", "68"],
        ["Appendix H", "Mentor Evaluation & Continuous Review Rubrics", "69"],
        ["ANNEXURE", "Final Hard-Bound Submission Checklist (Table Annexure.1)", "71"],
        ["GUIDELINES", "PPSU School of Engineering Formatting Compliance Statement", "73"]
    ]
    add_styled_table(
        doc,
        toc_headers,
        toc_data,
        col_widths=[1.6, 4.0, 0.8],
        alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # =========================================================================
    # LIST OF FIGURES (EXACT ALIGNED PAGINATION)
    # =========================================================================
    doc.add_page_break()
    p_lof_title = doc.add_paragraph()
    p_lof_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_title.paragraph_format.space_before = Pt(12)
    p_lof_title.paragraph_format.space_after = Pt(14)
    r_lof = p_lof_title.add_run("LIST OF FIGURES")
    r_lof.bold = True
    r_lof.font.name = 'Cambria'
    r_lof.font.size = Pt(16)
    r_lof.font.color.rgb = COLOR_PRIMARY

    lof_headers = ["Figure No.", "Figure Caption / Architectural Description", "Page No."]
    lof_data = [
        ["Figure 5.1", "Cache-Craft End-to-End System Development and Research Workflow", "20"],
        ["Figure 6.1", "High-Performance Multi-Tier System Architecture Diagram (L0/L1/L2)", "24"],
        ["Figure 6.2", "Autonomous Semantic Routing Decision Tree and Multi-Tier Logic Flowchart", "25"],
        ["Figure 6.3", "Multi-Panel UML Class, Sequence, and Component Architecture Diagrams", "26"],
        ["Figure 6.4", "Hardware Infrastructure and Middleware Layer Physical Block Diagram", "27"],
        ["Figure 10.1", "Empirical Latency Profiling and Cloud Cost Reduction Benchmark Curves", "51"],
        ["Figure 10.2", "Threshold Sensitivity vs. Precision, Recall, and F1-Score Trade-Off Analysis", "52"],
        ["Figure 10.3", "Next.js 15 Web Dashboard and Real-Time Telemetry Overview", "52"],
        ["Figure 10.4", "Interactive Semantic Chat Playground with L1 Cache-Hit Highlighting", "53"],
        ["Figure 10.5", "Vector Cache Explorer and Semantic Inverted Index Browser", "53"],
        ["Figure 10.6", "Dynamic Similarity Threshold Controls and Device Authorization Panel", "54"],
        ["Figure F.1", "NPTEL Operating Systems Fundamentals and Multithreading Certification", "68"]
    ]
    add_styled_table(
        doc,
        lof_headers,
        lof_data,
        col_widths=[1.2, 4.4, 0.8],
        alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # =========================================================================
    # LIST OF TABLES (EXACT ALIGNED PAGINATION)
    # =========================================================================
    doc.add_page_break()
    p_lot_title = doc.add_paragraph()
    p_lot_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot_title.paragraph_format.space_before = Pt(12)
    p_lot_title.paragraph_format.space_after = Pt(14)
    r_lot = p_lot_title.add_run("LIST OF TABLES")
    r_lot.bold = True
    r_lot.font.name = 'Cambria'
    r_lot.font.size = Pt(16)
    r_lot.font.color.rgb = COLOR_PRIMARY

    lot_headers = ["Table No.", "Table Title / Context", "Page No."]
    lot_data = [
        ["Table 1.1", "Cache-Craft Project Scope Matrix (In Scope vs. Out of Scope)", "4"],
        ["Table 1.2", "Expected Outcomes vs. Final Achieved Outcomes", "5"],
        ["Table 2.1", "UDP Workstation Hardware and System Specifications", "8"],
        ["Table 3.1", "Overview of Existing Semantic Caching and RAG Routing Approaches", "10"],
        ["Table 3.2", "Comprehensive Feature-by-Feature Comparative Matrix", "11"],
        ["Table 4.1", "Functional Requirements Specification (FR-01 to FR-10)", "14"],
        ["Table 4.2", "Non-Functional Requirements Specification (NFR-01 to NFR-08)", "15"],
        ["Table 4.3", "Hardware Requirements and Infrastructure Specifications", "16"],
        ["Table 4.4", "Software Requirements, Frameworks, and Runtime Dependencies", "16"],
        ["Table 4.5", "Benchmark Dataset Requirements and Corpus Distribution (1,200 Queries)", "18"],
        ["Table 5.1", "Project Phases, Milestones, and Key Deliverables", "20"],
        ["Table 5.2", "Progress Report Consolidation and Developmental Evolution (Reports 1 to 4)", "21"],
        ["Table 5.3", "Comprehensive 16-Week Project Schedule and Timeline (Gantt Representation)", "21"],
        ["Table 6.1", "Module-wise Architectural Design and Functional Responsibilities", "27"],
        ["Table 6.2", "PostgreSQL Database Schema and pgvector Index Definitions", "29"],
        ["Table 7.6", "Technology Selection Rationale and Architectural Trade-Off Analysis", "33"],
        ["Table 8.1", "Cache-Craft RESTful API Endpoints Specification", "37"],
        ["Table 9.1", "Unit and Module Testing Suite Test Cases (25 Tests)", "40"],
        ["Table 9.2", "Functional Testing Suite Test Cases (40 Tests)", "41"],
        ["Table 9.3", "Integration Testing Suite Test Cases (35 Tests)", "42"],
        ["Table 9.4", "End-to-End System and Resilience Testing Test Cases (25 Tests)", "43"],
        ["Table 9.5", "Performance, Load, and Concurrency Testing Test Cases (20 Tests)", "44"],
        ["Table 9.6", "User Acceptance Testing (UAT) Usability Scenarios (18 Tests)", "45"],
        ["Table 9.7", "Major Defects Discovered, Root Causes, and Technical Resolutions", "46"],
        ["Table 10.1", "Objective-wise Milestone and Metric Achievement Summary", "49"],
        ["Table 10.2", "Empirical Similarity Threshold Sweep and Benchmark Evaluation (N=700)", "50"],
        ["Table 10.3", "Baseline Comparative Results (Direct LLM vs. Exact Hash vs. Cache-Craft)", "51"],
        ["Table 11.1", "Architectural Improvements and Developmental Refinements", "56"],
        ["Table 12.1", "Technical Skills and Engineering Competencies Acquired", "58"],
        ["Table 12.2", "Professional, Research, and Project Management Skills Acquired", "59"],
        ["Table 13.1", "Current System Limitations and Operational Boundaries", "60"],
        ["Table 13.2", "Future Scope, Planned Enhancements, and Scalability Opportunities", "61"],
        ["Table 14.1", "Final Comprehensive Project Completion Status Matrix", "62"],
        ["Table H.1", "Final Project Evaluation Rubric and Grading Criteria", "69"],
        ["Table Annexure.1", "Final Hard-Bound Submission Checklist (17 Verification Points)", "71"]
    ]
    add_styled_table(
        doc,
        lot_headers,
        lot_data,
        col_widths=[1.2, 4.4, 0.8],
        alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    )

    # =========================================================================
    # LIST OF ABBREVIATIONS / ACRONYMS
    # =========================================================================
    doc.add_page_break()
    p_abb_title = doc.add_paragraph()
    p_abb_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abb_title.paragraph_format.space_before = Pt(12)
    p_abb_title.paragraph_format.space_after = Pt(14)
    r_abb = p_abb_title.add_run("LIST OF ABBREVIATIONS / ACRONYMS")
    r_abb.bold = True
    r_abb.font.name = 'Cambria'
    r_abb.font.size = Pt(16)
    r_abb.font.color.rgb = COLOR_PRIMARY

    abb_headers = ["Abbreviation / Acronym", "Full Expansion and Engineering Context"]
    add_styled_table(
        doc,
        abb_headers,
        ABBREVIATIONS,
        col_widths=[1.8, 4.6],
        alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    )
