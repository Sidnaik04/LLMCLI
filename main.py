import click
from config import get_key, load_config, set_key, set_last_provider
from formatter import print_json, print_pretty
from llm_client import AuthError, APIError, call_llm
from config import delete_key

PROVIDER_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini/gemini-2.5-flash",
}


# model resolver
def get_model(provider: str) -> str:
    return PROVIDER_MODELS[provider]


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


# Query handler
def handle_query(provider: str, api_key: str, output_format: str, query: str) -> None:
    model = get_model(provider)

    try:
        result = call_llm(provider=provider, model=model, query=query, api_key=api_key)

    except AuthError:
        click.echo("Authentication failed. Your API key may be invalid")
        delete_key(provider)
        new_key = resolve_api_key(provider)

        try:
            result = call_llm(
                provider=provider, model=model, query=query, api_key=new_key
            )

        except AuthError:
            click.echo("Authentication failed again. Continuing.")
            return api_key

        except APIError as exc:
            click.echo(f"API error: {exc}")
            return new_key

        api_key = new_key

    except APIError as exc:
        click.echo(f"API error: {exc}")
        return api_key

    if output_format == "json":
        print_json(result)
    else:
        print_pretty(result)

    return api_key


# REPL
def run_repl(provider: str, api_key: str, output_format: str) -> None:
    while True:
        try:
            user_input = click.prompt(
                f"llmcli ({provider}/{output_format})",
                prompt_suffix=" > ",
                default="",
                show_default=False,
            ).strip()

        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!!!")
            return

        if not user_input:
            click.echo("Query cannot be empty.")
            continue

        command = user_input.lower()

        if command in {"/exit", "/quit"}:
            click.echo("Goodbye!!!")
            return

        if command == "/provider":
            provider, api_key = resolve_provider(None)
            continue

        if command == "/format":
            output_format = resolve_format(None)
            continue

        api_key = handle_query(
            provider=provider,
            api_key=api_key,
            output_format=output_format,
            query=user_input,
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

        run_repl(
            provider=selected_provider,
            api_key=api_key,
            output_format=selected_format,
        )

    except ValueError as exc:
        click.echo(f"Configuration error: {exc}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
