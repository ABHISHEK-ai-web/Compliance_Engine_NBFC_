#!/usr/bin/env python3
"""
Generate sample RBI regulation and internal SOP PDFs for compliance testing.
Run from project root: python sample_data/generate_sample_pdfs.py
"""
import fitz
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent


def write_pdf(filename: str, title: str, sections: list[tuple[str, str]]):
    """Create a multi-section PDF from (heading, body) pairs."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    y = 50
    margin = 50
    max_width = 495

    def add_text(text: str, fontsize: float, bold: bool = False):
        nonlocal y, page
        font = "helv"
        if y > 780:
            page = doc.new_page(width=595, height=842)
            y = 50
        if bold:
            page.insert_text((margin, y), text, fontname=font, fontsize=fontsize)
            y += fontsize + 6
        else:
            # Word-wrap paragraphs
            words = text.split()
            line = ""
            for word in words:
                test = f"{line} {word}".strip()
                if fitz.get_text_length(test, fontname=font, fontsize=fontsize) < max_width:
                    line = test
                else:
                    if line:
                        page.insert_text((margin, y), line, fontname=font, fontsize=fontsize)
                        y += fontsize + 4
                        if y > 780:
                            page = doc.new_page(width=595, height=842)
                            y = 50
                    line = word
            if line:
                page.insert_text((margin, y), line, fontname=font, fontsize=fontsize)
                y += fontsize + 6
        y += 4

    add_text(title, 16, bold=True)
    add_text("Sample document for Compliance Intelligence Engine testing", 9)
    y += 8

    for heading, body in sections:
        add_text(heading, 12, bold=True)
        add_text(body, 10)
        y += 6

    out = OUTPUT_DIR / filename
    doc.save(str(out))
    doc.close()
    print(f"Created: {out}")


RBI_SECTIONS = [
    (
        "1. Introduction",
        "Reserve Bank of India (RBI) Digital Lending Guidelines (September 2022). "
        "Regulated entities (REs) and Lending Service Providers (LSPs) must ensure "
        "transparent, fair, and borrower-centric digital lending practices.",
    ),
    (
        "2. Key Fact Statement (KFS) - Section 3.2",
        "REs shall provide a Key Fact Statement (KFS) to the borrower in a standardized "
        "format before execution of the loan contract. The KFS must include loan amount, "
        "tenure, rate of interest, fees, charges, and all-inclusive Annual Percentage Rate (APR). "
        "Borrower acknowledgment of KFS must be obtained prior to disbursement.",
    ),
    (
        "3. Transparent Pricing - Section 3.4",
        "The all-inclusive Annual Percentage Rate (APR) must be disclosed prominently. "
        "Total cost of borrowing including processing fees, insurance, and other charges "
        "must be stated clearly to enable informed borrower decision-making.",
    ),
    (
        "4. Cooling-Off / Look-Up Period - Section 4.1",
        "Borrowers must be given a cooling-off period (minimum 3 days) or look-up period "
        "during which they may exit the digital loan without penalty by paying principal "
        "and proportionate APR without any foreclosure charges.",
    ),
    (
        "5. Disbursement - Section 4.3",
        "Loan amount shall be disbursed directly to the borrower's bank account only. "
        "No disbursement to third-party accounts except as permitted under applicable law.",
    ),
    (
        "6. Auto-Debit / Repayment - Section 4.5",
        "Setting up auto-debit or e-mandate/NACH for repayment requires explicit consent "
        "from the borrower. Borrower must have option to revoke repayment consent.",
    ),
    (
        "7. Data Privacy - Section 5.3",
        "Borrower data collection must follow data minimization and purpose limitation. "
        "Need-to-know access only. Data retention and data deletion policies must be "
        "defined. Data shall not be stored beyond the stated purpose.",
    ),
    (
        "8. LSP Oversight - Section 2.2",
        "RE remains responsible for actions of Lending Service Providers (LSP). "
        "LSP oversight, third party oversight, and outsourcing arrangements require "
        "periodic monitoring and audit of service provider conduct.",
    ),
    (
        "9. Grievance Redressal - Section 6",
        "REs must establish a grievance redressal mechanism with defined complaint mechanism, "
        "escalation matrix, resolution timelines, and access to RBI Ombudsman scheme.",
    ),
    (
        "10. Video KYC - KYC Directions",
        "Digital onboarding via Video KYC (V-CIP) must comply with RBI KYC Directions 2016 "
        "as amended. Video-based identification process with audit trail is mandatory for "
        "remote customer onboarding.",
    ),
    (
        "11. Fair Practices Code",
        "Regulated entities must adopt and publish Fair Practices Code (FPC) ensuring "
        "ethical conduct, transparency, and protection of borrower rights.",
    ),
]

SOP_SECTIONS = [
    (
        "1. Purpose",
        "This Standard Operating Procedure (SOP) governs digital personal loan origination "
        "at ABC FinTech NBFC. Scope: mobile app and web channel loans up to INR 5 lakh.",
    ),
    (
        "2. Eligibility & Onboarding",
        "Customer must complete PAN verification, Aadhaar OTP, and bank statement upload. "
        "Credit bureau pull is mandatory. Minimum age 21 years and stable income required.",
    ),
    (
        "3. Loan Application Workflow",
        "Step 1: Customer selects loan amount and tenure. Step 2: System runs credit scoring. "
        "Step 3: Offer presented with interest rate and EMI. Step 4: Customer accepts offer "
        "via OTP. Step 5: E-sign loan agreement. Step 6: Disbursement within 24 hours.",
    ),
    (
        "4. Interest & Fees",
        "Interest rate ranges from 18% to 36% per annum based on risk band. Processing fee "
        "up to 3% deducted from disbursement. Late payment penalty of 2% per month on overdue EMI.",
    ),
    (
        "5. Collections",
        "EMI collection via UPI auto-pay where customer opts in during onboarding. "
        "Field collection agency engaged after 60 DPD. Restructuring per internal policy only.",
    ),
    (
        "6. Partner Integration",
        "Loan leads sourced via digital marketplace partners. Partner APIs used for "
        "application data transfer. Commission paid per disbursed loan.",
    ),
    (
        "7. IT Security",
        "Application data encrypted at rest (AES-256) and in transit (TLS 1.2). "
        "Access restricted to authorized operations staff. Annual VAPT conducted.",
    ),
    (
        "8. Roles & Responsibilities",
        "Product team owns policy updates. Operations executes disbursement. "
        "Risk team monitors portfolio quality. Compliance reviews quarterly checklist.",
    ),
]

# Internal SOP intentionally omits: KFS, cooling-off, grievance redressal, data retention,
# APR disclosure, LSP oversight, direct disbursement to borrower account, explicit consent
# for auto-debit, Video KYC, and Fair Practices Code.


def main():
    write_pdf(
        "RBI_Digital_Lending_Guidelines_2022.pdf",
        "RBI Digital Lending Guidelines (2022) - Sample Circular",
        RBI_SECTIONS,
    )
    write_pdf(
        "Internal_Digital_Lending_SOP_ABC_FinTech.pdf",
        "ABC FinTech NBFC - Digital Lending SOP (Internal Policy)",
        SOP_SECTIONS,
    )
    print("\nUpload in the app:")
    print("  Regulation -> RBI_Digital_Lending_Guidelines_2022.pdf")
    print("  Policy     -> Internal_Digital_Lending_SOP_ABC_FinTech.pdf")
    print("Then run Analysis to see compliance gaps.")


if __name__ == "__main__":
    main()
