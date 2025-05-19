"""
ImageVault - ComfyUI Output Node Package
========================================

Author: Daniele Scaratti (aka lupodevelop)

This package provides the ImageVault output node for ComfyUI, enabling robust, reproducible image saving with full workflow metadata. All images saved with ImageVault are accompanied by the complete workflow state, ensuring traceability and reproducibility for every result.

Features:
---------
- Output node for ComfyUI with no outputs (true output node behavior).
- Saves images with embedded workflow metadata, as thumbnails, or as paired JSON files.
- Robust extraction of workflow data from hidden PROMPT/EXTRA_PNGINFO inputs.
- ComfyUI-style file naming (prefix + incrementing number, never overwriting).
- Detailed logging and error handling for all operations.

See the README.md for usage instructions and further details.
"""

from .image_vault import ImageVault

NODE_CLASS_MAPPINGS = {
    "ImageVault": ImageVault,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageVault": "ImageVault (Save Image + Workflow)",
}
