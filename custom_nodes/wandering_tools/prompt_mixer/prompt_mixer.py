# prompt_mixer.py
# Author: Daniele Scaratti (aka lupodevelop)
# Date: 2025-05-20
# Version: 1.0.0
# Description: Custom ComfyUI node for blending two prompts with adjustable parameters.

import random

class PromptMixer:
    """
    ComfyUI node for blending two prompts with adjustable parameters.
    Allows creative prompt mixing for generative exploration.
    """

    # To support "overwrite=False" logic, we store previous inputs and output.
    # Note: This relies on the node instance being persistent between executions.
    _last_inputs = None
    _last_mixed_prompt = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "main_prompt": ("STRING", {"multiline": True, "default": ""}),
                "secondary_prompt": ("STRING", {"multiline": True, "default": ""}),
                "blend_percent": ("FLOAT", {"default": 50.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "mode": (["append", "interpolate", "shuffle", "replace", "random_insert"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32-1}),
                "max_length": ("INT", {"default": 300, "min": 10, "max": 1000}),
                "overwrite": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("mixed_prompt",)
    FUNCTION = "mix"
    CATEGORY = "🎲 wandering_tools"

    @classmethod
    def IS_PREVIEW(cls):
        return True

    def mix(self, main_prompt, secondary_prompt, blend_percent, mode, seed, max_length, overwrite):
        """
        Mixes the two prompts according to the selected mode and blend percent.
        If overwrite=False, it reuses a previously mixed prompt if the inputs haven't changed.
        Adds new modes ('replace', 'random_insert'),
        and truncates the final prompt with an ellipsis if it exceeds max_length.
        """

        # Check if we should skip recalculation
        current_inputs = (
            main_prompt, secondary_prompt, blend_percent,
            mode, seed, max_length
        )

        if (not overwrite
            and self._last_inputs is not None
            and self._last_inputs == current_inputs
            and self._last_mixed_prompt is not None):
            # Reuse previous result
            return (self._last_mixed_prompt,)

        # Store inputs
        self._last_inputs = current_inputs

        # If both prompts are empty, return empty
        if not main_prompt.strip() and not secondary_prompt.strip():
            mixed_prompt = "(empty prompt)"
            self._last_mixed_prompt = mixed_prompt
            return (mixed_prompt,)

        # Deterministic randomness
        random.seed(seed)

        # Tokenize prompts
        main_tokens = main_prompt.strip().split()
        secondary_tokens = secondary_prompt.strip().split()

        # Calculate number of tokens to blend
        blend_count = int(len(secondary_tokens) * (blend_percent / 100.0))

        # Handle negative or out-of-range blend_count
        if blend_count < 0:
            blend_count = 0
        elif blend_count > len(secondary_tokens):
            blend_count = len(secondary_tokens)

        if mode == "append":
            # Append blend_count tokens from secondary to main
            mixed_tokens = main_tokens + secondary_tokens[:blend_count]

        elif mode == "interpolate":
            # Interleave tokens from both prompts
            mixed_tokens = []
            i, j = 0, 0
            while i < len(main_tokens) or j < blend_count:
                if i < len(main_tokens):
                    mixed_tokens.append(main_tokens[i])
                    i += 1
                if j < blend_count:
                    mixed_tokens.append(secondary_tokens[j])
                    j += 1

        elif mode == "shuffle":
            # Mix blend_count tokens from secondary into main, then shuffle
            mixed_tokens = main_tokens + secondary_tokens[:blend_count]
            random.shuffle(mixed_tokens)

        elif mode == "replace":
            # Replace up to blend_count tokens of main with tokens from secondary
            mixed_tokens = main_tokens[:]
            replace_indices = list(range(len(mixed_tokens)))
            random.shuffle(replace_indices)
            replace_indices = replace_indices[:blend_count]
            for idx, sec_token in zip(replace_indices, secondary_tokens[:blend_count]):
                mixed_tokens[idx] = sec_token

        elif mode == "random_insert":
            # Randomly insert up to blend_count tokens from secondary into main
            mixed_tokens = main_tokens[:]
            for sec_token in secondary_tokens[:blend_count]:
                insert_pos = random.randint(0, len(mixed_tokens))
                mixed_tokens.insert(insert_pos, sec_token)

        else:
            # Fallback: just main prompt
            mixed_tokens = main_tokens

        # Join tokens
        mixed_prompt = " ".join(mixed_tokens)

        # Truncate to max_length (by characters), adding ellipsis if needed
        if len(mixed_prompt) > max_length:
            truncated = mixed_prompt[:max_length - 3].rstrip()
            mixed_prompt = truncated + "..."

        # Save result to reuse if overwrite=False
        self._last_mixed_prompt = mixed_prompt
        return (mixed_prompt,)

    @classmethod
    def PREVIEW(cls, inputs, output):
        # Show the mixed prompt in a box in the node
        return output[0] if output and output[0] else "(no preview)"
