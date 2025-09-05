# app/routers/gov.py
from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from app.models.gov_rules import RunRequest
from app.services.gov_rules_service import GovRulesEngine
from app.utils.role_check import require_role  # <-- your existing role dependency

router = APIRouter(prefix="/gov/rules", tags=["gov-rules"])

# Lazily init a singleton engine (adjust path as needed)
ENGINE: GovRulesEngine | None = None

def get_engine() -> GovRulesEngine:
    global ENGINE
    if ENGINE is None:
        csv_path = Path(__file__).resolve().parent.parent / "data" / "df_ARM.csv"
        ENGINE = GovRulesEngine(csv_path)
    return ENGINE

@router.get("/bootstrap")
def bootstrap(_: None = Depends(require_role("government"))):
    eng = get_engine()
    return {
        "tokens": eng.tokens,
        "defaults": {"min_support": 0.02, "min_confidence": 0.3},
    }

@router.post("/run")
def run(req: RunRequest, _: None = Depends(require_role("government"))):
    eng = get_engine()
    try:
        result = eng.run_rules(
            target_consequents=req.pre.target_consequents,
            min_support=req.pre.min_support,
            min_confidence=req.pre.min_confidence,
            max_len_antecedent=req.pre.max_len_antecedent,
            max_rules=req.pre.max_rules,
            antecedents_contains=req.post.antecedents_contains,
            consequents_contains=req.post.consequents_contains,
            rhs_exact=req.post.rhs_exact,
            rhs_target=req.post.rhs_target,
            sort_by=str(req.sort.get("by", "lift")),
            sort_order=str(req.sort.get("order", "desc")),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))