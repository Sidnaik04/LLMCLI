import click
from config import get_key, load_config, set_key, set_last_provider


# provider selection helper
def prompt_provider() -> str:
    config = load_config()
    keys = config.get("keys", {})
    last_provider = config.get("last_provider")

    available_providers = [
        provider for provider in ("openai", "gemini") if keys.get(provider)
    ]

    if len(available_providers) == 1:
        return available_providers[0]

    if len(available_providers) == 2:
        default = last_provider if last_provider in available_providers else "openai"

        value = click.prompt(
            "which provider?",
            type=click.Choice(["openai", "gemini"]),
            default=default,
            show_default=True,
        )

        return value

    raise RuntimeError("No API keys configured.")


# Key Resolution
def resolve_api_key(provider: str) -> str:
    key = get_key(provider)

    if key:
        return key

    key = click.prompt(f"Enter {provider} API key", hide_input=True).strip()

    while not key:
        click.echo("API key cannot be empty.")
        key = click.prompt(f"Enter {provider} API key", hide_input=True).strip()

    set_key(provider, key)

    return key


# Startup resolution
def resolve_provider(provider_option: str | None) -> tuple[str, str]:
    config = load_config()

    if not config.get("keys"):
        setup_config()

    if provider_option:
        provider = provider_option
    else:
        provider = prompt_provider()

    api_key = resolve_api_key(provider)

    set_last_provider(provider)

    return provider, api_key


def setup_config() -> None:
    click.echo("No API keys configured. Let's set one up.")

    while True:
        openai_key = click.prompt(
            "OpenAI API key (leave blank to skip)",
            default="",
            hide_input=True,
            show_default=False,
        ).strip()

        gemini_key = click.prompt(
            "Gemini API key (leave blank to skip)",
            default="",
            hide_input=True,
            show_default=False,
        ).strip()

        if not openai_key and not gemini_key:
            click.echo("At least one API key is required.")
            continue

        if openai_key:
            set_key("openai", openai_key)

        if gemini_key:
            set_key("gemini", gemini_key)

        return


def resolve_format(output_format: str | None) -> str:
    if output_format:
        return output_format

    return click.prompt(
        "output format?", type=click.Choice(["json", "pretty"]), default="pretty"
    )


# startup


@click.command()
@click.option("--provider", type=click.Choice(["openai", "gemini"]), default=None)
@click.option(
    "--format", "output_format", type=click.Choice(["json", "pretty"]), default=None
)
def main(provider: str | None, output_format: str | None) -> None:
    try:
        selected_provider, api_key = resolve_provider(provider)
        selected_format = resolve_format(output_format)

        click.echo(f"Starting llmcli with {selected_provider}/{selected_format}")

    except ValueError as exc:
        click.echo(f"Configuration error: {exc}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
