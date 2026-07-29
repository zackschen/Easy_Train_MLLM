"""Helpers for loading LLaVA non-LoRA weights across base and PEFT models."""


def _key_variants(key):
    variants = []

    def add(value):
        if value and value not in variants:
            variants.append(value)

    add(key)
    index = 0
    while index < len(variants):
        current = variants[index]
        index += 1
        for prefix in ("base_model.", "model."):
            if current.startswith(prefix):
                add(current[len(prefix):])

    stripped_variants = tuple(variants)
    for current in stripped_variants:
        for prefix in (
            "model.",
            "model.model.",
            "base_model.",
            "base_model.model.",
            "base_model.model.model.",
        ):
            add(prefix + current)
    return variants


def align_state_dict_keys_to_model(state_dict, model):
    """Map checkpoint keys to the exact names expected by ``model``."""
    expected_keys = set(model.state_dict().keys())
    aligned = {}
    unmatched = []

    for source_key, value in state_dict.items():
        target_key = next(
            (candidate for candidate in _key_variants(source_key) if candidate in expected_keys),
            None,
        )
        if target_key is None:
            unmatched.append(source_key)
            continue
        if target_key in aligned:
            raise ValueError(f"Multiple checkpoint keys map to {target_key}")
        aligned[target_key] = value

    return aligned, unmatched
