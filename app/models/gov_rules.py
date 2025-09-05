from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PreFilters(BaseModel):
    target_consequents: List[str] = []
    min_support: float = 0.02
    min_confidence: float = 0.3
    max_len_antecedent: int = 4
    max_rules: int = 1000

class PostFilters(BaseModel):
    antecedents_contains: List[str] = []
    consequents_contains: List[str] = []
    rhs_exact: bool = False
    rhs_target: Optional[str] = None

class RunRequest(BaseModel):
    pre: PreFilters
    post: PostFilters
    sort: Dict[str, Any] = {"by": "lift", "order": "desc"}