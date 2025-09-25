import os
from typing import Dict, Any, List
from schemas import ProposalPlan, SKUSelection, ArchitectureItem, ROI

def mock_plan(customer: Dict[str, Any], objectives: List[str], shortlisted_skus: List[Dict[str,Any]], top_snippets: List[Dict[str,str]]) -> ProposalPlan:
    # Simple heuristic selection: pick up to 3 SKUs
    picks = []
    for r in shortlisted_skus[:3]:
        picks.append(SKUSelection(sku=r['sku'], reason=f"Matches features for {customer.get('use_case','')}", must_have=True))

    overview = f"""This proposal outlines a tailored solution for {customer.get('company')} in the {customer.get('industry')} industry.
It addresses goals such as {', '.join(objectives[:3]) if objectives else 'the stated business objectives'} using our proven components.
The approach emphasizes quick time-to-value, scalability, and measurable ROI within {customer.get('timeline_weeks',8)} weeks."""

    arch = [ArchitectureItem(component="Web/App", role="Integration SDK"),
            ArchitectureItem(component="Backend", role="Core APIs & Orchestration"),
            ArchitectureItem(component="Analytics", role="Dashboards & Reporting")]

    plan = [
        {"phase":"Discovery", "weeks":1},
        {"phase":"Integration", "weeks":3},
        {"phase":"UAT & Training", "weeks":2},
        {"phase":"Go-live", "weeks":1}
    ]

    citations = [s['id'] for s in top_snippets]

    return ProposalPlan(
        customer=customer,
        objectives=objectives,
        selected_skus=picks,
        solution_overview=overview,
        architecture=arch,
        implementation_plan=plan,
        pricing={"currency":"INR","items":[{"sku":p.sku,"qty":1} for p in picks]},
        risks_mitigations=[{"risk":"Data quality issues","mitigation":"Pre-launch validation jobs"},
                           {"risk":"Integration delays","mitigation":"Early sandbox access & weekly checkpoints"}],
        roi_summary=ROI(period_months=12, benefits=["+2-5% conversion lift","-10% churn","Faster onboarding"]),
        citations=citations
    )

# Optional: Wire in OpenAI (if user sets OPENAI_API_KEY). For MVP we keep mock plan to stay offline.
