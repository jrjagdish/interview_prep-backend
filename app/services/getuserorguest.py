from fastapi import Depends, HTTPException, Request
from app.services.authService import get_current_user,get_current_guest
from app.db.session import get_db

async def get_user_or_guest(request: Request, db=Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(401, "Authorization header missing")

    token_type, token = auth_header.split(" ")
    if token_type.lower() != "bearer":
        raise HTTPException(401, "Invalid token type")

    try:
        # Try user token first
        return await get_current_user(token=token, db=db)
    except HTTPException as e_user:
        # If fails, try guest token
        try:
            return await get_current_guest(token=token)
        except HTTPException:
            # Both failed
            raise HTTPException(401, "Invalid token for user or guest")
