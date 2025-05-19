# image_vault.py
# Author: Daniele Scaratti (aka lupodevelop)
# Date: 2025-05-17
# Version: 1.0.0
# Description: High-quality ComfyUI output node for reproducible image saving with full workflow metadata.
"""
ImageVault - ComfyUI Output Node
===============================

Author: Daniele Scaratti (aka lupodevelop)

ImageVault is an advanced output node for ComfyUI designed to save generated images together with the complete workflow state (prompt, seed, parameters, etc.), ensuring full reproducibility and traceability of results.

Key Features:
-------------
- Save images with embedded workflow metadata (PNG), as thumbnails, or as paired JSON files.
- Robust, automatic extraction of the workflow via hidden inputs (PROMPT/EXTRA_PNGINFO), compatible with all ComfyUI pipelines.
- ComfyUI-style file naming: prefix + incrementing number, never overwriting.
- True output node behavior: no outputs, preview handled by ComfyUI.
- Detailed logging for every extraction and save step.

Usage:
------
Connect ImageVault as an output node in your ComfyUI pipeline. The node will automatically receive the workflow via the hidden PROMPT input (and, if available, from EXTRA_PNGINFO). Select the desired save mode:
- image_only: image only
- image_with_metadata: PNG image with embedded workflow metadata
- thumbnail_with_metadata: PNG thumbnail with metadata + original image
- json_with_workflow: image + JSON file with workflow

All files are saved in the output/ folder with incrementing file names.
"""
import os
import json
from PIL import Image as PILImage

class ImageVault:
    """
    ComfyUI output node for saving images and workflow metadata with high reproducibility.

    Features:
    - Saves images in multiple formats, with or without embedded workflow metadata.
    - Extracts workflow from PROMPT or EXTRA_PNGINFO (ComfyUI hidden inputs).
    - Robust file naming, fully compatible with ComfyUI conventions.
    - Detailed logging for every operation.
    """
    FUNCTION = "save"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    CATEGORY = "🎲 wandering_tools"

    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the node inputs, including hidden inputs for workflow metadata.
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "mode": ([
                    "image_only",
                    "image_with_metadata",
                    "thumbnail_with_metadata",
                    "json_with_workflow"
                ],),
                "prefix": ("STRING", {"default": ""}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    @classmethod
    def IS_PREVIEW(cls):
        """
        Indicates that the node supports preview in ComfyUI.
        """
        return True

    def save(self, image, mode, prefix, prompt=None, extra_pnginfo=None):
        """
        Saves the image and workflow metadata according to the selected mode.
        - image_only: saves only the image in output/
        - image_with_metadata: saves PNG with embedded workflow metadata in output/
        - thumbnail_with_metadata: saves PNG thumbnail with metadata in output/snapshot/, full image in output/
        - json_with_workflow: saves image in output/, JSON file with workflow in output/snapshot/
        """
        print(f"[ImageVault] Save called with mode='{mode}', prefix='{prefix}'")
        # Save directory
        save_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(save_dir, exist_ok=True)
        print(f"[ImageVault] Output directory: {save_dir}")
        # Find the next available index for file naming (like ComfyUI SaveImage)
        def get_next_index(folder, prefix, ext):
            import re
            max_idx = 0
            for fname in os.listdir(folder):
                if fname.startswith(prefix) and fname.endswith(ext):
                    m = re.search(rf"{re.escape(prefix)}(\\d+)\\{ext}$", fname)
                    if m:
                        idx = int(m.group(1))
                        if idx > max_idx:
                            max_idx = idx
            # Ensure no file is overwritten
            while True:
                candidate = f"{prefix}{max_idx+1:05d}{ext}"
                if not os.path.exists(os.path.join(folder, candidate)):
                    break
                max_idx += 1
            return max_idx + 1
        ext = ".png"
        idx = get_next_index(save_dir, prefix, ext)
        base_name = f"{prefix}{idx:05d}"
        image_path = os.path.join(save_dir, base_name + ext)
        print(f"[ImageVault] Image will be saved as: {image_path}")
        # Save the image
        try:
            pil_img = self._to_pil(image)
            print(f"[ImageVault] Image converted to PIL.Image. Size: {pil_img.size}")
        except Exception as e:
            print(f"[ImageVault] ERROR converting image to PIL.Image: {e}")
            raise
        metadata = self._get_workflow_metadata(prompt, extra_pnginfo)
        print(f"[ImageVault] Workflow metadata extracted: {json.dumps(metadata)[:200]}{'...' if len(json.dumps(metadata))>200 else ''}")
        try:
            if mode == "image_only":
                pil_img.save(image_path)
                print(f"[ImageVault] Image saved (image_only mode)")
            elif mode == "image_with_metadata":
                pil_img.save(image_path, pnginfo=self._make_pnginfo(metadata))
                print(f"[ImageVault] Image saved with metadata (image_with_metadata mode)")
            elif mode == "thumbnail_with_metadata":
                # Save thumbnail with metadata in snapshot subfolder
                snapshot_dir = os.path.join(save_dir, f"{prefix}snapshot_{self._get_unique_id()}")
                os.makedirs(snapshot_dir, exist_ok=True)
                thumb = pil_img.copy()
                thumb.thumbnail((256, 256))
                thumb_path = os.path.join(snapshot_dir, base_name + "_thumb" + ext)
                thumb.save(thumb_path, pnginfo=self._make_pnginfo(metadata))
                print(f"[ImageVault] Thumbnail saved with metadata: {thumb_path}")
                # Always save the original image in output/
                pil_img.save(image_path)
                print(f"[ImageVault] Full image saved in output/ (thumbnail_with_metadata mode)")
            elif mode == "json_with_workflow":
                # Save JSON with workflow metadata in snapshot subfolder, with _workflow suffix
                snapshot_dir = os.path.join(save_dir, f"{prefix}snapshot_{self._get_unique_id()}")
                os.makedirs(snapshot_dir, exist_ok=True)
                json_path = os.path.join(snapshot_dir, base_name + "_workflow.json")
                with open(json_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                print(f"[ImageVault] Workflow metadata saved as JSON: {json_path}")
                # Always save the original image in output/
                pil_img.save(image_path)
                print(f"[ImageVault] Full image saved in output/ (json_with_workflow mode)")
        except Exception as e:
            print(f"[ImageVault] ERROR during file save: {e}")
            raise
        print(f"[ImageVault] Save operation completed for: {image_path}")
        # No return, as this is an output node
        return ()

    def _to_pil(self, image):
        """
        Converts the image to PIL.Image format, handling batches and channels.
        """
        print(f"[ImageVault] _to_pil called. Type: {type(image)}")
        import numpy as np
        if hasattr(image, 'cpu'):
            arr = image.cpu().numpy()
        else:
            arr = np.array(image)
        print(f"[ImageVault] Numpy array shape: {arr.shape}, dtype: {arr.dtype}")
        # Remove batch dimensions if present
        while arr.ndim > 3:
            arr = arr[0]
        # Transpose if channels are in the wrong order
        if arr.shape[-1] != 3 and arr.shape[0] == 3:
            arr = arr.transpose(1, 2, 0)
        # Ensure values are in [0,1]
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 1)
            arr = (arr * 255).astype('uint8')
        print(f"[ImageVault] Final array shape for PIL: {arr.shape}, dtype: {arr.dtype}")
        return PILImage.fromarray(arr)

    def _get_unique_id(self):
        """
        Generates a unique ID based on the current timestamp.
        """
        import time
        uid = str(int(time.time() * 1000))
        print(f"[ImageVault] Generated unique id: {uid}")
        return uid

    def _get_workflow_metadata(self, prompt=None, extra_pnginfo=None):
        """
        Extracts the workflow from the metadata provided by ComfyUI (PROMPT or EXTRA_PNGINFO).
        """
        print("[ImageVault] Attempting to extract workflow metadata from PROMPT or EXTRA_PNGINFO ...")
        if extra_pnginfo is not None and isinstance(extra_pnginfo, dict) and 'workflow' in extra_pnginfo:
            print("[ImageVault] Extracted workflow from extra_pnginfo.")
            return extra_pnginfo['workflow']
        if prompt is not None and isinstance(prompt, dict) and "version" in prompt:
            print("[ImageVault] Extracted workflow from PROMPT input.")
            return prompt
        print("[ImageVault] Warning: No workflow provided via PROMPT or EXTRA_PNGINFO input.")
        return {}

    def _make_pnginfo(self, metadata):
        """
        Creates a PNGInfo object with the workflow metadata, if valid.
        """
        from PIL.PngImagePlugin import PngInfo
        pnginfo = PngInfo()
        # Add metadata only if it is a valid workflow dictionary (must have 'version' key)
        if isinstance(metadata, dict) and "version" in metadata:
            try:
                pnginfo.add_text("workflow", json.dumps(metadata))
                print("[ImageVault] Metadata injected into PNG.")
            except Exception as e:
                print(f"[ImageVault] ERROR injecting metadata into PNG: {e}")
        else:
            print(f"[ImageVault] Warning: Provided workflow metadata is not valid or missing 'version' key. Metadata will not be injected. Metadata: {json.dumps(metadata, indent=2)}")
        return pnginfo
