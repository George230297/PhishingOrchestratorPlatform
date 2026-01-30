from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_captured_credential(password: str) -> str:
    """
    Applies secure hashing (bcrypt) to the provided password.
    Returns the hash string.
    
    CRITICAL: This function must be the ONLY way to process captured credentials.
    NEVER store or return the password in plain text.
    """
    if not password:
        return ""
    
    # Apply bcrypt hashing
    return pwd_context.hash(password)
