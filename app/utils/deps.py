# app/utils/deps.py (DEV ONLY — no auth yet)
def require_role(*_allowed_roles: str):
    def _dep():
        # No-op in dev. Replace with real check later.
        return None
    return _dep