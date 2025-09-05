from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# ---- Safe coercion helpers ----
TRUE_SET  = {"true", "t", "yes", "y", "1"}
FALSE_SET = {"false", "f", "no", "n", "0"}

def _coerce_bool_series(s: pd.Series) -> pd.Series | None:
    if pd.api.types.is_bool_dtype(s):
        return s.astype("boolean")
    if pd.api.types.is_numeric_dtype(s):
        uniq = set(pd.unique(s.dropna()))
        if uniq.issubset({0, 1, 0.0, 1.0}):
            return s.fillna(0).astype("Int8").astype("boolean")
        return None
    if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
        def to_bool(x):
            if pd.isna(x): return pd.NA
            v = str(x).strip().lower()
            if v in TRUE_SET: return True
            if v in FALSE_SET: return False
            return pd.NA
        coerced = s.map(to_bool)
        uniq = set(pd.unique(coerced.dropna()))
        if uniq.issubset({True, False}):
            return coerced.fillna(False).astype("boolean")
        return None
    return None

def _to_onehot_from_basket(df: pd.DataFrame, basket_col: str = "basket") -> pd.DataFrame:
    baskets = df[basket_col].fillna("").astype(str)
    tokens = sorted({tok.strip() for row in baskets for tok in row.split(";") if tok.strip()})
    X = pd.DataFrame(0, index=range(len(baskets)), columns=tokens, dtype="Int8")
    for i, row in enumerate(baskets):
        for tok in row.split(";"):
            t = tok.strip()
            if t:
                X.iat[i, X.columns.get_loc(t)] = 1
    return X

class GovRulesEngine:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._onehot: pd.DataFrame | None = None
        self._tokens: List[str] = []
        self._load()

    @property
    def tokens(self) -> List[str]:
        return self._tokens

    def _load(self):
        if not self.csv_path.exists():
            raise FileNotFoundError(f"df_ARM.csv not found at {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        if "basket" in df.columns:
            X = _to_onehot_from_basket(df, "basket")
        else:
            candidates: dict[str, pd.Series] = {}
            for col in df.columns:
                b = _coerce_bool_series(df[col])
                if b is not None:
                    candidates[col] = b
            if not candidates:
                raise ValueError(
                    "Could not infer item columns. Provide a 'basket' column or item columns as 0/1/True/False."
                )
            X = pd.DataFrame({k: v.fillna(False).astype(int) for k, v in candidates.items()})
            zero_cols = [c for c in X.columns if X[c].sum() == 0]
            if zero_cols:
                X = X.drop(columns=zero_cols)
            if X.empty:
                raise ValueError("After conversion, all item columns were empty or zero-only.")

        self._onehot = X.astype("Int8")
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

        # PRE: require all selected target consequents
        for tok in target_consequents:
            if tok not in X.columns:
                raise ValueError(f"Unknown token in target_consequents: {tok}")
            X = X[X[tok] == 1]

        N = len(X)
        if N == 0:
            return {"stats": {"pre_filtered_records": 0, "runtime_ms": 0}, "rules": []}

        # Frequent itemsets (max_len optional; you can honor max_len_antecedent here if desired)
        fis = apriori(X, min_support=min_support, use_colnames=True)
        if fis.empty:
            return {"stats": {"pre_filtered_records": int(N), "runtime_ms": 0}, "rules": []}

        rules = association_rules(fis, metric="confidence", min_threshold=min_confidence)
        if rules.empty:
            return {"stats": {"pre_filtered_records": int(N), "runtime_ms": 0}, "rules": []}

        rules["A"] = rules["antecedents"].apply(lambda s: sorted(list(s)))
        rules["C"] = rules["consequents"].apply(lambda s: sorted(list(s)))

        # --- add near the top of the file (below imports) ---
        def _has_unknown(items) -> bool:
            # returns True if any token contains "unknown" (case-insensitive)
            return any("unknown" in str(x).lower() for x in items)

      
        # NEW: drop any rule that has "unknown" in A or C (case-insensitive)
        rules = rules[~rules["A"].apply(_has_unknown)]
        rules = rules[~rules["C"].apply(_has_unknown)]
        def contains_all(container: List[str], required: List[str]) -> bool:
            s = set(container)
            return all(r in s for r in required)

        # POST filters
        if antecedents_contains:
            rules = rules[rules["A"].apply(lambda A: contains_all(A, antecedents_contains))]
        if consequents_contains:
            rules = rules[rules["C"].apply(lambda C: contains_all(C, consequents_contains))]

        # RHS exact (predictive rule)
        if rhs_exact:
            if not rhs_target:
                raise ValueError("rhs_exact is true but rhs_target is missing")
            rules = rules[rules["C"].apply(lambda C: set(C) == {rhs_target})]
            rules = rules[~rules["A"].apply(lambda A: any(str(x).startswith("Severity_") for x in A))]

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