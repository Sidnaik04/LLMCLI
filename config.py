import json
from pathlib import Path

CONFIG_FILE = Path(".llmcli_config.json")


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {"last_provider": None, "keys": {}}

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Configuration file is corrupted or contains invalid JSON."
        ) from exc

    if not isinstance(config, dict):
        raise ValueError("Configuration file must contain a JOSN object.")

    return config


def save_config(config: dict) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)


def get_key(provider: str) -> str | None:
    config = load_config()
    return config.get("keys", {}).get(provider)


def set_key(provider: str, key: str) -> None:
    config = load_config()

    if "keys" not in config:
        config["keys"] = {}

    config["keys"][provider] = key
    save_config(config)


def delete_key(provider: str) -> None:
    config = load_config()
    config.get("keys", {}).pop(provider, None)
    save_config(config)


def set_last_provider(provider: str) -> None:
    config = load_config()
    config["last_provider"] = provider
    save_config(config)
