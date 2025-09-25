from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CustomerInput(BaseModel):
    company: str
    industry: str
    region: str = "IN"
    use_case: str
    objectives: List[str] = []
    timeline_weeks: int = 8
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    discovery_notes: Optional[str] = None

class SKUSelection(BaseModel):
    sku: str
    reason: str = ""
    must_have: bool = True

class ArchitectureItem(BaseModel):
    component: str
    role: str

class PlanPricingItem(BaseModel):
    sku: str
    qty: int = 1

class ROI(BaseModel):
    period_months: int = 12
    benefits: List[str] = []

class ProposalPlan(BaseModel):
    customer: Dict[str, Any]
    objectives: List[str]
    selected_skus: List[SKUSelection] = []
    solution_overview: str
    architecture: List[ArchitectureItem] = []
    implementation_plan: List[Dict[str, Any]] = []
    pricing: Dict[str, Any] = {"currency":"INR","items":[]}
    risks_mitigations: List[Dict[str, str]] = []
    roi_summary: ROI = ROI()
    citations: List[str] = []
    needs_clarification: Optional[List[str]] = None

class PricingItemResult(BaseModel):
    sku: str
    name: str
    unit_price: float
    qty: int
    subtotal: float

class PricingBreakdown(BaseModel):
    currency: str = "INR"
    items: List[PricingItemResult] = []
    discount_pct: float = 0.0
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_pct: float = 18.0
    tax_amount: float = 0.0
    total: float = 0.0
