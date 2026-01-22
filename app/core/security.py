import hashlib

def hash_captured_credential(password: str) -> str:
    """
    Applies SHA-256 hashing to the provided password.
    Returns the hexadecimal digest of the hash.
    
    CRITICAL: This function must be the ONLY way to process captured credentials.
    NEVER store or return the password in plain text.
    """
    if not password:
        return ""
    
    # Encode the string to bytes, apply sha256, and return hex digest
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
