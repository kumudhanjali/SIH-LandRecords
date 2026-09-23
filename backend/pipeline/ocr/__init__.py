"""
OCR Engine Module.
Provides uniform interfaces for OCR engines (Nayana, Qwen2.5-VL).
"""

from pipeline.ocr.nayana_engine import run_ocr as run_nayana_ocr
from pipeline.ocr.qwen_engine import run_ocr as run_qwen_ocr

__all__ = ["run_nayana_ocr", "run_qwen_ocr"]
