from fastapi import Depends, HTTPException, status
from app.db import get_supabase
from app.auth.dependencies import get_current_user

async def get_user_hospital_id(user: dict = Depends(get_current_user)):
    """
    Get hospital ID for the current authenticated user based on their role
    """
    supabase = get_supabase()
    user_id = user.get("sub")
    role = user.get("role")
    # print(f"User: {user}")
    # print(f"User ID: {user_id}, Role: {role}")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user authentication"
        )
    
    # Check user's role and get associated hospital
    table_name = None
    if role == "hospital_administrator":
        table_name = "Hospital_Administrator"
    elif role == "doctor":
        table_name = "Doctor"
    elif role == "nurse":
        table_name = "Nurse"
    else:
        # For roles without hospital association
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role '{role}' is not associated with any hospital"
        )
    # print(f"table_name: {table_name}")
    # Get hospital ID from appropriate table
    resp = supabase.table(table_name).select("hospital_id").eq("user_id", user_id).single().execute()
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hospital found for this {role}"
        )
    
    return resp.data.get("hospital_id")
