# Sample Test Documents

Use these PDFs to test the Compliance Intelligence Engine without sourcing real RBI files.

## Files

| File | Upload as | Purpose |
|------|-----------|---------|
| `RBI_Digital_Lending_Guidelines_2022.pdf` | **RBI Circular** (Regulation) | Sample RBI digital lending requirements (KFS, APR, cooling-off, grievance, etc.) |
| `Internal_Digital_Lending_SOP_ABC_FinTech.pdf` | **Internal SOP** (Policy) | Intentionally incomplete internal policy to trigger gap detection |

## Generate PDFs

If PDFs are missing, run:

```bash
cd backend
source venv/bin/activate
pip install PyMuPDF   # if not already installed
python ../sample_data/generate_sample_pdfs.py
```

## Expected violations (rule engine)

The internal SOP is designed to miss these RBI requirements:

- Key Fact Statement (KFS) disclosure
- Cooling-off / look-up period
- Grievance redressal mechanism
- Data retention / minimization
- All-inclusive APR disclosure
- LSP / third-party oversight
- Direct disbursement to borrower account
- Explicit auto-debit / e-mandate consent
- Video KYC (V-CIP)
- Fair Practices Code

## Test flow

1. Start backend and frontend
2. **Upload Center** → upload regulation PDF
3. **Upload Center** → upload policy PDF
4. **Analysis** → click **Analyze**
5. **Violations** / **Dashboard** → review findings

## Text sources

Plain-text versions (for editing) are in `RBI_Digital_Lending_Guidelines_2022.txt` and `Internal_Digital_Lending_SOP_ABC_FinTech.txt`.
