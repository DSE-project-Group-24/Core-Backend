# app/services/gov_rules_service.py
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

class GovRulesEngine:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._onehot = None
        self._tokens: List[str] = []
        self._load()

    @property
    def tokens(self) -> List[str]:
        return self._tokens

    def _load(self):
        if not self.csv_path.exists():
            raise FileNotFoundError(f"df_ARM.csv not found at {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        # If basket column exists: convert to one-hot (semicolon-separated tokens)
        if "basket" in df.columns:
            baskets = df["basket"].fillna("").astype(str)
            tokens = sorted({tok.strip() for row in baskets for tok in row.split(";") if tok.strip()})
            X = pd.DataFrame(0, index=range(len(baskets)), columns=tokens, dtype=int)
            for i, row in enumerate(baskets):
                for tok in row.split(";"):
                    t = tok.strip()
                    if t:
                        X.at[i, t] = 1
            self._onehot = X
        else:
            # Assume one-hot: keep only 0/1 numeric columns
            cand = df.select_dtypes(include=["number"]).copy()
            drop_cols = []
            for c in cand.columns:
                uniq = set(pd.unique(cand[c].dropna()))
                if not uniq.issubset({0, 1, 0.0, 1.0}):
                    drop_cols.append(c)
            cand.drop(columns=drop_cols, inplace=True)
            if cand.empty:
                raise ValueError("Could not infer item columns. Provide 0/1 one-hot columns or a 'basket' column.")
            self._onehot = cand.astype(int)

        self._tokens = sorted(self._onehot.columns.astype(str).tolist())

    def run_rules(
        self,
        *,
        target_consequents: List[str],
        min_support: float,
        min_confidence: float,
        max_len_antecedent: int,
        max_rules: int,
        antecedents_contains: List[str],
        consequents_contains: List[str],
        rhs_exact: bool,
        rhs_target: str | None,
        sort_by: str,
        sort_order: str,
    ) -> Dict[str, Any]:
        X = self._onehot.copy()

        # PRE: keep only rows that contain ALL chosen target consequents
        for tok in target_consequents:
            if tok not in X.columns:
                raise ValueError(f"Unknown token in target_consequents: {tok}")
            X = X[X[tok] == 1]

        N = len(X)
        if N == 0:
            return {"stats": {"pre_filtered_records": 0, "runtime_ms": 0}, "rules": []}

        # Frequent itemsets
        fis = apriori(X, min_support=min_support, use_colnames=True, max_len=None)
        if fis.empty:
            return {"stats": {"pre_filtered_records": int(N), "runtime_ms": 0}, "rules": []}

        # Association rules
        rules = association_rules(fis, metric="confidence", min_threshold=min_confidence)
        if rules.empty:
            return {"stats": {"pre_filtered_records": int(N), "runtime_ms": 0}, "rules": []}

        # Unpack for filtering and response
        rules["A"] = rules["antecedents"].apply(lambda s: sorted(list(s)))
        rules["C"] = rules["consequents"].apply(lambda s: sorted(list(s)))

        def contains_all(container: List[str], required: List[str]) -> bool:
            s = set(container)
            return all(r in s for r in required)

        # POST: contains filters
        if antecedents_contains:
            rules = rules[rules["A"].apply(lambda A: contains_all(A, antecedents_contains))]
        if consequents_contains:
            rules = rules[rules["C"].apply(lambda C: contains_all(C, consequents_contains))]

        # Optional: RHS exactly equals chosen target (e.g., Severity_S)
        if rhs_exact:
            if not rhs_target:
                raise ValueError("rhs_exact is true but rhs_target is missing")
            rules = rules[rules["C"].apply(lambda C: set(C) == {rhs_target})]
            # optional leakage guard: drop if Severity_* in antecedent
            rules = rules[~rules["A"].apply(lambda A: any(str(x).startswith("Severity_") for x in A))]

        # Sort & cap
        by = sort_by if sort_by in {"lift", "support", "confidence"} else "lift"
        ascending = (sort_order == "asc")
        rules = rules.sort_values(by=by, ascending=ascending).head(max_rules)

        out = [
            {
                "antecedents": row["A"],
                "consequents": row["C"],
                "support": float(row["support"]),
                "confidence": float(row["confidence"]),
                "lift": float(row["lift"]),
            }
            for _, row in rules.iterrows()
        ]
        return {
            "stats": {
                "pre_filtered_records": int(N),
                "min_support": min_support,
                "min_confidence": min_confidence,
                "runtime_ms": 0,
            },
            "rules": out,
        }