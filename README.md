# AI Proposal Generator (Streamlit)

## Quickstart
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run ui.py
```

## What it does
- Collects customer inputs
- Shortlists products from `data/products.csv`
- Retrieves relevant snippets from `kb/*.md`
- Creates a proposal plan (mock planner, offline)
- Computes pricing with taxes/discounts from `data/pricing.json`
- Renders Markdown preview and saves a **DOCX** for download

## Customize
- Edit `data/products.csv` (SKUs, features, price)
- Edit `data/pricing.json` (tax, max discount)
- Edit template `templates/proposal.md.j2`
- Add knowledge files in `kb/*.md`
