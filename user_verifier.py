import jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header

load_dotenv()

SUPABASE_REF = os.getenv("SUPABASE_REF")
JWKS_URL = f"https://{SUPABASE_REF}.supabase.co/auth/v1/.well-known/jwks.json"

jwk_client = jwt.PyJWKClient(JWKS_URL)

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ")

    try:
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    
    return payload["sub"]  # this is the user's id (uuid), matching auth.users.id