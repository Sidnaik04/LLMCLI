# llmcli

> A lightweight interactive CLI for querying multiple LLM providers through a single interface powered by LiteLLM.

`llmcli` is a terminal-based REPL that lets you interact with OpenAI and Gemini without writing provider-specific code.

Choose a provider once, enter queries continuously, switch providers or output formats during a session, and get responses as either clean terminal output or JSON.

## Why llmcli?

When working with multiple LLM providers, every provider tends to have its own SDK, authentication flow, request format, and response structure.

`llmcli` puts LiteLLM behind a small application layer so the CLI can work with multiple providers through one interface.

```text
                     llmcli
                        │
                        ▼
                  LiteLLM Client
                   /          \
                  /            \
             OpenAI            Gemini
```

The application itself remains provider-agnostic.

## Features

- OpenAI and Gemini support
- LiteLLM-based provider routing
- Interactive terminal REPL
- Multiple queries in a single session
- Switch providers with `/provider`
- Switch output formats with `/format`
- JSON output for programmatic use
- Rich terminal output for interactive use
- Persistent local API-key configuration
- Automatic API-key recovery after authentication failures
- Graceful handling of API/network errors
- Clean `/exit`, `/quit`, and `Ctrl+C` termination

## Quick Start

### Requirements

- Python 3.10+
- `uv`
- An OpenAI and/or Gemini API key

### Install

Clone the repository:

```bash
git clone https://github.com/Sidnaik04/llmcli.git
cd llmcli
```

Install dependencies:

```bash
uv sync
```

Start the CLI:

```bash
uv run main.py
```

On first launch, `llmcli` will ask for your API key.

## Usage

### Start normally

```bash
uv run main.py
```

The CLI resolves the configured provider and asks for the desired output format.

Example:

```text
Which provider? [openai]: openai
Output format? [pretty]: pretty

llmcli (openai/pretty) > What is tokenization?
```

### Select a provider

```bash
uv run main.py --provider openai
```

or:

```bash
uv run main.py --provider gemini
```

### Select an output format

Pretty terminal output:

```bash
uv run main.py --format pretty
```

JSON:

```bash
uv run main.py --format json
```

Both options can be combined:

```bash
uv run main.py --provider gemini --format json
```

## Interactive Commands

| Command     | Description          |
| ----------- | -------------------- |
| `/provider` | Switch LLM provider  |
| `/format`   | Switch output format |
| `/exit`     | Exit the application |
| `/quit`     | Exit the application |
| `Ctrl+C`    | Exit the application |

Any other non-empty input is treated as an LLM query.

## Output Formats

### Pretty

```text
╭── gemini / gemini/gemini-2.5-flash ──╮
│                                      │
│ An embedding is a numerical vector  │
│ representation of semantic meaning. │
│                                      │
╰──────────────────────────────────────╯
```

### JSON

```json
{
  "provider": "gemini",
  "model": "gemini/gemini-2.5-flash",
  "query": "What is an embedding?",
  "response": "An embedding is a numerical vector representation of semantic meaning.",
  "tokens_used": 32
}
```

JSON output makes the CLI easier to integrate into scripts and other tools.

## Configuration

`llmcli` stores local configuration in:

```text
.llmcli_config.json
```

Example:

```json
{
  "last_provider": "openai",
  "keys": {
    "openai": "sk-...",
    "gemini": "..."
  }
}
```

The configuration file is automatically excluded from Git.

### Security Notice

API keys are currently stored as plaintext in `.llmcli_config.json`.

This is intentional for the scope of this learning project, but it is **not suitable for production use**.

Do not commit your configuration file or expose your API keys.

## Architecture

```text
┌───────────────────────────────────────┐
│               main.py                 │
│        CLI + startup + REPL           │
└───────────────────┬───────────────────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
      config.py  llm_client  formatter.py
          │         │         │
          │         ▼         │
          │      LiteLLM      │
          │       /   \       │
          │      /     \      │
          │ OpenAI   Gemini   │
          │                   │
          └───────────────────┘
```

## Project Structure

```text
llmcli/
├── main.py
├── config.py
├── llm_client.py
├── formatter.py
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
└── .gitignore
```

## Development

Install dependencies:

```bash
uv sync
```

Run the application:

```bash
uv run main.py
```

Run a syntax check:

```bash
uv run python -m py_compile \
    main.py \
    config.py \
    llm_client.py \
    formatter.py
```

These are deliberate non-goals rather than missing features.

## Tech Stack

| Component     | Technology |
| ------------- | ---------- |
| Language      | Python     |
| Environment   | uv         |
| CLI           | Click      |
| LLM Routing   | LiteLLM    |
| Terminal UI   | Rich       |
| Configuration | JSON       |

## License

This project is licensed under the [MIT License](https://github.com/Sidnaik04/LLMCLI/blob/main/LICENSE).

## Disclaimer

`llmcli` is a learning project. You are responsible for managing your API keys, API usage, and associated provider costs.
