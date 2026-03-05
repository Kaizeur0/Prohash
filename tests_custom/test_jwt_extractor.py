import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.jwt_extractor import JWTExtractor

def test_valid_jwt():
    extractor = JWTExtractor()
    # Header: {"alg":"HS256","typ":"JWT"} -> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    # Payload: {"sub":"1234567890"} -> eyJzdWIiOiIxMjM0NTY3ODkwIn0
    # Signature: dummy
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dummy_signature"
    
    result = extractor.extract(token)
    assert result is not None
    assert result['header']['alg'] == "HS256"
    assert result['payload']['sub'] == "1234567890"
    assert result['token'] == token

def test_invalid_jwt():
    extractor = JWTExtractor()
    
    # Not enough parts
    assert extractor.extract("eyJhbGciOi.JIUzI1NiIsIn") is None
    
    # Invalid base64
    assert extractor.extract("invalid.invalid.invalid") is None
