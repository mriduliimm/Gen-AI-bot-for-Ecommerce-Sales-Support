import os, json, io
import streamlit as st
import pandas as pd
from schemas import CustomerInput
from catalog import load_catalog, shortlist_by_requirements, get_sku
from retrieval import MiniRetriever
from planner import mock_plan
from pricing import compute_pricing
from templating import render_markdown, save_docx_from_context
from compliance import check_claims, mandatory_clauses
from store import save_session

st.set_page_config(page_title="AI Proposal Generator", page_icon="🧠", layout="wide")
st.title("🧠 AI Proposal Generator — Sales Proposals in Minutes")

# Sidebar: basic info
st.sidebar.header("Configuration")
currency = st.sidebar.selectbox("Currency", ["INR","USD","EUR"], index=0)
discount_pct = st.sidebar.slider("Discount %", 0.0, 30.0, 10.0, 1.0)
topk = st.sidebar.slider("Knowledge Top-K", 1, 10, 5)

st.sidebar.markdown("---")
st.sidebar.caption("Data files live in ./data and ./kb. Edit CSV/MD to customize.")

# Load data & retriever
df = load_catalog()
retriever = MiniRetriever(df)

# --- Input Forms ---
with st.form("customer_form"):
    st.subheader("1) Customer & Opportunity")
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company", "Acme Ltd")
        industry = st.text_input("Industry", "Retail")
        region = st.text_input("Region", "IN")
        use_case = st.text_input("Primary Use-case", "Personalized recommendations")
    with col2:
        # Use comma-separated text (compatible with all Streamlit versions)
        objectives_csv = st.text_input(
            "Objectives (comma separated)",
            "Improve conversion,Increase AOV,Reduce churn"
        )
        timeline_weeks = st.number_input("Timeline (weeks)", 1, 52, 8)
        budget_min = st.number_input("Budget Min", 0.0, 1e9, 100000.0, step=5000.0, format="%f")
        budget_max = st.number_input("Budget Max", 0.0, 1e9, 500000.0, step=5000.0, format="%f")

    discovery_notes = st.text_area(
        "Discovery Notes / RFP excerpt (optional)",
        "They need web personalization and a CDP integration with consent management."
    )

    st.subheader("2) Scope & Must-haves")
    must_have_text = st.text_input("Must-have features (comma separated)", "recommendations, cdp, consent")

    # Submit button must be inside the form:
    submitted = st.form_submit_button("Generate Draft Proposal")

# Visible debug (helps confirm your click is seen)
st.caption(f"Debug — submitted={submitted}")

# Prepare containers so sections always exist on the page
preview_container = st.container()
download_container = st.container()
error_container = st.container()

# Make sure output dir exists
import os, json, traceback
os.makedirs("out", exist_ok=True)

# Parse comma-separated objectives once here
objectives = [o.strip() for o in objectives_csv.split(",") if o.strip()]

if submitted:
    try:
        # Basic validation (show errors in the page, not just terminal)
        missing = []
        if not company: missing.append("Company")
        if not industry: missing.append("Industry")
        if not use_case: missing.append("Primary Use-case")
        if missing:
            error_container.error("Please fill required fields: " + ", ".join(missing))
            st.stop()

        # Data files checks
        if not os.path.exists("data/products.csv"):
            error_container.error("Missing file: data/products.csv")
            st.stop()
        if not os.path.exists("data/pricing.json"):
            error_container.error("Missing file: data/pricing.json")
            st.stop()

        # --- Normal flow ---
        must_have_features = [x.strip() for x in must_have_text.split(",") if x.strip()]

        # Build the CustomerInput
        ci = CustomerInput(
            company=company, industry=industry, region=region, use_case=use_case,
            objectives=objectives, timeline_weeks=int(timeline_weeks),
            budget_min=float(budget_min) if budget_min else None,
            budget_max=float(budget_max) if budget_max else None,
            discovery_notes=discovery_notes
        )

        # Shortlist & retrieval
        short = shortlist_by_requirements(df, must_have_features, region=region, budget_max=ci.budget_max)
        if short.empty:
            st.warning("No matching SKUs found with current filters. Showing all SKUs as fallback.")
            short = df.copy()

        query = ci.use_case + "\n" + "; ".join(ci.objectives) + "\n" + (ci.discovery_notes or "")
        hits = retriever.search(query, k=topk)
        top_snips = [{"text": d, "id": i} for d, i in hits]

        # Plan & pricing
        shortlisted_rows = short.to_dict(orient="records")
        plan = mock_plan(customer=ci.model_dump(), objectives=ci.objectives,
                         shortlisted_skus=shortlisted_rows, top_snippets=top_snips)

        from pricing import compute_pricing
        pr = compute_pricing(plan.pricing.get("items", []), currency=currency, discount_pct=discount_pct)

        # Decorate SKUs with names
        sku_map = {r['sku']: r for r in shortlisted_rows}
        sel_skus = []
        for sel in plan.selected_skus:
            r = sku_map.get(sel.sku, {})
            sel_skus.append({"sku": sel.sku, "name": r.get("name",""), "reason": sel.reason})

        context = {
            "title": f"Proposal for {ci.company}",
            "company": ci.company,
            "industry": ci.industry,
            "region": ci.region,
            "use_case": ci.use_case,
            "objectives": ci.objectives,
            "solution_overview": plan.solution_overview,
            "selected_skus": sel_skus,
            "architecture": [a.model_dump() for a in plan.architecture],
            "implementation_plan": plan.implementation_plan,
            "pricing_breakdown": json.loads(pr.model_dump_json()),
            "assumptions": mandatory_clauses(),
            "citations": plan.citations
        }

        # PREVIEW
        with preview_container:
            st.subheader("Preview (Markdown)")
            md = render_markdown(context)
            st.markdown(md)

            # Compliance check shown near preview
            hits = check_claims(md)
            if hits:
                st.error(f"Compliance check: found banned claims: {', '.join(hits)}")
            else:
                st.success("Compliance check passed.")

        # DOWNLOADS
        with download_container:
            st.subheader("Download")
            md_bytes = md.encode("utf-8")
            st.download_button("⬇️ Download Markdown", md_bytes,
                               file_name=f"proposal_{ci.company.replace(' ','_')}.md",
                               mime="text/markdown")

            docx_path = os.path.join("out", f"proposal_{ci.company.replace(' ','_')}.docx")
            save_docx_from_context(context, docx_path)
            with open(docx_path, "rb") as f:
                st.download_button("⬇️ Download DOCX", f,
                                   file_name=os.path.basename(docx_path),
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # Persist session
        saved = save_session({"customer": ci.model_dump(),
                              "plan": json.loads(plan.model_dump_json()),
                              "pricing": json.loads(pr.model_dump_json())})
        st.caption(f"Saved session to {saved}")

    except Exception as e:
        # Show the full stacktrace right in the UI so you can fix fast
        error_container.error("An error occurred while generating the draft.")
        error_container.exception(e)
else:
    with preview_container:
        st.info("Fill the form and click **Generate Draft Proposal** to see the preview here.")
