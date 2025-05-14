import pytest
from src.amazon_bulk_generator.core.validators import validate_skus

def test_sku_validation():
    # Test valid SKUs with special characters
    valid_skus = [
        ["ABC123"],  # Basic alphanumeric
        ["ABC-123"],  # With hyphen
        ["ABC_123"],  # With underscore
        ["ABC.123"],  # With dot
        ["ABC,123"],  # With comma
        ["ABC>123"],  # With greater than
        ["ABC<123"],  # With less than
        ["ABC/123"],  # With forward slash
        ["ABC\"123"],  # With double quote
        ["ABC:123"],  # With colon
        ["ABC;123"],  # With semicolon
        ["ABC+123"],  # With plus
        ["ABC=123"],  # With equals
        ["ABC-123_DEF.456,GHI>789<JKL/MNO\"PQR:STU;VWX+YZ="],  # Complex combination
        ["A" * 40],  # Maximum length
    ]
    
    for skus in valid_skus:
        result = validate_skus(skus)
        assert result[0] is True, f"SKU validation failed for {skus}"

    # Test invalid SKUs
    invalid_skus = [
        [],  # Empty list
        [""],  # Empty SKU
        ["A" * 41],  # Exceeds max length
        ["ABC#123"],  # Invalid special character #
        ["ABC@123"],  # Invalid special character @
        ["ABC!123"],  # Invalid special character !
        ["ABC$123"],  # Invalid special character $
        ["ABC%123"],  # Invalid special character %
        ["ABC^123"],  # Invalid special character ^
        ["ABC&123"],  # Invalid special character &
        ["ABC*123"],  # Invalid special character *
        ["ABC(123"],  # Invalid special character (
    ]
    
    for skus in invalid_skus:
        result = validate_skus(skus)
        assert result[0] is False, f"SKU validation should fail for {skus}"

if __name__ == "__main__":
    pytest.main([__file__])
