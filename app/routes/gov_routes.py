# app/routers/gov.py
from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from app.models.gov_rules import RunRequest
from app.services.gov_rules_service import GovRulesEngine
from app.auth.dependencies import government_personnel_required 

router = APIRouter()


ENGINE: GovRulesEngine | None = None

def get_engine() -> GovRulesEngine:
    global ENGINE
    if ENGINE is None:
        csv_path = Path(__file__).resolve().parent.parent / "data" / "df_ARM.csv"
        ENGINE = GovRulesEngine(csv_path)
    return ENGINE

@router.get("/bootstrap")
def bootstrap():
    eng = get_engine()
    clean_tokens = [t for t in eng.tokens if "unknown" not in t.lower()]
    return {"tokens": clean_tokens, "defaults": {"min_support": 0.05, "min_confidence": 0.3}}
    

@router.post("/run", dependencies=[Depends(government_personnel_required)])
def run(req: RunRequest):
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
    


