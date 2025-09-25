import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_catalog():
    path = os.path.join(DATA_DIR, "products.csv")
    df = pd.read_csv(path)
    # normalize text columns for safety
    for col in ["sku","name","features","benefits","category","regions","prereqs"]:
        if col in df.columns:
            df[col] = df[col].fillna("")
    return df

def get_sku(df: pd.DataFrame, sku: str):
    row = df[df["sku"]==sku]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

def shortlist_by_requirements(df: pd.DataFrame, must_have_features, region="IN", budget_max=None):
    # simple filter: feature keywords & region availability
    def has_features(text):
        t = (text or "").lower()
        return all(feat.lower() in t for feat in must_have_features) if must_have_features else True
    def in_region(text):
        t = (text or "").lower()
        return (region.lower() in t) or (t.strip()=="" )

    m = df[df["features"].apply(has_features) & df["regions"].apply(in_region)]
    # if budget provided, filter with unit_price <= budget_max (rough)
    if budget_max is not None and "price" in m.columns:
        m = m[m["price"] <= float(budget_max)]
    return m

