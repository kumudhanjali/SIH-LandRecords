"""
Qwen2.5-VL OCR Engine Wrapper
Handles Vision-Language OCR inference for land records using Qwen2.5-VL via Transformers.
Strictly conforms to the standard OCR engine contract.
"""

import os
from typing import Dict, Any, List, Optional
from PIL import Image

# Configurable model ID (3B variant default for balanced local dev speed & memory)
DEFAULT_QWEN_MODEL = os.getenv("QWEN_MODEL_ID", "Qwen/Qwen2.5-VL-3B-Instruct")

_model = None
_processor = None
_load_attempted = False
_load_error = None


def _get_qwen_model():
    """
    Lazy loader for Qwen2.5-VL model and processor.
    Returns (model, processor, error_message).
    """
    global _model, _processor, _load_attempted, _load_error
    if _load_attempted:
        return _model, _processor, _load_error

    _load_attempted = True
    try:
        import torch
        from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float32

        _processor = AutoProcessor.from_pretrained(DEFAULT_QWEN_MODEL)
        _model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            DEFAULT_QWEN_MODEL,
            torch_dtype=dtype,
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True
        )
        if not torch.cuda.is_available():
            _model.to(device)
        _model.eval()
        _load_error = None
    except Exception as exc:
        _model = None
        _processor = None
        _load_error = f"Failed to load Qwen2.5-VL model '{DEFAULT_QWEN_MODEL}': {str(exc)}"

    return _model, _processor, _load_error


def run_ocr(image_path: str) -> Dict[str, Any]:
    """
    Execute OCR using the Qwen2.5-VL engine.

    Contract:
    {
        "engine": "qwen",
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
            "engine": "qwen",
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
            "engine": "qwen",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": f"Corrupted or unreadable image file: {str(img_err)}"
        }

    # 3. Load model & processor
    model, processor, load_err = _get_qwen_model()
    if load_err or model is None or processor is None:
        return {
            "engine": "qwen",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": load_err or "Model not initialized"
        }

    # 4. Perform Inference
    try:
        import torch

        prompt = (
            "Read and transcribe all visible text in this document accurately line by line. "
            "Preserve Kannada, Telugu, Hindi, and English text verbatim without summarizing."
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        text_input = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = processor.image_processor(images=[image], return_tensors="pt")
        
        device = next(model.parameters()).device
        inputs = processor(
            text=[text_input],
            images=image_inputs,
            padding=True,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=1024)

        # Slice out prompt tokens
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0].strip()

        raw_lines = [line.strip() for line in output_text.split("\n") if line.strip()]
        lines_output = []
        for line in raw_lines:
            lines_output.append({
                "text": line,
                "confidence": 0.95,
                "bbox": None
            })

        overall_conf = 0.95 if lines_output else 0.0

        return {
            "engine": "qwen",
            "raw_text": output_text,
            "lines": lines_output,
            "overall_confidence": overall_conf,
            "language_detected": "multilingual_vlm",
            "error": None
        }

    except Exception as inf_err:
        return {
            "engine": "qwen",
            "raw_text": "",
            "lines": [],
            "overall_confidence": 0.0,
            "language_detected": None,
            "error": f"Qwen2.5-VL inference failed: {str(inf_err)}"
        }
