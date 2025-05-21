<!--
Author: Daniele Scaratti (aka lupodevelop)
Date: 2025-05-19
Version: 1.0.0
-->

# Prompt Wandering Tools

 Is a collection of custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) designed to encourage creative exploration and inspiration through generative workflows. Instead of focusing on strict prompt optimization or deterministic results, these tools embrace randomness and variability, allowing users to "wander" through the possibilities offered by generative models.

## What is Prompt Wandering?

Prompt wandering is the philosophy of giving generative models more freedom and randomness, intentionally stepping away from rigid optimization. The goal is not to achieve a perfect, finished result on the first try, but to explore, be surprised, and let the process itself inspire new ideas. By embracing unpredictability, users can discover unexpected outcomes and creative directions that would be missed with a purely deterministic approach.

## What's in this repository?

- **Custom ComfyUI Nodes:**  
  Tools and output nodes that support prompt wandering workflows, such as:
  - **ImageVault:** An advanced output node that saves images along with complete workflow metadata, enabling reproducibility and creative tracking.
  - *(More nodes coming soon!)*

- **Examples:**  
  Example workflows and usage scenarios (see the `examples/` folder). *(coming soon!)*

## Manual Installation

1. **Clone this repository:**
   ```sh
   git clone https://github.com/lupodevelop/prompt-wandering-tools.git
   ```

2. **Copy the custom nodes:**  
   Copy the `custom_nodes/wandering_tools` folder into your ComfyUI `custom_nodes` directory.

3. **Install dependencies:**  
   Make sure you have [ComfyUI](https://github.com/comfyanonymous/ComfyUI) installed.  
   Then, install required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

4. **Restart ComfyUI:**  
   The new nodes should now be available in the ComfyUI interface.

## License

MIT License

---

For more details on each node, see the documentation in their respective folders.
