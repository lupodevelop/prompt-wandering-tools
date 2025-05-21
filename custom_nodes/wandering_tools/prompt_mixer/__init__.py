# __init__.py for PromptMixer node
from .prompt_mixer import PromptMixer

NODE_CLASS_MAPPINGS = {
    "PromptMixer": PromptMixer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptMixer": "Prompt Mixer",
}