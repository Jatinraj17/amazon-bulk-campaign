import re

# Constants
MAX_SKU_LENGTH = 40
SKU_PATTERN = r'^[a-zA-Z0-9_\-.,></":\;+=]+$'

def validate_sku(sku: str) -> bool:
    """Validate a single SKU"""
    if not sku or not sku.strip():
        return False
    if len(sku) > MAX_SKU_LENGTH:
        return False
    if not re.match(SKU_PATTERN, sku):
        return False
    return True

# Test cases
test_skus = [
    # Valid SKUs
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
    "ABC-123_DEF.456,GHI>789<JKL/MNO\"PQR:STU;VWX+YZ=",  # Complex combination
    "A" * 40,  # Maximum length
    
    # Invalid SKUs
    "",  # Empty
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

def run_tests():
    print("Running SKU validation tests...\n")
    
    # First 15 SKUs should be valid
    for sku in test_skus[:15]:
        result = validate_sku(sku)
        print(f"Testing valid SKU: {sku}")
        assert result is True, f"SKU should be valid: {sku}"
        print("✓ Passed\n")
    
    # Remaining SKUs should be invalid
    for sku in test_skus[15:]:
        result = validate_sku(sku)
        print(f"Testing invalid SKU: {sku}")
        assert result is False, f"SKU should be invalid: {sku}"
        print("✓ Passed\n")
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    run_tests()
