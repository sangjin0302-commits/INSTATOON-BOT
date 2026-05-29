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

## Railway Deployment

Deploy from the GitHub repository and use this start command:

```text
python -m app.main
```

Required Railway variables:

```text
TELEGRAM_TOON_BOT_TOKEN=
OPENAI_API_KEY=
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_IMAGE_MODEL=
OUTPUT_DIR=outputs
DEFAULT_PANEL_COUNT=6
ENABLE_IMAGE_GENERATION=false
MAX_DAILY_GENERATIONS=
ADMIN_USER_IDS=
```

`TELEGRAM_TOON_BOT_TOKEN` must be set for the service to start. `OPENAI_API_KEY`
is required only for live storyboard generation and is not needed for the fake
provider test path. Keep `ENABLE_IMAGE_GENERATION=false` until live image
generation is explicitly approved.

Do not commit `.env`, generated `outputs/`, PNGs, ZIPs, or cache files. The bot
does not post to Instagram, publish, approve, fan out, or mutate Auto-Sns,
Notion, or Drive.
