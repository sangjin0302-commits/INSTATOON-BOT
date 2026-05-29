# Instagram Toon Telegram Bot

Standalone scaffold for a Telegram bot that turns a user idea into a respectful,
administrative-law themed Instagram toon package for manual upload.

The default implementation does not make live OpenAI calls, generate live images,
publish to Telegram channels, post to Instagram, mutate Auto-Sns, or write to
Notion/Drive. Tests use fake providers and local placeholder slide rendering.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
copy .env.example .env
pytest
python -m py_compile app\*.py
```

Run the bot only after adding a Telegram token:

```powershell
python -m app.main
```

Set `ENABLE_IMAGE_GENERATION=true` only when live image generation is explicitly
approved and `OPENAI_API_KEY` is configured.
