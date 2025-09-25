import os, json
from typing import List
from schemas import PricingBreakdown, PricingItemResult
from catalog import load_catalog, get_sku
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_pricing_rules():
    path = os.path.join(DATA_DIR, "pricing.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compute_pricing(items: List[dict], currency: str = "INR", discount_pct: float = 0.0) -> PricingBreakdown:
    rules = load_pricing_rules()
    df = load_catalog()
    out = PricingBreakdown(currency=currency, items=[])
    # clamp discount within rules
    max_disc = rules.get("max_discount_pct", 20.0)
    if discount_pct > max_disc:
        discount_pct = max_disc
    if discount_pct < 0: discount_pct = 0.0

    for it in items:
        sk = get_sku(df, it["sku"])
        if not sk: 
            continue
        qty = int(it.get("qty",1))
        unit_price = float(sk.get("price", 0.0))
        subtotal = unit_price * qty
        out.items.append(PricingItemResult(sku=sk["sku"], name=sk["name"], unit_price=unit_price, qty=qty, subtotal=subtotal))

    out.subtotal = sum(i.subtotal for i in out.items)
    out.discount_pct = discount_pct
    out.discount_amount = out.subtotal * (discount_pct/100.0)
    taxable = out.subtotal - out.discount_amount
    out.tax_pct = rules.get("tax_pct", 18.0)
    out.tax_amount = taxable * (out.tax_pct/100.0)
    out.total = taxable + out.tax_amount
    return out
