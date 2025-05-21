# PromptMixer - ComfyUI Node

**PromptMixer** is a custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that allows you to blend two text prompts with adjustable parameters. This node is designed for creative exploration, letting you experiment with prompt fusion, randomness, and different mixing strategies.

## Features

- Takes two prompts as input: a main prompt and a secondary prompt.
- Adjustable blend percentage to control how much of the secondary prompt is mixed in.
- Multiple blend modes: append, interpolate, shuffle.
- Seed parameter for reproducible randomization.
- Maximum length control for the resulting prompt.
- Overwrite option to control if the prompt should be remixed when inputs change.
- Preview of the mixed prompt directly in the node.

## Usage

1. Add the PromptMixer node to your ComfyUI workflow.
2. Connect or enter your main and secondary prompts.
3. Adjust the blend percentage, mode, seed, and max length as desired.
4. The mixed prompt will be shown as a preview and can be used as input for CLIP or other nodes.

## Parameters

- **main_prompt**: The primary text prompt.
- **secondary_prompt**: The secondary text prompt to blend in.
- **blend_percent**: Percentage of the secondary prompt to include (0-100).
- **mode**: How to blend the prompts (append, interpolate, shuffle).
- **seed**: Random seed for reproducibility.
- **max_length**: Maximum length of the resulting prompt (in characters).
- **overwrite**: If true, always remix when inputs change.

---

For more details, see the code in `prompt_mixer.py`.