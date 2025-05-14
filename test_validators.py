from src.amazon_bulk_generator.core.validators import validate_skus

def test_sku_validation():
    print("\nTesting valid SKUs:")
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
    ]
    
    for skus in valid_skus:
        result = validate_skus(skus)
        print(f"\nTesting SKUs: {skus}")
        print(f"Result: {'✓ Valid' if result[0] else f'✗ Invalid - {result[1]}'}")
        
    print("\nTesting complex SKU:")
    complex_sku = ["ABC-123_DEF.456,GHI>789<JKL/MNO\"PQR:STU;VWX+YZ"]
    result = validate_skus(complex_sku)
    print(f"Complex SKU result: {'✓ Valid' if result[0] else f'✗ Invalid - {result[1]}'}")
    
    print("\nTesting invalid SKUs:")
    invalid_skus = [
        [],  # Empty list
        [""],  # Empty SKU
        ["A" * 41],  # Exceeds max length
        ["ABC#123"],  # Invalid special character #
        ["ABC@123"],  # Invalid special character @
        ["ABC!123"],  # Invalid special character !
    ]
    
    for skus in invalid_skus:
        result = validate_skus(skus)
        print(f"\nTesting SKUs: {skus}")
        print(f"Result: {'✗ Should be invalid' if result[0] else '✓ Correctly invalid'} - {result[1]}")

if __name__ == "__main__":
    test_sku_validation()
