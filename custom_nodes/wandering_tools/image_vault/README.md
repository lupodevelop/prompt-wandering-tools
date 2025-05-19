<!--
Author: Daniele Scaratti (aka lupodevelop)
Date: 2025-05-19
Version: 1.0.0
Description: Documentation for the ImageVault custom node for ComfyUI.
-->

# ImageVault - ComfyUI Output Node

**ImageVault** is a complete output node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that enables robust, reproducible image saving with complete workflow metadata. Designed for researchers, artists, and developers who require full traceability and reproducibility of their generative workflows, ImageVault ensures that every saved image is accompanied by the exact workflow state (prompt, seed, parameters, etc.) used to generate it.

## Features

- Save images with embedded workflow metadata (PNG), as thumbnails, or as paired JSON files.
- Automatic extraction of workflow data from hidden PROMPT/EXTRA_PNGINFO inputs (no server or API calls required).
- ComfyUI-style file naming: prefix + incrementing number, never overwriting existing files.
- True output node: no outputs, preview handled by ComfyUI.
- Detailed logging and robust error handling for every operation.

## Usage

1. Add ImageVault as an output node in your ComfyUI pipeline.
2. The node will automatically receive the workflow via the hidden PROMPT input (and, if available, from EXTRA_PNGINFO).
3. Select the desired save mode:
   - **image_only**: Save only the image (saved in the `output/` folder).
   - **image_with_metadata**: Save PNG image with embedded workflow metadata (saved in the `output/` folder).
   - **thumbnail_with_metadata**: Save PNG thumbnail with metadata (saved in a `output/snapshot/` subfolder) and the full image with no metadata (saved in `output/`).
   - **json_with_workflow**: Save the image with no metadata (in `output/`) and a JSON file with workflow metadata (in a `output/snapshot/` subfolder).
4. Images are always saved in the `output/` folder with incrementing file names. Thumbnails and workflow JSON files are saved in a dedicated `output/snapshot/` subfolder for each operation.

## License

MIT License

For more information, see the source code and documentation in image_vault.py.
