from pipeline.preprocessing.denoise import denoise_image
from pipeline.preprocessing.deskew import deskew_image
from pipeline.preprocessing.quality_check import check_image_quality
from pipeline.classification.document_type import classify_document
from pipeline.classification.language_detect import detect_language


# -----------------------------
# Test image
# -----------------------------

input_path = "uploads/133826299539863636.jpg"


# -----------------------------
# Test Denoising
# -----------------------------

denoised_path = "processed/test_denoised.jpg"

denoise_image(input_path, denoised_path)

print("DENOISE: PASS")
print("Saved:", denoised_path)


# -----------------------------
# Test Deskew
# -----------------------------

deskewed_path = "processed/test_deskewed.jpg"

deskew_image(input_path, deskewed_path)

print("DESKEW: PASS")
print("Saved:", deskewed_path)


# -----------------------------
# Test Quality Check
# -----------------------------

quality_result = check_image_quality(input_path)

print("QUALITY CHECK: PASS")
print(quality_result)


# -----------------------------
# Test Document Classification
# -----------------------------

sample_text = """
Survey Number 123/4
Owner Name: Ravi Kumar
Village: Bannerghatta
Land Plot
"""

document_result = classify_document(sample_text)

print("DOCUMENT TYPE: PASS")
print(document_result)


# -----------------------------
# Test Language Detection
# -----------------------------

language_result = detect_language(
    "This is a land record document"
)

print("LANGUAGE DETECTION: PASS")
print(language_result)


print("\nALL TESTS COMPLETED")