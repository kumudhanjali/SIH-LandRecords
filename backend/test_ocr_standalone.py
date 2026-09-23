"""
Section 1 Standalone Test: OCR Engine Contract Validation
Tests nayana_engine.py and qwen_engine.py on:
1. Valid sample deskewed image (or generated sample)
2. Non-existent file (error handling)
3. Corrupted image file (error handling)
Validates that output dictionary keys, types, and contract match 100%.
"""

import os
import sys
from PIL import Image

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.ocr import nayana_engine, qwen_engine

EXPECTED_KEYS = {"engine", "raw_text", "lines", "overall_confidence", "language_detected", "error"}


def validate_contract(result: dict, expected_engine: str) -> bool:
    assert isinstance(result, dict), f"Result must be a dict, got {type(result)}"
    assert set(result.keys()) == EXPECTED_KEYS, f"Keys mismatch: {set(result.keys())} vs {EXPECTED_KEYS}"
    assert result["engine"] == expected_engine, f"Engine mismatch: {result['engine']} != {expected_engine}"
    assert isinstance(result["raw_text"], str), f"raw_text must be str"
    assert isinstance(result["lines"], list), f"lines must be list"
    assert isinstance(result["overall_confidence"], (int, float)), f"overall_confidence must be float"
    assert 0.0 <= result["overall_confidence"] <= 1.0, f"overall_confidence {result['overall_confidence']} out of range [0, 1]"
    assert result["language_detected"] is None or isinstance(result["language_detected"], str)
    assert result["error"] is None or isinstance(result["error"], str)
    return True


def run_tests():
    print("==================================================")
    print("  SECTION 1: OCR ENGINE CONTRACT TEST")
    print("==================================================")

    # Prepare fixtures
    sample_img_path = os.path.join(os.path.dirname(__file__), "processed", "test_deskewed.jpg")
    if not os.path.exists(sample_img_path):
        os.makedirs(os.path.dirname(sample_img_path), exist_ok=True)
        img = Image.new("RGB", (200, 100), color=(255, 255, 255))
        img.save(sample_img_path)

    corrupt_img_path = os.path.join(os.path.dirname(__file__), "processed", "corrupt_sample.jpg")
    with open(corrupt_img_path, "wb") as f:
        f.write(b"NOT_A_VALID_IMAGE_BYTES_12345")

    missing_path = "non_existent_image_path_404.jpg"

    engines = [
        ("nayana", nayana_engine),
        ("qwen", qwen_engine),
    ]

    for name, module in engines:
        print(f"\nTesting engine wrapper: {name}")

        # Test 1: Sample image
        res_sample = module.run_ocr(sample_img_path)
        validate_contract(res_sample, name)
        print(f"  [PASS] Valid image call returned contract-compliant dict. (error: {res_sample['error']})")

        # Test 2: Missing file
        res_missing = module.run_ocr(missing_path)
        validate_contract(res_missing, name)
        assert res_missing["error"] is not None, "Missing file should set error field"
        print(f"  [PASS] Missing file handled gracefully: '{res_missing['error']}'")

        # Test 3: Corrupt file
        res_corrupt = module.run_ocr(corrupt_img_path)
        validate_contract(res_corrupt, name)
        assert res_corrupt["error"] is not None, "Corrupt file should set error field"
        print(f"  [PASS] Corrupted file handled gracefully: '{res_corrupt['error']}'")

    # Clean up temp corrupt file
    if os.path.exists(corrupt_img_path):
        os.remove(corrupt_img_path)

    print("\n==================================================")
    print("  SECTION 1 TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
