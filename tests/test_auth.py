import pytest
from src.services.auth import hash_password, verify_password

def test_password_hashing():
    password = "secure_password123"
    hashed = hash_password(password)
    
    # Hashed password should not equal plaintext
    assert hashed != password
    
    # Verification should succeed with correct password
    assert verify_password(password, hashed) is True
    
    # Verification should fail with incorrect password
    assert verify_password("wrong_password", hashed) is False
