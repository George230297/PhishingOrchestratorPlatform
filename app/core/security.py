from passlib.context import CryptContext

# Switch to argon2 which is more modern and less fussy about versions/lengths than legacy bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_captured_credential(password: str) -> str:
    """
    Applies secure hashing (argon2) to the provided password.
    Returns the hash string.
    
    CRITICAL: This function must be the ONLY way to process captured credentials.
    NEVER store or return the password in plain text.
    """
    if not password:
        return ""
    
    return pwd_context.hash(password)
