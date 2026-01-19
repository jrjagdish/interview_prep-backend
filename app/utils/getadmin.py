from fastapi import Depends, HTTPException, status
from app.services.authService import get_current_user

def admin_only(current_user=Depends(get_current_user)):
    print(f"user role:{current_user.role} ,email: {current_user.email}")
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
