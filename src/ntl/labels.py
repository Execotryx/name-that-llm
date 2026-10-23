"""Authoritative class order and provider mapping; never inferred from text."""
PROVIDERS = {
    "Anthropic": ["claude-fable-5", "claude-opus-4-6", "claude-opus-4-8", "claude-opus-5", "claude-sonnet-5"],
    "Google": ["gemini-3.1-pro-preview", "gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash"],
    "ZAI": ["glm-5.3", "glm-5.3-flash"],
    "OpenAI": ["gpt-5.5", "gpt-5.6-luna", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-6-astra"],
    "Moonshot AI": ["kimi-k3"], "Qwen": ["qwen3.8-max"],
}
CLASSES = sorted(label for labels in PROVIDERS.values() for label in labels)
PROVIDER = {label: provider for provider, labels in PROVIDERS.items() for label in labels}
