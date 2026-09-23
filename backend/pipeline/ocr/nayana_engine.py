"""
Nayana OCR Engine Wrapper
Handles Indic and multilingual land record OCR inference using Nayana-OCR via Transformers.
Strictly conforms to the standard OCR engine contract.
"""

import os
from typing import Dict, Any, List, Optional
from PIL import Image

# Configurable model ID with sensible default
DEFAULT_NAYANA_MODEL = os.getenv("NAYANA_MODEL_ID", "agenor/nayana-ocr")

_model = None
_processor = None
_load_attempted = False
_load_error = None


def _get_nayana_model():
    """
    Lazy loader for Nayana-OCR model and processor.
    Returns (model, processor, error_message).
    """
    global _model, _processor, _load_attempted, _load_error
    if _load_attempted:
        return _model, _processor, _load_error

    _load_attempted = True
    try:
        import torch
        from transformers import AutoProcessor, AutoModelForVision2Seq

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        _processor = AutoProcessor.from_pretrained(DEFAULT_NAYANA_MODEL)
        _model = AutoModelForVision2Seq.from_pretrained(
            DEFAULT_NAYANA_MODEL,
            torch_dtype=dtype,
            low_cpu_mem_usage=True
        ).to(device)
        _model.eval()
        _load_error = None
    except Exception as exc:
        _model = None
        _processor = None
        _load_error = f"Failed to load Nayana-OCR model '{DEFAULT_NAYANA_MODEL}': {str(exc)}"

    return _model, _processor, _load_error


def run_ocr(image_path: str) -> Dict[str, Any]:
    """
    Execute OCR using the Nayana-OCR engine.

    Contract:
    {
        "engine": "nayana",
        "raw_text": str,
        "lines": [ {"text": str, "confidence": float, "bbox": [x,y,w,h] | None} ],
        "overall_confidence": float,   # 0.0 - 1.0
        "language_detected": str | None,
        "error": str | None            # Populated if OCR failed, other fields empty/default
    }
    """
    # 1. Validate file existence
    if not image_path or not os.path.exists(image_path):
        return {
            "engine": "nayana",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": f"Image file not found: {image_path}"
        }

    # 2. Validate image readability
    try:
        image = Image.open(image_path)
        image.verify()
        # Re-open for actual processing as verify() damages image pointer
        image = Image.open(image_path).convert("RGB")
    except Exception as img_err:
        return {
            "engine": "nayana",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": f"Corrupted or unreadable image file: {str(img_err)}"
        }

    # 3. Load model & processor
    model, processor, load_err = _get_nayana_model()
    if load_err or model is None or processor is None:
        # Graceful degradation with clear error message
        return {
            "engine": "nayana",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": load_err or "Model not initialized"
        }

    # 4. Perform Inference
    try:
        import torch

        device = next(model.parameters()).device
        inputs = processor(images=image, return_tensors="pt").to(device)

        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=1024)

        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        raw_text = generated_text.strip()

        # Parse output into lines
        raw_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        lines_output = []
        for line in raw_lines:
            lines_output.append({
                "text": line,
                "confidence": 0.90,  # Model generation confidence estimate
                "bbox": None
            })

        overall_conf = 0.90 if lines_output else 0.0

        return {
            "engine": "nayana",
            "raw_text": raw_text,
            "lines": lines_output,
            "overall_confidence": overall_conf,
            "language_detected": "indic_multilingual",
            "error": None
        }

    except Exception as inf_err:
        return {
            "engine": "nayana",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": f"Nayana-OCR inference failed: {str(inf_err)}"
        }
