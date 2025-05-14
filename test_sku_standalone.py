import re

def validate_sku(sku: str) -> tuple[bool, str | None]:
    """Validate a single SKU"""
    # Constants
    MAX_SKU_LENGTH = 40
    SKU_PATTERN = r'^[a-zA-Z0-9_\-.,></":\;+=]+$'
    
    print(f"\nValidating SKU: {sku}")
    
    # Check empty
    if not sku or not sku.strip():
        msg = "Empty SKU is not allowed"
        print(f"Failed: {msg}")
        return False, msg
        
    # Check length
    if len(sku) > MAX_SKU_LENGTH:
        msg = f"SKU length {len(sku)} exceeds max length {MAX_SKU_LENGTH}"
        print(f"Failed: {msg}")
        return False, msg
        
    # Check pattern
    match = re.match(SKU_PATTERN, sku)
    if not match:
        msg = f"SKU contains invalid characters"
        print(f"Failed: {msg}")
        return False, msg
        
    print("Passed validation")
    return True, None

def run_tests():
    print("Running SKU validation tests...")
    
    # Test valid SKUs
    valid_skus = [
        "ABC123",  # Basic alphanumeric
        "ABC-123",  # With hyphen
        "ABC_123",  # With underscore
        "ABC.123",  # With dot
        "ABC,123",  # With comma
        "ABC>123",  # With greater than
        "ABC<123",  # With less than
        "ABC/123",  # With forward slash
        'ABC"123',  # With double quote
        "ABC:123",  # With colon
        "ABC;123",  # With semicolon
        "ABC+123",  # With plus
        "ABC=123",  # With equals
        "ABC-123_DEF.456,GHI>789<JKL/MNO\"PQR:STU;VWX+YZ",  # Complex combination
    ]
    
    print("\n=== Testing Valid SKUs ===")
    for sku in valid_skus:
        result, error = validate_sku(sku)
        assert result is True, f"SKU should be valid: {sku}. Error: {error}"
        print(f"✓ Valid SKU test passed: {sku}")
    
    # Test invalid SKUs
    invalid_skus = [
        "",  # Empty
        " ",  # Whitespace only
        "A" * 41,  # Too long
        "ABC#123",  # Invalid special character #
        "ABC@123",  # Invalid special character @
        "ABC!123",  # Invalid special character !
        "ABC$123",  # Invalid special character $
        "ABC%123",  # Invalid special character %
        "ABC^123",  # Invalid special character ^
        "ABC&123",  # Invalid special character &
        "ABC*123",  # Invalid special character *
        "ABC(123",  # Invalid special character (
    ]
    
    print("\n=== Testing Invalid SKUs ===")
    for sku in invalid_skus:
        result, error = validate_sku(sku)
        assert result is False, f"SKU should be invalid: {sku}"
        print(f"✓ Invalid SKU test passed: {sku} (Expected error: {error})")
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
