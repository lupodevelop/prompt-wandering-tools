# prompt_mixer.py
# Author: Daniele Scaratti (aka lupodevelop)
# Date: 2025-05-20
# Version: 1.0.0
# Description: Custom ComfyUI node for blending two prompts with adjustable parameters.

import random

class PromptMixer:
    """
    A ComfyUI node that blends two Conditioning inputs (main_clip and secondary_clip)
    by extracting their underlying text, mixing them, and re-encoding them into a single
    Conditioning output. Includes multiple blend modes, a random seed for reproducibility,
    and an 'overwrite' feature that reuses the previous mix if the inputs haven't changed.
    """

    # To support "overwrite=False" logic, we store previous inputs and output.
    # (Node instance must persist between executions.)
    _last_inputs = None
    _last_mixed_prompt = None
    _last_conditioning = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP", {}),
                "main_clip": ("CONDITIONING", {}),
                "secondary_clip": ("CONDITIONING", {}),
                "blend_percent": ("FLOAT", {"default": 50.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "mode": (["append", "interpolate", "shuffle", "replace", "random_insert"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32-1}),
                "max_length": ("INT", {"default": 300, "min": 10, "max": 1000}),
                "overwrite": ("BOOLEAN", {"default": True}),
            }
        }

    # We want to output a single Conditioning object that can be passed to other nodes (KSampler, etc.)
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("CONDITIONING",)
    OUTPUT_NODE = True  # opzionale, se vuoi che sia nodo di output
    FUNCTION = "mix"
    CATEGORY = "🎲 wandering_tools"

    @classmethod
    def IS_PREVIEW(cls):
        return True

    def _extract_prompt_text(self, conditioning):
        """
        Attempt to extract the original text from a Conditioning object.
        If not found, returns an empty string.
        """
        if not conditioning or not isinstance(conditioning, dict):
            return ""
        # In ComfyUI, CLIP-based conditioning typically stores text under "text"
        return conditioning.get("text", "")

    def mix(self, clip, main_clip, secondary_clip, blend_percent, mode, seed, max_length, overwrite):
        """
        Mixes two Conditioning objects by:
          1) Extracting their text
          2) Blending them according to mode & blend_percent
          3) Truncating & adding an ellipsis if too long
          4) Re-encoding into a single Conditioning (using the default CLIP model)
          5) If overwrite=False, and inputs haven't changed, reuse the previous result
        """

        # Extract text from incoming Conditionings
        main_prompt = self._extract_prompt_text(main_clip)
        secondary_prompt = self._extract_prompt_text(secondary_clip)

        # Prepare a tuple to detect if inputs changed
        current_inputs = (
            main_prompt, secondary_prompt, blend_percent,
            mode, seed, max_length
        )

        # If overwrite=False and inputs haven't changed, return previous result
        if (not overwrite
            and self._last_inputs is not None
            and self._last_inputs == current_inputs
            and self._last_conditioning is not None):
            return (self._last_conditioning,)

        # Store current inputs
        self._last_inputs = current_inputs

        # If both prompts are empty, short-circuit
        if not main_prompt.strip() and not secondary_prompt.strip():
            final_text = "(empty prompt)"
            # Re-encode an empty prompt so that we still return a valid Conditioning
            clip_model = load_model("CLIP")
            empty_cond = clip_model.encode(final_text)
            empty_cond["text"] = final_text
            self._last_mixed_prompt = final_text
            self._last_conditioning = empty_cond
            return (empty_cond,)

        # Deterministic randomness
        random.seed(seed)

        # Split text into tokens
        main_tokens = main_prompt.strip().split()
        secondary_tokens = secondary_prompt.strip().split()

        # Compute how many tokens from secondary to blend
        blend_count = int(len(secondary_tokens) * (blend_percent / 100.0))
        blend_count = max(0, min(blend_count, len(secondary_tokens)))

        # Perform blending based on mode
        if mode == "append":
            mixed_tokens = main_tokens + secondary_tokens[:blend_count]

        elif mode == "interpolate":
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
            mixed_tokens = main_tokens + secondary_tokens[:blend_count]
            random.shuffle(mixed_tokens)

        elif mode == "replace":
            mixed_tokens = main_tokens[:]
            replace_indices = list(range(len(mixed_tokens)))
            random.shuffle(replace_indices)
            replace_indices = replace_indices[:blend_count]
            for idx, sec_token in zip(replace_indices, secondary_tokens[:blend_count]):
                mixed_tokens[idx] = sec_token

        elif mode == "random_insert":
            mixed_tokens = main_tokens[:]
            for sec_token in secondary_tokens[:blend_count]:
                insert_pos = random.randint(0, len(mixed_tokens))
                mixed_tokens.insert(insert_pos, sec_token)

        else:
            # Fallback: no mixing, just main tokens
            mixed_tokens = main_tokens

        # Join tokens into final text
        final_text = " ".join(mixed_tokens)

        # Truncate if exceeding max_length (characters) & add ellipsis
        if len(final_text) > max_length:
            truncated = final_text[:max_length - 3].rstrip()
            final_text = truncated + "..."

        # Encode the mixed text into a new Conditioning
        final_cond = clip.encode(final_text)
        final_cond["text"] = final_text

        # Cache results for potential reuse
        self._last_mixed_prompt = final_text
        self._last_conditioning = final_cond

        # Restituisci anche la preview
        return (final_cond, {"preview": final_text})

    @classmethod
    def PREVIEW(cls, inputs, output):
        """
        Show the mixed prompt in a box in the node preview.
        'output' is a tuple with one Conditioning dict. We'll extract its text.
        """
        if isinstance(output, tuple) and len(output) > 1 and isinstance(output[1], dict):
            return output[1].get("preview", "(no preview)")
        if output and isinstance(output[0], dict):
            return output[0].get("text", "(no text)")
        return "(no preview)"
