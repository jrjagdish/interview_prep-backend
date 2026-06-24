import os
import jwt
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import requests

load_dotenv()

router = APIRouter()
security = HTTPBearer()

# Get this from your Clerk Dashboard (API Keys section)
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

# Make sure the JWKS client initialization handles a live string
jwks_client = jwt.PyJWKClient(CLERK_JWKS_URL)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"cref {credentials}")
    try:
        # 1. Fetch the signing key automatically from Clerk's JWKS endpoint
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # 2. Decode and verify token authenticity
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_exp": True,   # Keep expiration check enabled
                "verify_aud": False,   # Bypass strict audience checks
                "verify_iss": False,   # Bypass strict issuer matching
            },
            leeway=60  # Accounts for any system time variations (clock skew)
        )
        
        return payload  
        
    except jwt.ExpiredSignatureError:
        print("❌ JWT Error: Token has expired!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except Exception as e:
        # 👇 ADD THIS LINE to see the exact error message in your FastAPI console terminal
        print(f"❌ JWT Verification Failed Because: {str(e)}") 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


# Protect any route like this:
@router.get("/api/users/sync")
async def secure_data(current_user: dict = Depends(get_current_user)):
    clerk_id = current_user.get("sub")
    
    headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
    clerk_response = requests.get(f"https://api.clerk.com/v1/users/{clerk_id}", headers=headers)
    if clerk_response.status_code != 200:
        print(f"❌ Clerk API Call failed: {clerk_response.status_code} - {clerk_response.text}")
        raise HTTPException(status_code=400,detail="failed to fetch data from clerk")
    
    user_data = clerk_response.json()

    # ❌ FIX: Swapped inner double quotes to single quotes to prevent breaking the f-string literal
    print(f"got user data: {user_data}")
    
    return {
        "message": "You are securely authenticated!",
        "clerk_user_id": clerk_id
    }