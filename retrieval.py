import os, glob
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KB_DIR = os.path.join(os.path.dirname(__file__), "kb")

class MiniRetriever:
    def __init__(self, product_df):
        self.docs = []
        self.ids = []
        # Build docs from products
        for _, r in product_df.iterrows():
            doc = f"SKU: {r['sku']}\nName: {r['name']}\nFeatures: {r['features']}\nBenefits: {r['benefits']}\nCategory: {r['category']}\nPrereqs: {r['prereqs']}"
            self.docs.append(doc)
            self.ids.append(f"products.csv#{r['sku']}")
        # Build docs from KB markdown files
        for p in glob.glob(os.path.join(KB_DIR, "*.md")):
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
            self.docs.append(txt)
            self.ids.append(os.path.relpath(p, os.path.dirname(__file__)))
        # Fit TF-IDF
        self.vect = TfidfVectorizer(stop_words='english')
        self.X = self.vect.fit_transform(self.docs)

    def search(self, query: str, k: int = 5) -> List[Tuple[str,str]]:
        if not query.strip():
            return []
        q = self.vect.transform([query])
        sims = cosine_similarity(q, self.X).ravel()
        idx = sims.argsort()[::-1][:k]
        return [(self.docs[i], self.ids[i]) for i in idx]
