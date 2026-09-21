from pipeline.preprocessing.denoise import denoise_image
from pipeline.preprocessing.deskew import deskew_image
from pipeline.preprocessing.quality_check import check_image_quality
from pipeline.classification.document_type import classify_document
from pipeline.classification.language_detect import detect_language

import os


def process_document(input_path, processed_dir):

    # -----------------------------
    # Get original filename
    # -----------------------------

    original_filename = os.path.basename(input_path)

    filename_without_extension = os.path.splitext(
        original_filename
    )[0]

    # -----------------------------
    # 1. Quality Check
    # -----------------------------

    quality_result = check_image_quality(input_path)

    # -----------------------------
    # 2. Denoising
    # -----------------------------

    denoised_path = os.path.join(
        processed_dir,
        f"{filename_without_extension}_denoised.jpg"
    )

    denoise_image(
        input_path,
        denoised_path
    )

    # -----------------------------
    # 3. Deskewing
    # -----------------------------

    deskewed_path = os.path.join(
        processed_dir,
        f"{filename_without_extension}_deskewed.jpg"
    )

    deskew_image(
        denoised_path,
        deskewed_path
    )

    # -----------------------------
    # 4. Document Classification
    # -----------------------------

    sample_text = """
    Survey Number
    Land
    Owner
    Village
    """

    document_result = classify_document(
        sample_text
    )

    # -----------------------------
    # 5. Language Detection
    # -----------------------------

    language_result = detect_language(
        sample_text
    )

    # -----------------------------
    # Final Result
    # -----------------------------

    return {
        "quality": quality_result,
        "denoised_file": denoised_path,
        "deskewed_file": deskewed_path,
        "document_type": document_result,
        "language": language_result
    }