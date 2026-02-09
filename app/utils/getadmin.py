from fastapi import Depends, HTTPException, status
from app.services.authService import get_current_user
from app.models.users import User

def admin_only(current_user: User = Depends(get_current_user)):
    """
    Restricts access to users with the 'admin' role.
    Impact: Ensures that sensitive B2B guest management routes 
    cannot be accessed by standard candidates or unauthorized users.
    """
    # 1. Check for Active Status first
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    # 2. Role Verification
    # Using lowercase check to prevent string-matching bugs
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required."
        )
    
    return current_user