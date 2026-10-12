"""
build_final_hardbound_report.py — Master Assembler & Generator for Cache-Craft
Final Hard-Bound Project Report (P P Savani University, School of Engineering).

Coordinates modular construction across:
  - styles.py (Typography, XML margins, cell paddings, borders, colors)
  - metadata.py (Authoritative constants, test cases, tables, benchmarks, references)
  - front_matter.py (Cover, Certificate, Declaration, Acknowledgement, Abstract, TOC, LOF, LOT, Abbreviations)
  - chapters_1_to_5.py (Introduction, Organization, Literature Review, Requirements, Methodology)
  - chapters_6_to_10.py (System Design, Tech Stack, Implementation, Testing & Validation, Results)
  - chapters_11_to_15.py (Challenges, Contribution, Limitations & Future Scope, Conclusion, References)
  - appendices.py (Appendices A to H, Annexure Checklist, Formatting Compliance)

After document generation, uses Microsoft Word COM automation to update all fields,
compute exact pagination, and export a print-ready PDF version.
"""

import os
import sys
import time
import docx

from build_report.styles import setup_document_styles
from build_report.front_matter import build_cover_page, build_front_matter_section
from build_report.chapters_1_to_5 import build_chapters_1_to_5
from build_report.chapters_6_to_10 import build_chapters_6_to_10
from build_report.chapters_11_to_15 import build_chapters_11_to_15
from build_report.appendices import build_appendices

OUTPUT_DOCX = "Cache-Craft_Final_Hard_Bound_Project_Report.docx"
OUTPUT_PDF = "Cache-Craft_Final_Hard_Bound_Project_Report.pdf"

def generate_report():
    print("=" * 75)
    print("STARTING CACHE-CRAFT FINAL HARD-BOUND REPORT GENERATION")
    print("=" * 75)
    
    doc = docx.Document()
    
    # 1. Setup Styles and Typography
    print(">> [1/8] Setting up document typography, styles, and color palette...")
    setup_document_styles(doc)
    
    # 2. Cover Page
    print(">> [2/8] Generating formal hard-bound cover page (Section 0)...")
    build_cover_page(doc)
    
    # 3. Front Matter (Certificate, Declaration, Acknowledgement, Abstract, TOC, LOF, LOT, Abbreviations)
    print(">> [3/8] Generating front matter with Roman pagination (Section 1)...")
    build_front_matter_section(doc)
    
    # 4. Chapters 1 to 5
    print(">> [4/8] Generating Chapters 1 to 5 with Arabic pagination (Section 2)...")
    build_chapters_1_to_5(doc)
    
    # 5. Chapters 6 to 10
    print(">> [5/8] Generating Chapters 6 to 10 with architectural figures & tables...")
    build_chapters_6_to_10(doc)
    
    # 6. Chapters 11 to 15
    print(">> [6/8] Generating Chapters 11 to 15, conclusions, and APA references...")
    build_chapters_11_to_15(doc)
    
    # 7. Appendices and Annexure
    print(">> [7/8] Generating Appendices A-H, Annexure Checklist, and Guidelines...")
    build_appendices(doc)
    
    # 8. Save initial DOCX
    print(f">> [8/8] Saving assembled document to '{OUTPUT_DOCX}'...")
    doc.save(OUTPUT_DOCX)
    docx_size_mb = os.path.getsize(OUTPUT_DOCX) / (1024 * 1024)
    print(f"Successfully generated DOCX! File size: {docx_size_mb:.2f} MB")
    
    # =========================================================================
    # WORD COM AUTOMATION: Update fields, pagination, and export PDF
    # =========================================================================
    print("\n" + "=" * 75)
    print("INVOKING MICROSOFT WORD COM AUTOMATION (FIELD UPDATE & PDF EXPORT)")
    print("=" * 75)
    
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        
        docx_abs = os.path.abspath(OUTPUT_DOCX)
        pdf_abs = os.path.abspath(OUTPUT_PDF)
        
        print(f">> Opening '{OUTPUT_DOCX}' in Word background engine...")
        doc_word = word.Documents.Open(docx_abs)
        
        print(">> Updating all dynamic fields and table references...")
        doc_word.Fields.Update()
        
        # Compute exact page count
        # wdStatisticPages = 2
        total_pages = doc_word.ComputeStatistics(2)
        print(f">> Total Computed Document Pages: {total_pages} Pages")
        
        # Save updated docx with refreshed fields
        print(">> Saving updated DOCX...")
        doc_word.Save()
        
        # Export to PDF (wdFormatPDF = 17)
        print(f">> Exporting print-ready PDF to '{OUTPUT_PDF}'...")
        doc_word.SaveAs(pdf_abs, FileFormat=17)
        
        doc_word.Close(False)
        word.Quit()
        
        if os.path.exists(OUTPUT_PDF):
            pdf_size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
            print(f">> Successfully exported PDF! File size: {pdf_size_mb:.2f} MB")
        print("\nAll tasks completed with 100% success!")
        
    except Exception as e:
        print(f"Notice during Word COM automation: {e}")
        print("The DOCX file is completely generated and can be opened directly in Microsoft Word.")

if __name__ == "__main__":
    generate_report()
